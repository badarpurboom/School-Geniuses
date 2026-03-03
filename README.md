# School ERP (Django + React)

This project is a school management system with:

- Django REST backend (`/api/...`)
- React frontend (Vite + Ant Design) in `frontend/`

The old Streamlit UI is no longer required for normal usage.

## Features

- Dashboard metrics and charts
- Student admission
- Staff registration
- Academics:
  - Subject creation
  - Class creation
  - Timetable management
  - Student promotion
- QR attendance
- Fee collection
- Examination scheduling and marks entry
- School AI query assistant (Gemini + LangChain SQL)

## Backend Setup

1. Create and activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install Python dependencies

```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`

```env
GEMINI_API_KEY=your_key_here
```

4. Run backend

```bash
python manage.py migrate
python manage.py runserver
```

Backend runs at `http://127.0.0.1:8000`.

## Frontend Setup (React + Ant Design)

1. Go to frontend folder

```bash
cd frontend
```

2. Install Node dependencies

```bash
npm install
```

3. Create frontend env file

```bash
copy .env.example .env
```

Default value:

```env
VITE_API_BASE_URL=/api
```

4. Run frontend

```bash
npm run dev
```

Frontend runs at `http://127.0.0.1:5173`.
Vite dev server automatically proxies `/api` and `/media` to Django backend (`http://127.0.0.1:8000`).

## Notes

- Login uses Django `/api/login/` and stores token in browser local storage.
- Current backend APIs are mostly open, so token is sent but not strictly required on all endpoints.
- QR attendance page requires browser camera permission.
