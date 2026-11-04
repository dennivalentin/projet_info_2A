from dao.db_connection import DBConnection
from business_object.import_bo import Import


class ImportDao:
    def create(self, import_task: Import) -> Import:
        """Insère une nouvelle tâche d'importation en base."""
        query = """
            INSERT INTO import (
                user_id, start_date, end_date, 
                trigger_type, status, nb_calls, 
                nb_neo, nb_approaches
            ) VALUES (
                %(user_id)s, %(start_date)s, %(end_date)s, 
                %(trigger_type)s, %(status)s, %(nb_calls)s, 
                %(nb_neo)s, %(nb_approaches)s
            )
            RETURNING import_id;
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    {
                        "user_id": import_task._user_id,
                        "start_date": import_task._start_date,
                        "end_date": import_task._end_date,
                        "trigger_type": import_task._trigger_type,
                        "status": import_task._status,
                        "nb_calls": import_task._nb_calls,
                        "nb_neo": import_task._nb_neo,
                        "nb_approaches": import_task._nb_approaches,
                    },
                )
                res = cur.fetchone()
                if res:
                    import_task._import_id = res["import_id"]
        return import_task

    def update(self, import_task: Import) -> bool:
        """Met à jour le statut et les compteurs de la tâche à la fin de l'import."""
        if not getattr(import_task, "_import_id", None):
            return False

        query = """
            UPDATE import
            SET status = %(status)s,
                nb_calls = %(nb_calls)s,
                nb_neo = %(nb_neo)s,
                nb_approaches = %(nb_approaches)s
            WHERE import_id = %(import_id)s;
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    {
                        "status": import_task._status,
                        "nb_calls": import_task._nb_calls,
                        "nb_neo": import_task._nb_neo,
                        "nb_approaches": import_task._nb_approaches,
                        "import_id": import_task._import_id,
                    },
                )
                return cur.rowcount > 0

    def find_last_successful_import(self) -> Import | None:
        """Get the last successful import"""
        query = """
            SELECT import_id, user_id, start_date, end_date, 
                   trigger_type, status, nb_calls, nb_neo, nb_approaches
            FROM import
            WHERE status = 'success'
            ORDER BY end_date DESC
            LIMIT 1;
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                row = cur.fetchone()
                if not row:
                    return None

                task = Import(
                    user_id=row["user_id"],
                    start_date=row["start_date"],
                    end_date=row["end_date"],
                    trigger_type=row["trigger_type"],
                    status=row["status"],
                    nb_calls=row["nb_calls"],
                    nb_neo=row["nb_neo"],
                    nb_approaches=row["nb_approaches"],
                    import_id=row["import_id"],
                )
                task._import_id = row[0]
                return task


