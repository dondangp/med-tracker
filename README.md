# Medication Adherence Web Application

## 1. Introduction

### 1.1 Background
When it comes to medication, adherence is a crucial factor in achieving successful treatment outcomes, especially in the treatment of chronic conditions. The consequences of poor medication adherence include a decline in the patient’s health, readmission to hospitals, and higher expenditures in healthcare costs. Some of the causes of this may include forgetfulness, lack of understanding of treatment, side effects, or complex medication schedules. More robust tools are needed, including reminders, progress tracking, adverse reaction monitoring, and predictive analytics, to better support patient adherence in a healthcare setting. The goal of this team project is to develop a web application that incorporates these functionalities that enable real-time tracking of patients’ progress, detection of adherence gaps, and modification of any required actions.

### 1.2 Justification
Medication adherence is very important when it comes to treatment and also for optimizing healthcare resources. The treatment of chronic illness usually includes the use of long-term medication and their full benefits are not realized because approximately 50 percent of patients do not take their medications as prescribed [1](https://pubmed.ncbi.nlm.nih.gov/21389250/). This goes to show that there is a need for a more effective tracking solution that not only focuses on reminders but also able to analyze patient data, track side effects, and provide predictive insights to medication adherence. This team project aims to create a comprehensive tracker that will integrate medication schedules, adverse reaction tracking, progress monitoring, and predictive analysis.

### 1.3 Solution
The proposed solution will be a web-based application that will allow patients and healthcare providers to monitor medication adherence, track medication schedules, send reminder emails, and also offer predictive data analysis. The front-end of the application will gather patient input on their adherence and record any issues they face like side effects. The app’s predictive analysis feature will assess adherence trends and predict any potential risks to enable early interventions.

## 2. Technical Design

### 2.1 Tools and Technology

#### Programming Languages:
- Python - Primary language for backend and data processing
- HTML/CSS - Used for styling in frontend components if needed

#### Frameworks and Libraries:
- Streamlit - Frontend framework for user interaction
- FastAPI - Backend framework for handling API requests and business logic
- Pandas - Data manipulation for adherence tracking analytics
- SQLAlchemy - ORM for PostgreSQL database interactions
- Celery - Task queue for scheduling reminders
- Redis - Message broker for Celery task execution
- Twilio API - For sending SMS notifications
- Firebase Email - For sending email notifications
- FHIR Resources - For integrating standardized medication data

#### Database and Storage:
- PostgreSQL - Primary database for storing users, medications, adherence logs
- AWS S3/Firebase Storage - Optional cloud storage for handling prescription images

#### Deployment and Infrastructure:
- Azure - Cloud hosting for scalability and reliability
- Docker - Containerization for backend services
- GitHub Actions - CI/CD pipeline for automated deployment
