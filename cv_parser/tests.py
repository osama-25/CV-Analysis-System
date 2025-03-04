from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.sessions.models import Session
from .models import CVDocument
import json

class UploadCVTestCase(TestCase):
    def test_upload_cv_valid_pdf(self):
        with open('uploads/File_1.pdf', 'rb') as f:
            pdf_file = SimpleUploadedFile('File_1.pdf', f.read(), content_type='application/pdf')

            response = self.client.post(reverse('upload_cv'), {'file': pdf_file})

        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.json())
        self.assertIn('data', response.json())

    def test_upload_cv_invalid_file_format(self):
        with open('uploads/cv.txt', 'rb') as f:
            txt_file = SimpleUploadedFile('cv.txt', f.read(), content_type='text/plain')

            response = self.client.post(reverse('upload_cv'), {'file': txt_file})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("error"), "Unsupported file format")

    def test_upload_cv_no_file(self):
        response = self.client.post(reverse('upload_cv'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("error"), "No file uploaded")


class QueryCVTestCase(TestCase):
    def test_query_find_skill(self):
        CVDocument.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="123456789",
            education='["Bachelor\'s in Computer Science"]',
            work_experience='["Software Engineer at ABC Corp"]',
            skills='["Python", "Django"]',
            projects='["Project1", "Project2"]',
            certifications='["Certification1"]'
        )

        query = {
            "query": "Find candidates with Python skills"
        }
        
        response = self.client.post(reverse('query_cv'), json.dumps(query), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())
        self.assertEqual(response.json().get("response"), ["John Doe"])

    def test_query_compare_education(self):
        CVDocument.objects.create(
            name="Alice",
            email="alice@example.com",
            phone="987654321",
            education='["Bachelor\'s in Engineering"]',
            work_experience='["Engineer at XYZ Corp"]',
            skills='["Java", "Spring Boot"]',
            projects='["Project1"]',
            certifications='["Certification A"]'
        )
        CVDocument.objects.create(
            name="Bob",
            email="bob@example.com",
            phone="123456789",
            education='["Master\'s in Computer Science"]',
            work_experience='["Developer at ABC Corp"]',
            skills='["Python", "Django"]',
            projects='["Project2"]',
            certifications='["Certification B"]'
        )

        query = {
            "query": "Compare education levels of Alice and Bob"
        }

        response = self.client.post(reverse('query_cv'), json.dumps(query), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())
        self.assertEqual(len(response.json()["response"]), 2)

    def test_query_experience_industry(self):
        CVDocument.objects.create(
            name="Charlie",
            email="charlie@example.com",
            phone="1122334455",
            education='["Bachelor\'s in Business Administration"]',
            work_experience='["HR Manager at ABC Corp"]',
            skills='["Management", "Team Leadership"]',
            projects='["Project3"]',
            certifications='["HR Certification"]'
        )

        query = {
            "query": "Who has experience in HR?"
        }

        response = self.client.post(reverse('query_cv'), json.dumps(query), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())
        self.assertEqual(response.json().get("response"), ["Charlie"])

    def test_query_job_match(self):
        CVDocument.objects.create(
            name="David",
            email="david@example.com",
            phone="2233445566",
            education='["Master\'s in Data Science"]',
            work_experience='["Data Scientist at XYZ Corp"]',
            skills='["Python", "Machine Learning"]',
            projects='["Data Analysis"]',
            certifications='["Data Science Certification"]'
        )

        query = {
            "query": "find a candidate matching a Data Scientist role?"
        }

        response = self.client.post(reverse('query_cv'), json.dumps(query), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())
        self.assertEqual(response.json().get("response"), ["David"])

    def test_query_unclassified(self):
        query = {
            "query": "What is the weather like today?"
        }

        response = self.client.post(reverse('query_cv'), json.dumps(query), content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("response"), "Unclassified query")
