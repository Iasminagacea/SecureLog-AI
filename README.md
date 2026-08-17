# SecureLog AI – AI-Powered Security Log Analyzer

**SecureLog AI** is a modern cybersecurity application built to parse, analyze, and interpret system logs to detect malicious patterns and potential cyberattacks. 

By leveraging Artificial Intelligence, the application not only flags suspicious activities but also provides detailed, structured reports containing a severity classification (Risk Level) and step-by-step remediation strategies.

## What it does
- **Log Analysis:** Analyzes raw system logs sent via file upload or JSON payload.
- **Threat Detection:** Detects common threat patterns such as Brute Force Attacks, SQL Injection (SQLi), Cross-Site Scripting (XSS), and Unauthorized Access.
- **Risk Classification:** Classifies the detected incidents into risk levels (Low, Medium, High).
- **Remediation Steps:** Suggests actionable, step-by-step solutions to mitigate the detected vulnerabilities.
- **Auditing:** Stores historical analysis reports in a database for easy retrieval and auditing.

## Technologies and Languages Used
- **Programming Language:** Python 3
- **Backend Framework:** Flask (RESTful API)
- **Database:** MongoDB (PyMongo)
- **Artificial Intelligence:** Google Gemini API (LLM for intelligent log analysis and triage)
- **Containerization:** Docker & Docker Compose

---

## Quick Start (Docker Compose)

The easiest way to run the application is by using **Docker Compose**.

### 1. Environment Setup
Create a `.env` file in the root directory and add your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Run the Application
Run the following command to build and start both the Flask API and the MongoDB instance:
```bash
docker-compose up --build
```
The API will be available at `http://localhost:5000`.

---

## API Endpoints Overview

- `GET /health` 
  Checks the connection status to MongoDB and verifies if the Gemini API key is configured.
  
- `POST /analyze` 
  Accepts a log file upload (e.g., `sample_logs.json`) or raw JSON log data and returns the AI-generated security analysis containing the risk level and fix suggestions.

- `GET /reports` 
  Retrieves the latest 20 security reports stored in the MongoDB database.
