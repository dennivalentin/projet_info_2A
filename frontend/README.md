# NEO-Watch frontend: developer guide

User interface built with [Streamlit](https://streamlit.io/). It only talks to the backend API
(no direct database access).

How to install and configure the whole application: see the [README at the root](../README.md).

## 🚀 Run

```bash
uv sync --project frontend --all-extras
cd frontend
uv run streamlit run src/app.py
```

The interface listens on port 8000 (`.streamlit/config.toml`) and calls the API at
`BACKEND_URL` (in the `.env` file at the root of the repository).

## 🏛️ Structure

| Item | Description |
| --- | --- |
| `src/app.py` | Entry point: goes to the menu if logged in, to the login page otherwise |
| `src/pages/home.py` | Log in and create an account |
| `src/pages/neo_menu.py` | Menu with all the features, new alert notifications at login, admin tools |
| `src/pages/dashboard.py` | Dashboard of the period |
| `src/pages/search_neo.py` | Search, details of a NEO, CSV export |
| `src/pages/statistics.py` | Statistics and charts |
| `src/pages/favourites.py` | Favourite NEOs, their approaches (CSV export) and graph (PNG export) |
| `src/pages/alert.py` | Alerts and notifications |
| `src/pages/create_neo.py` | Declare a NEO |
| `src/pages/apod.py` | NASA picture of the day |
| `src/pages/admin.py` | Administrators: accounts (promote, delete) and connection history |
| `src/utils/api_client.py` | HTTP client of the API: adds the JWT token to every request and renews it with the refresh token when it expires |
| `src/utils/auth_guard.py` | Sends back to the login page when the user is not logged in |
| `src/utils/log_init.py` | Logs (`frontend/logs/frontend.log`) and page navigation tracking |

## ⚒️ Code quality

```bash
cd frontend
uv run --all-extras ruff check src
uv run --all-extras mypy src
uv run --all-extras bandit -r src
```
