# Cardiovascular Healthcare App

A comprehensive healthcare application for managing patient data, appointments, test results, and prescriptions, with a focus on cardiovascular health.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [User Roles](#user-roles)
- [Screenshots](#screenshots)

## Overview

This application provides a complete healthcare management system that allows medical staff to:
- Register new patients
- Collect patient lifestyle information
- Schedule appointments
- Record test results
- Generate prescriptions
- Visualize health data trends
- Analyze patient records

The system is designed to streamline the healthcare process while providing valuable insights through data visualization.

## Features

- **Patient Management**: Register new patients and view existing patient records
- **Appointment Scheduling**: Create and manage patient appointments
- **Test Results Recording**: Record and track vital health metrics
- **Prescription Generation**: Create and manage prescriptions based on test results
- **Data Visualization**: View trends in health metrics across patient demographics
- **User Authentication**: Role-based access control for staff and administrators
- **Database Overview**: Administrative view of all database records

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Database**: MySQL
- **Data Visualization**: Matplotlib
- **Data Processing**: Pandas

## System Architecture

The application follows a client-server architecture:

1. **Frontend (app_ui.py)**: Streamlit-based user interface for interacting with the system
2. **Backend (app_main.py)**: FastAPI server that handles HTTP requests and business logic
3. **Database**: MySQL database for persistent storage of healthcare data

## Installation

1. Set up a virtual environment:
```
python -m venv adt_env
source adt_env/bin/activate  # On Windows: adt_env\Scripts\activate
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Set up MySQL database:
   - Create a database named `healthcare_db`
   - Configure the database connection in `app_main.py` (host, port, user, password)

## Usage

1. Start the backend server:
```
uvicorn app_main:app --reload
```

2. Start the frontend application:
```
streamlit run app_ui.py
```

3. Access the application in your web browser at `http://localhost:8501`


## Database Schema

The application uses the following database tables:

- **patient_details**: Basic patient information
- **patient_lifestyle**: Patient lifestyle factors
- **doctors**: Doctor information
- **appointments**: Scheduled appointments
- **test_details**: Health test results
- **prescriptions**: Medication prescriptions

## API Endpoints

### Patient Management
- `POST /patients/new`: Create a new patient
- `POST /patients/lifestyle`: Add lifestyle information for a patient
- `GET /patients/{patient_id}`: Get patient information

### Appointment Management
- `GET /doctors`: Get list of doctors
- `POST /appointments`: Schedule a new appointment
- `GET /appointments/{patient_id}`: Get patient appointments

### Test & Prescription Management
- `POST /tests`: Add test results
- `POST /prescriptions`: Create a prescription
- `GET /records/{appointment_id}`: Get test and prescription records

### Analysis & Data Access
- `GET /fetch/{table}`: Fetch data from a specified table
- `GET /get_analysis`: Get patient analysis data

## User Roles

- **Staff**: Can register patients, schedule appointments, record tests, and generate prescriptions
- **Admin**: Has staff privileges plus access to the database overview and analytics
