# 🔭 NEO-Watch

![CI](https://github.com/dennivalentin/projet_info_2A/actions/workflows/ci.yml/badge.svg)

**NEO-Watch** is a web application to explore and monitor **Near-Earth Objects** (NEOs):
asteroids and comets whose orbit comes close to the Earth. The data comes from the
[NASA NeoWs API](https://api.nasa.gov/) and is stored in a PostgreSQL database.

ENSAI 2nd year IT project.

## ✨ Features

| Feature | Description |
| --- | --- |
| 🔐 Accounts | Create an account and log in (JWT authentication). Administrators can reset and update the data. |
| ☄️ Dashboard | Upcoming close approaches over a chosen period, number of NEOs and share of hazardous ones, closest approach, your favourites. |
| 🔍 Search & Explore | Search NEOs by name, size, hazard flag, origin; sort; details and close approaches (km and astronomical units); CSV export. |
| 📊 Statistics | Approaches per month, size distribution, share of potentially hazardous NEOs, mean and median distance, each with an explanation. |
| ⭐ Favourites | Follow NEOs, see their approaches and a graph of their distance to Earth over time. |
| 🔔 Alerts | Define criteria (minimum size, maximum distance, hazardous only) and be notified of the matching approaches. |
| ➕ Declare a NEO | Record your own observation (origin `USER`: it is never overwritten by the NASA imports). |
| 🌌 Picture of the Day | NASA's astronomy picture of the day, with its description, to download. |

The NASA data is imported automatically, in the background: 2 years back and 1 year ahead on
the first launch, then only what is missing, once a day.

## 🚀 Install and launch (SSP Cloud)

You need an [SSP Cloud](https://datalab.sspcloud.fr/) account.

### 1. Start the services

- [ ] Launch a **PostgreSQL** service
- [ ] Launch a **VSCode-python** service, with the ports **5000** (API) and **8000** (interface) open

### 2. Get the code and the dependencies

In a terminal of the VSCode service:

```bash
git clone https://github.com/dennivalentin/projet_info_2A.git
cd projet_info_2A
uv sync --project backend
uv sync --project frontend
```

:warning: Open the folder `projet_info_2A` in VSCode (File > Open Folder): it must be the root
of the explorer.

### 3. Create the `.env` file

Create a file named `.env` at the root of the repository (next to this README) and complete it.
The PostgreSQL values are given in the README of your PostgreSQL service on SSP Cloud.

```default
POSTGRES_HOST=postgresql-<suffix>
POSTGRES_PORT=5432
POSTGRES_DATABASE=defaultdb
POSTGRES_USER=user-<username>
POSTGRES_PASSWORD=<password>
POSTGRES_SCHEMA=project

UVICORN_HOST=0.0.0.0
UVICORN_PORT=5000

BACKEND_URL=http://localhost:5000
BACKEND_TIMEOUT=10

NASA_API_KEY=<your NASA key>

JWT_SECRET_KEY=<a long random key>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

- `NASA_API_KEY`: get a free key in one minute at [api.nasa.gov](https://api.nasa.gov/).
  Without it, the application uses `DEMO_KEY`, limited to a few dozen calls: the first import
  then stops early, and it goes on a little more at each launch (it resumes where it stopped).
- `JWT_SECRET_KEY` is **required**. Generate one with `python key_generator_for_.env.py`.

### 4. Launch the application

Open two terminals, both at the root of the repository:

```bash
uv run --project backend python backend/src/main.py
```

```bash
cd frontend
uv run streamlit run src/app.py
```

:warning: After launching, do not click on the link of the pop-up: on SSP Cloud the
application is reached through the URLs of the next step.

### 5. Open the application

In [My services](https://datalab.sspcloud.fr/my-services), click **Open** on the VSCode
service: it gives the public URLs of the interface (port 8000) and of the API (port 5000).

### 6. First launch

On its first start, the API creates the tables and two accounts by itself (`data/init_db.sql`
and `data/pop_db.sql`):

| Username | Password | Role |
| --- | --- | --- |
| `admin` | `admin` | administrator |
| `observateur` | `observateur` | user |

Log in, then the NASA import starts in the background: the NEOs appear little by little.
You can also create your own account from the login page.

:lock: Change the `admin` password before any real use.

## 🗂️ Project structure

| Item | Description |
| --- | --- |
| `backend/` | REST API (FastAPI), layered architecture: see [backend/README.md](backend/README.md) |
| `frontend/` | User interface (Streamlit): see [frontend/README.md](frontend/README.md) |
| `data/` | SQL scripts: `init_db.sql` creates the tables, `pop_db.sql` the seed data, `pop_db_test.sql` the test data |
| `doc/` | Report, tracking documents, UML diagrams |
| `.github/workflows/ci.yml` | Continuous integration: tests, Ruff and Bandit on every push |
| `key_generator_for_.env.py` | Generates a value for `JWT_SECRET_KEY` |

## ⚙️ Continuous integration

On every push, GitHub Actions (`.github/workflows/ci.yml`):

- starts a PostgreSQL database and runs all the backend unit tests, with coverage
- checks the code style of the backend and the frontend with [Ruff](https://docs.astral.sh/ruff/)
- looks for security issues with [Bandit](https://bandit.readthedocs.io/)

The result is in the *Actions* tab of the GitHub repository.

## ❓ Troubleshooting

| Problem | Solution |
| --- | --- |
| `JWT_SECRET_KEY missing in .env` | Add `JWT_SECRET_KEY` to `.env` (step 3). |
| The interface shows "Connection error" | The API is not running, or `BACKEND_URL` is wrong. |
| Few NEOs, or none in the coming days | The NASA import is limited by `DEMO_KEY`: set your own `NASA_API_KEY`, then restart the API. |
| Data to start again from scratch | Log in as `admin`, then **Reset database** in the menu. |
