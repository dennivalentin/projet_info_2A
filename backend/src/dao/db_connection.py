import os
import threading

import psycopg2
from psycopg2.extras import RealDictCursor

from utils.singleton import Singleton


class DBConnection(metaclass=Singleton):
    """Database connection manager implementing the Singleton pattern.

    FastAPI runs synchronous endpoints in a pool of worker threads. A single
    psycopg2 connection shared by all threads means they also share the same
    transaction: one failing query (or a long NASA import) breaks the requests
    running at the same time ("current transaction is aborted"...).
    So each thread gets its own connection, re-opened automatically if it was
    closed (database restarted, idle timeout on SSP Cloud, ...).
    """

    def __init__(self):
        self._local = threading.local()

    @staticmethod
    def _connect():
        """Opens a new connection using the POSTGRES_* environment variables.

        Raises:
            KeyError: If any of the required POSTGRES_* environment variables are missing.
            psycopg2.Error: If the connection to the database fails.
        """
        return psycopg2.connect(
            host=os.environ["POSTGRES_HOST"],
            port=os.environ["POSTGRES_PORT"],
            database=os.environ["POSTGRES_DATABASE"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            options=f"-c search_path={os.environ['POSTGRES_SCHEMA']}",
            cursor_factory=RealDictCursor,
        )

    @property
    def connection(self):
        """Provides the database connection of the current thread.
        Returns:
            The established database connection.
        """
        conn = getattr(self._local, "connection", None)
        if conn is None or conn.closed:
            conn = self._connect()
            self._local.connection = conn
        return conn
