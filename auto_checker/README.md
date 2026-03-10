# Auto Checker — Competition Answer Sheet Checking System

A Django web application for automated competition answer sheet checking using Gemma AI API for OCR and text analysis.

## Features

- **OMR Sheet Checking** — Upload OMR answer sheet images, auto-extract names & bubbled answers via OCR, compare with answer key, generate scored Excel.
- **Debug Sheet Checking** — Upload buggy pseudo-code answer PDFs, extract error identifications & correct outputs, score against answer key.
- **DSA Round Checking** — Upload coding answer PDFs, evaluate code quality with partial marking using AI analysis.
- **Final Score Merger** — Merge all round Excel files, add manual puzzle scores, generate ranked leaderboard.
- **Spin the Wheel** — Fun round with animated wheel for bonus/penalty assignment.

## Setup

### 1. Clone and enter the project

```bash
cd auto_checker
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Edit the `.env` file and add your Gemma (Google Generative AI) API key:

```
GEMMA_API_KEY=your_actual_api_key_here
```

Get your API key from [Google AI Studio](https://aistudio.google.com/apikey).

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## Project Structure

```
auto_checker/
├── manage.py
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── project/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── checker_app/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── apps.py
│   └── utils/
│       ├── gemma_client.py
│       ├── ocr_utils.py
│       ├── scoring.py
│       └── excel_generator.py
├── templates/
│   ├── base.html
│   ├── omr.html
│   ├── debug.html
│   ├── dsa.html
│   ├── merger.html
│   └── wheel.html
├── static/
│   ├── css/style.css
│   └── js/wheel.js
└── media/
```

## Tech Stack

- **Backend:** Django 4.2
- **AI/OCR:** Google Generative AI (Gemma)
- **Excel:** pandas + openpyxl
- **Frontend:** HTML, CSS, vanilla JS
