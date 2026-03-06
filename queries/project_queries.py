from db import get_connection


def create_project(user_id, title, description, github_url=None, demo_url=None, visibility='Public'):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Project (user_id, title, description, github_url, demo_url, visibility) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *;",
            (user_id, title, description, github_url, demo_url, visibility),
        )
        project = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return project
    except Exception:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass
        return None


def get_projects_by_user(user_id, limit=50):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM Project WHERE user_id=%s ORDER BY created_at DESC LIMIT %s",
            (user_id, limit),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception:
        return []


def count_projects_by_user(user_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Project WHERE user_id=%s", (user_id,))
        cnt = cur.fetchone()[0]
        cur.close()
        conn.close()
        return cnt
    except Exception:
        return 0
