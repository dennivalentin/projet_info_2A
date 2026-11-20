"""HTTP client used by all the pages to call the backend API (adds the JWT token)."""

import logging
import os

import requests
import streamlit as st

DEFAULT_TIMEOUT = int(os.getenv("BACKEND_TIMEOUT", 5))
API_URL = os.getenv("BACKEND_URL", "http://localhost:5000")


class APIClient:
    """A client for making authenticated HTTP requests to a backend API.

    Attributes:
        base_url (str): The base URL of the API.
        timeout (int): Default timeout for requests in seconds.
        session (requests.Session): The requests session used for connection pooling.
    """

    def __init__(self, base_url: str, timeout: int = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _get_headers(self) -> dict:
        """Generates headers, including the authentication token if present.

        Returns:
            dict: A dictionary containing the request headers.
        """
        headers = {}
        # Retrieve the token stored in Streamlit's session_state
        token = st.session_state.get("access_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
            headers["X-Auth-Token"] = token
        return headers

    def _refresh_access_token(self) -> bool:
        """Gets a new access token with the refresh token (the access token lasts 30 min).

        Returns:
            bool: True if the tokens of the session were renewed.
        """
        refresh_token = st.session_state.get("refresh_token")
        if not refresh_token:
            return False
        try:
            response = self.session.post(
                f"{self.base_url}/login/refresh",
                json={"refresh_token": refresh_token},
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException:
            return False
        if response.status_code != 200:
            return False
        tokens = response.json()
        st.session_state["access_token"] = tokens["access_token"]
        st.session_state["refresh_token"] = tokens.get("refresh_token", refresh_token)
        return True

    def _request(self, method: str, path: str, **kwargs):
        """Internal centralized method for all types of requests.

        When the access token has expired (401), it is renewed once with the
        refresh token and the request is sent again. If the session cannot be
        renewed, the user is sent back to the login page.

        Args:
            method (str): The HTTP method to use (e.g., 'GET', 'POST').
            path (str): The API endpoint path.
            **kwargs: Additional arguments passed to the requests.request method.
        Returns:
            dict: A dictionary containing the 'status_code' and the response 'data'.
        """
        url = f"{self.base_url}{path}"
        # Logger of the current page (see log_init.get_page_logger)
        logger = st.session_state.get("logger") or logging.getLogger("api_client")
        logger.info(f"  {method} {url}")

        # Automatically inject headers (including the token)
        headers = kwargs.pop("headers", {})
        headers.update(self._get_headers())
        timeout = kwargs.pop("timeout", self.timeout)

        response = None
        data = None
        try:
            response = self.session.request(
                method=method, url=url, timeout=timeout, headers=headers, **kwargs
            )
            if (
                response.status_code == 401
                and st.session_state.get("access_token")
                and not path.startswith("/login")
            ):
                if self._refresh_access_token():
                    headers.update(self._get_headers())
                    response = self.session.request(
                        method=method, url=url, timeout=timeout, headers=headers, **kwargs
                    )
                else:
                    logger.info("Session expired: back to the login page")
                    st.session_state.clear()
                    st.switch_page("pages/home.py")

            try:
                data = response.json()
            except Exception:
                data = response.text

            return {"status_code": response.status_code, "data": data}

        except requests.exceptions.Timeout:
            return {"status_code": 0, "data": "Timeout"}
        except requests.exceptions.ConnectionError:
            return {"status_code": 0, "data": "Connection error"}
        except requests.exceptions.RequestException as e:
            return {"status_code": 0, "data": str(e)}
        finally:
            # Only log if a response was actually received
            if response is not None:
                logger.info(f"  {response.status_code} {response.reason}")
                logger.debug(f"  {data}")

    def get(self, path: str, params=None, **kwargs):
        """Sends a GET request.
        Args:
            path (str): The endpoint path.
            params (dict, optional): Query parameters.
            **kwargs: Additional arguments for requests.request.
        Returns:
            dict: The response dictionary.
        """
        return self._request(method="GET", path=path, params=params, **kwargs)

    def post(self, path: str, json=None, data=None, **kwargs):
        """Sends a POST request.
        Args:
            path (str): The endpoint path.
            json (dict, optional): JSON body for the request.
            data (dict/bytes, optional): Form data or raw body.
            **kwargs: Additional arguments for requests.request.
        Returns:
            dict: The response dictionary.
        """
        return self._request(method="POST", path=path, json=json, data=data, **kwargs)

    def put(self, path: str, json=None, data=None, **kwargs):
        """Sends a PUT request.
        Args:
            path (str): The endpoint path.
            json (dict, optional): JSON body for the request.
            data (dict/bytes, optional): Form data or raw body.
            **kwargs: Additional arguments for requests.request.
        Returns:
            dict: The response dictionary.
        """
        return self._request(method="PUT", path=path, json=json, data=data, **kwargs)

    def delete(self, path: str, **kwargs):
        """Sends a DELETE request.
        Args:
            path (str): The endpoint path.
            **kwargs: Additional arguments for requests.request.
        Returns:
            dict: The response dictionary.
        """
        return self._request(method="DELETE", path=path, **kwargs)


def error_message(response: dict, default: str = "Error") -> str:
    """Readable error of an API answer: the "detail" given by FastAPI, if any."""
    data = response.get("data") if response else None
    if isinstance(data, dict) and "detail" in data:
        detail = data["detail"]
        if isinstance(detail, list):  # 422: list of the invalid fields
            return "; ".join(
                f"{error.get('loc', ['?'])[-1]}: {error.get('msg', '')}" for error in detail
            )
        return str(detail)
    return str(data) if data else default


def fetch_new_notifications() -> list[str]:
    """Gets the new alert notifications and keeps them for the session.

    The backend gives each notification once (F6): they are stored in
    st.session_state["notifications"] so that the alerts page can show them again.
    """
    user = st.session_state.get("user") or {}
    res = api_client.get(f"/alerts/user/{user.get('user_id')}/notifications")
    new = res.get("data", {}).get("notifications", []) if res.get("status_code") == 200 else []
    st.session_state.setdefault("notifications", [])
    st.session_state["notifications"] = new + st.session_state["notifications"]
    return new


api_client = APIClient(API_URL)
