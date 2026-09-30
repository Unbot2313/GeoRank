# GeoRank

A web platform that tells small businesses why AI assistants don't recommend them — and what to fix.

GeoRank is a Django web application built around Generative Engine Optimization (GEO).
A business owner submits their website URL and gets back an AI visibility score, a
content readability and citability report, and a prioritized list of actionable
recommendations. Unlike traditional SEO tools, which optimize for search engine
rankings, GeoRank optimizes for being cited and recommended by AI assistants such as
ChatGPT, Perplexity, and Gemini.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Team](#team)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Documentation](#documentation)

## Features

### Implemented

- URL analysis: submit a website URL and get it analyzed, with validation and clear error handling when a site is unreachable or times out.
- AI visibility score: a single score summarizing how likely the business is to be surfaced by AI assistants.
- Readability and citability scores: evaluate how understandable and usable the site's content is for AI systems.
- Recommendations: a prioritized, non-technical list of actions to improve visibility.
- Accounts: user registration, login, logout, password validation, and authenticated access to the platform.
- User profile: update username, email, company name, and industry sector.
- Free plan limits: Free users can perform up to 3 successful analyses per day. Failed analyses do not consume the daily limit.
- Analysis history: users can review previous completed and failed analyses.
- Score history: track Visibility, Readability, and Citability scores for the same website over time.

### Planned for future deliveries

- Competitor comparison: register competitors and compare their AI visibility scores against the user's website.
- PDF export: download the full analysis report as a PDF.
- Email notifications: notify users when an analysis report is ready.
- Password recovery: reset forgotten passwords through email.
- More specialized recommendations based on the company's industry sector.

Scope and priorities are tracked as MoSCoW-labeled issues in the [backlog](https://github.com/users/Unbot2313/projects/6).

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + Django 6 (MVT) |
| AI Analysis | Google Gemini 2.5 Flash |
| Web Scraping | requests + BeautifulSoup4 |
| Frontend | Tailwind CSS (CDN) |
| Database | SQLite |
| Dependency management | uv |
| Version control | Git + GitHub |
| Project management | GitHub Projects + Wiki |

## Team

| Name | Role | GitHub | Email |
|---|---|---|---|
| Tomas Ramirez Galeano | Product / Development | [@unbot2313](https://github.com/unbot2313) | tramirezg@eafit.edu.co |
| Miguel Angel Alzate Osorno | Development / Documentation | [@alzate4664](https://github.com/alzate4664) | maalzateo1@eafit.edu.co |
| Alessandro Soccol Mejia | Design / Testing | [@AlessandroSoccol](https://github.com/AlessandroSoccol) | asoccolm@eafit.edu.co |

Course: Proyecto Integrador 1 (ST0251) — Universidad EAFIT

## Getting Started

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Git

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/Unbot2313/GeoRank.git
cd GeoRank
```

**2. Install dependencies**

`uv` creates the virtual environment and installs everything from the lockfile:

```bash
uv sync
```

**3. Set up environment variables**

```bash
cp .env.example .env
```

Then open `.env` and fill in:

- `DJANGO_SECRET_KEY` — generate one with:

  ```bash
  uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

- `GEMINI_API_KEY` — free key from [Google AI Studio](https://aistudio.google.com/apikey)

The remaining variables have working defaults for local development. `.env` is
git-ignored and must never be committed.

**4. Apply migrations and create a superuser**

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

**5. Run the development server**

```bash
uv run python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

### Working with dependencies

```bash
uv add <package>       # add a dependency
uv remove <package>    # remove a dependency
uv sync                # install from the lockfile
```

Never call `pip` or `python` directly — always go through `uv`. The `uv.lock` file is
committed so every member gets identical versions.

`requirements.txt` is generated from the lockfile and kept in the repository for
tooling that expects it. Do not edit it by hand — regenerate it after changing
dependencies:

```bash
uv export --no-hashes --no-dev --no-emit-project --format requirements-txt -o requirements.txt
```

If you prefer plain pip, `pip install -r requirements.txt` installs the same
pinned versions.

## Project Structure

```
GeoRank/
├── georank/              # Project settings, main URLs, WSGI/ASGI
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── analysis/             # URL analysis feature app
│   ├── models.py         # Analysis, Score, Recommendation
│   ├── views.py          # Submit URL, view results
│   ├── forms.py          # URL input form
│   ├── urls.py           # App routes
│   ├── services/
│   │   ├── scraper.py    # Web content extraction
│   │   ├── gemini.py     # Gemini API integration
│   │   └── pipeline.py   # Analysis orchestration
│   └── templates/
│       └── analysis/     # HTML templates (Tailwind)
├── .env.example          # Environment variables template
├── manage.py
├── requirements.txt      # Pinned deps, generated from uv.lock
├── pyproject.toml        # Dependencies
└── uv.lock               # Pinned versions
```

## Contributing

Work happens on branches, never directly on `main`:

```
feat/user-login
fix/broken-pagination
chore/update-deps
```

Commits are a single lowercase line: `feat: login`, `fix: null ranking score`.
Open a pull request against `main` when the work is ready.

## Documentation

Full project documentation lives in the [GitHub Wiki](https://github.com/Unbot2313/GeoRank/wiki):

- [Product Vision Board](https://github.com/Unbot2313/GeoRank/wiki/Product-Vision-Board)
- [Requirements Specification](https://github.com/Unbot2313/GeoRank/wiki/Activities)
- [Team Members](https://github.com/Unbot2313/GeoRank/wiki/Team-Members)
- [Weekly Meetings](https://github.com/Unbot2313/GeoRank/wiki/Weekly-Meetings)

The backlog and Kanban board are tracked in [GitHub Projects](https://github.com/users/Unbot2313/projects/6).
