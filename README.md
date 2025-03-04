CV Analysis System
This is a CV Analysis System built with Django, Python, and other related technologies. The project allows users to upload CVs (in PDF format), extract structured information such as personal details, skills, education, work experience, and more, and analyze the extracted data.

Features
CV Upload: Users can upload CV files (PDF format).
Data Extraction: The system extracts structured information from the uploaded CVs, such as:
Name, email, phone number
Education background
Work experience
Skills
Certifications (if any)
Query System: Allows querying specific information like education, work experience, and skills from the parsed CV data.
Error Handling: Handles various errors related to invalid file formats and other edge cases.
Installation
Requirements
Python 3.7+
Django 3.x
Dependencies listed in requirements.txt
Setup

Clone the repository:
git clone https://github.com/osama-25/CV-Analysis-System.git
cd CV-Analysis-System

Set up a virtual environment:
python -m venv venv
source venv/bin/activate  # For Linux/macOS
venv\Scripts\activate  # For Windows

Install the required dependencies:
pip install -r requirements.txt

Apply migrations to set up the database:
python manage.py migrate

Run the development server:
python manage.py runserver

Visit http://127.0.0.1:8000/ in your browser to access the application.

Usage
Uploading a CV: You can upload a CV through the "Upload CV" endpoint, and the system will extract the relevant information from the document.
Querying Data: Use the query system to find specific details from the CVs, such as skills, work experience, and education. You can perform queries such as:
Compare education levels of candidates
Find candidates with specific skills
Match candidates to specific job roles like "Data Scientist"
Testing
You can run the test suite to ensure everything is working properly:

python manage.py test
The tests cover:

Uploading valid and invalid CVs
Querying data from uploaded CVs
Error handling and edge cases
