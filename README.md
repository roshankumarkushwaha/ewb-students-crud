# Students Database CRUD API — EWB Internship Project

A structured FastAPI + SQLite backend for the EWB Edu Tech Python Backend Development assignment. Includes mandatory CRUD operations and extra features: filtering, pagination, statistics, CSV export, automated tests, and optional local Ollama question answering.

**Use fictional sample data. Do not publish real student personal information.**

## Features

### Required
- Create, read, update, and delete student records.
- SQLite persistence and auto-generated student IDs.
- Student name, date of birth, email and/or phone, plus optional course, address, enrollment date.
- Input validation, duplicate-email protection, missing-record errors.
- Interactive OpenAPI documentation and reproducible setup instructions.

### Additional
- Filter by name, course, or email.
- Pagination with total result count.
- Student statistics grouped by course.
- CSV export.
- Automated tests.
- Optional Ollama natural-language Q&A grounded in database records. The model cannot execute SQL.

## Structure

```text
ewb_students_crud_pro/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── crud.py
│   ├── schemas.py
│   ├── ai_assistant.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   └── test_students.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

`students.db` is created automatically and excluded from Git.

## Requirements
- Python 3.10+
- pip
- Optional AI: install Ollama and download `llama3.2:1b`.

## Setup (Windows PowerShell)

Open the extracted folder in VS Code and choose Terminal → New Terminal.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If `py` is unavailable, use `python` to create the environment. If PowerShell blocks activation, run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.

## Start the API

```powershell
python -m uvicorn app.main:app --reload
```

- Home: http://127.0.0.1:8000/
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health: http://127.0.0.1:8000/health

Keep the terminal running; press Ctrl+C to stop.

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API overview |
| GET | `/health` | Basic health check |
| POST | `/students` | Create student |
| GET | `/students` | List, filter, paginate |
| GET | `/students/{student_id}` | Retrieve one |
| PUT | `/students/{student_id}` | Replace student fields |
| PATCH | `/students/{student_id}` | Update selected fields |
| DELETE | `/students/{student_id}` | Delete student |
| GET | `/stats` | Student statistics |
| GET | `/students/export.csv` | Download CSV |
| POST | `/ai/ask` | Optional Ollama Q&A |

## Example: create a student

Use Swagger UI → `POST /students` → Try it out.

```json
{
  "name": "Asha Sharma",
  "date_of_birth": "2005-04-12",
  "email": "asha@example.com",
  "phone": "9800000000",
  "course": "Computer Science",
  "address": "Birgunj, Nepal",
  "enrollment_date": "2025-08-01"
}
```

At least one contact field (email or phone) is required. Email must be valid and unique.

### Filtering and pagination
- `/students?name=Asha`
- `/students?course=Computer`
- `/students?email=asha@example.com`
- `/students?limit=10&offset=0`

The list response includes `items`, `total`, `limit`, and `offset`.

### Partial update
`PATCH /students/1` body:

```json
{"course": "Artificial Intelligence and Machine Learning"}
```

### Statistics and CSV
Open `GET /stats` for counts and recent records. Open `GET /students/export.csv` to download all records.

## Optional local AI with Ollama

The core CRUD project works without Ollama.

1. Install Ollama from https://ollama.com/
2. Run `ollama pull llama3.2:1b` in a terminal.
3. Ensure Ollama is running at `http://127.0.0.1:11434`.
4. In Swagger UI, use `POST /ai/ask` with:

```json
{
  "question": "How many students are there?",
  "model": "llama3.2:1b"
}
```

The backend fetches up to 200 student records and sends a JSON snapshot as context. The model is not allowed to execute SQL or change data. AI answers can still be inaccurate, so verify results against `/students` and `/stats`. Use fictional data for demonstrations.

## Run automated tests

```powershell
python -m pytest -v
```

Tests use a temporary SQLite database and cover CRUD, validation, duplicate emails, missing records, filtering, stats, and CSV export.

## Common status codes
- `200`: read or update successful.
- `201`: record created.
- `204`: record deleted.
- `400`: invalid update request.
- `404`: student not found.
- `409`: duplicate email.
- `422`: validation error.
- `503`: Ollama unavailable.

## GitHub submission

1. Test all CRUD operations in `/docs`.
2. Run `python -m pytest -v` and fix any failures.
3. Check that `.venv`, `.env`, `students.db`, secrets, and real student records are not staged.
4. Create an empty GitHub repository.
5. From this project folder, run the following, replacing the URL with your repository URL:

```powershell
git init
git add .
git commit -m "Build student management API with FastAPI and SQLite"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

6. Confirm the files appear on GitHub, then submit that repository URL using your trainer's announced channel.

## Architecture
- `main.py`: HTTP routes, status codes, OpenAPI docs.
- `schemas.py`: validation and response models.
- `crud.py`: SQL/database operations.
- `database.py`: SQLite connection, transactions, schema.
- `ai_assistant.py`: isolated optional Ollama integration.
- `tests/`: automated checks.

This is an educational project, not a production-ready system for sensitive records. Before real deployment, add authentication, authorization, backups, deployment hardening, and privacy controls.
