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

- **URL analysis:** submit a website URL and get it analyzed, with validation and clear error handling when a site is unreachable or times out.
- **AI visibility score:** a single score summarizing how likely the business is to be surfaced by AI assistants.
- **Readability report:** a content readability and citability breakdown of the analyzed site.
- **Recommendations:** a prioritized, non-technical list of actions to improve visibility.
- **Accounts:** email and password registration and login, with the dashboard restricted to authenticated users.
- **Competitor comparison:** measure the visibility score against selected competitors.
- **PDF export:** download the full report.
- **Score history:** track visibility improvements over time.

Scope and priorities are tracked as MoSCoW-labeled issues in the [backlog](https://github.com/users/Unbot2313/projects/6).

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + Django 6 (MVT) |
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

**3. Apply migrations and create a superuser**

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

**4. Run the development server**

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

## Project Structure

```
GeoRank/
├── georank/          # Project settings, main URLs, WSGI/ASGI
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── manage.py
├── pyproject.toml    # Dependencies
└── uv.lock           # Pinned versions
```

Feature apps will be added as development progresses.

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
