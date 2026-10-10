import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def run_init_sql():
    """
    Create necessary table for the app (No observation in it)
    """
    sql_path = Path("data/init_db.sql")
    if not sql_path.exists():
        print(f"File not found : {sql_path.resolve()}")
        return

    with open(sql_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    print("Connection to PostgreSQL...")
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

    try:
        with conn.cursor() as cur:
            cur.execute(sql_content)
        conn.commit()
        print("All tables has been reset")
    except Exception as e:
        conn.rollback()
        print(f"SQL error: {e}")
    finally:
        conn.close()


run_init_sql()
