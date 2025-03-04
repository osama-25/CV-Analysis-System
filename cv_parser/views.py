from django.http import JsonResponse
from django.core.files.storage import default_storage
from .utils import extract_text_from_pdf, extract_text_from_docx
from .llm import parse_cv_data
from .models import CVDocument
import json
from groq import Groq
import os
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.sessions.models import Session
import re

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
client = Groq(
    api_key=GROQ_API_KEY,
)

@csrf_exempt
def upload_cv(request):
    """ Handles file uploads (PDF or DOCX) and extracts text. """
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        file_path = default_storage.save(f"uploads/{uploaded_file.name}", uploaded_file)

        # Process file based on type
        if uploaded_file.name.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif uploaded_file.name.endswith(".docx"):
            text = extract_text_from_docx(uploaded_file)
        else:
            return JsonResponse({"error": "Unsupported file format"}, status=400)

        print('extracted text ', text)
        # Parse extracted text
        structured_data = parse_cv_data(text)
        
        if isinstance(structured_data, str):
            structured_data = json.loads(structured_data.strip("`"))

        CVDocument.objects.create(
            file=uploaded_file,
            name=structured_data.get("Name"),
            email=structured_data.get("Email"),
            phone=structured_data.get("Phone"),
            education=json.dumps(structured_data.get("Education", [])),
            work_experience=json.dumps(structured_data.get("Work Experience", [])),
            skills=json.dumps(structured_data.get("Skills", [])),
            projects=json.dumps(structured_data.get("Projects", [])),
            certifications=json.dumps(structured_data.get("Certifications", []))
        )

        return JsonResponse({"message": "File processed", "data": structured_data}, status=201)

    return JsonResponse({"error": "No file uploaded"}, status=400)

@csrf_exempt
def query_cv(request):
    if request.method == "GET":
        return render(request, "query_cv.html") 

    if request.method == "POST":
        body = json.loads(request.body)
        user_query = body.get("query")
        
        print('user_query ', user_query)

        # Retrieve stored context or initialize if not available
        context = request.session.get('context', '')

        prompt = f"""
        You are an intelligent query classifier specialized in parsing HR-related queries about candidate CVs. Your task is to classify the provided query into one of the following types and extract any relevant entities. Please output your response strictly in valid JSON format with no special characters as described below.

        Query Types:
        1. "find_skill": For queries that ask for candidates with a specific skill.
        - Relevant entity: "skill"
        - Example: "Find candidates with Python skills" should yield:
            {{"type": "find_skill", "skill": "Python"}}
        2. "compare_education": For queries that compare education levels of two candidates.
        - Relevant entities: "candidate1" and "candidate2"
        - Example: "Compare education levels of Alice and Bob" should yield:
            {{"type": "compare_education", "candidate1": "Alice", "candidate2": "Bob"}}
        3. "experience_industry": For queries that ask for candidates with experience in a specific industry.
        - Relevant entity: "industry"
        - Example: "Who has experience in software development?" should yield:
            {{"type": "experience_industry", "industry": "software development"}}
        4. "job_match": For queries that seek candidates for a specific job requirement.
        - Relevant entity: "job_title"
        - Example: "Who is a good match for a Data Scientist role?" should yield:
            {{"type": "job_match", "job_title": "Data Scientist"}}

        If the query does not clearly match any of these types, output:
        {{"type": "-1"}}

        Now, classify the following query:

        {user_query}
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"Recall this context: {context} while answering."},
                {"role": "user", "content": prompt},
            ]
        )
        structured_query = response.choices[0].message.content.strip().lower()

        # Update session context
        updated_context = context + "\n" + structured_query  # Append the new response to the existing context
        request.session['context'] = updated_context

        print('structured_query ', structured_query)
        
        structured_query = json.loads(structured_query)
        query_type = structured_query.get("type", -1)
        print('query_type ', query_type)

        if query_type == "find_skill":
            skill_name = structured_query.get("skill", "").strip()
            if not skill_name:
                return JsonResponse({"response": "Missing skill name"}, status=400)
            candidates = CVDocument.objects.filter(skills__icontains=skill_name).values_list('name', flat=True)
            return JsonResponse({"response": list(candidates)})

        elif query_type == "compare_education":
            candidate1 = structured_query.get("candidate1", "").strip()
            candidate2 = structured_query.get("candidate2", "").strip()
            if not candidate1 or not candidate2:
                return JsonResponse({"response": "Missing candidate names"}, status=400)
            education_data = []
            candidate1_data = CVDocument.objects.filter(name__icontains=candidate1).values_list('name', 'education')
            if candidate1_data.exists():
                education_data.extend(list(candidate1_data))
            candidate2_data = CVDocument.objects.filter(name__icontains=candidate2).values_list('name', 'education')
            if candidate2_data.exists():
                education_data.extend(list(candidate2_data))
            return JsonResponse({"response": education_data})

        elif query_type == "experience_industry":
            industry = structured_query.get("industry", "").strip()
            if not industry:
                return JsonResponse({"response": "Missing industry"}, status=400)
            candidates = CVDocument.objects.filter(work_experience__icontains=industry).values_list('name', flat=True)
            return JsonResponse({"response": list(candidates)})

        elif query_type == "job_match":
            job_title = structured_query.get("job_title", "").strip()
            if not job_title:
                return JsonResponse({"response": "Missing job title"}, status=400)
            matching_candidates = CVDocument.objects.filter(work_experience__icontains=job_title).values_list('name', flat=True)
            return JsonResponse({"response": list(matching_candidates)})

        else:
            return JsonResponse({"response": "Unclassified query"}, status=400)
