import os
import time
import json
from dotenv import load_dotenv
from groq import Groq, APIError, RateLimitError

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

def parse_cv_data(cv_text, max_retries=3, initial_delay=2):
    prompt = f"""
    Extract structured information from the following CV:
    ---
    {cv_text}
    ---
    Return ONLY valid JSON with the following structure:
    {{
        "Name": "Full Name",
        "Email": "email@example.com",
        "Phone": "1234567890",
        "Education": ["Degree at University"],
        "Work Experience": ["Job Title at Company"],
        "Skills": ["Skill1", "Skill2"],
        "Projects": ["Project1", "Project2"],
        "Certifications": ["Certification1", "Certification2"]
    }}

    Do NOT include any explanations, markdown formatting (such as ```json), or extra text—ONLY return raw JSON.
    """

    retries = 0
    delay = initial_delay

    while retries < max_retries:
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert CV parser. Extract structured data from CVs and return only valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = completion.choices[0].message.content.strip()

            # Ensure valid JSON response
            return {"response": json.loads(response_text)}

        except RateLimitError:
            time.sleep(delay)  # Wait before retrying
            retries += 1
            delay *= 2  # Exponential backoff
        except (APIError, json.JSONDecodeError) as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    return {"error": "Max retries reached. Unable to process the request."}
