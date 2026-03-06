from db import get_connection


def create_post(user_id, caption, image_url):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Post (user_id, caption, image_url) VALUES (%s, %s, %s) RETURNING *;",
            (user_id, caption, image_url),
        )
        post = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return post
    except Exception:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass
        return None


def get_posts_by_user(user_id, limit=50):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM Post WHERE user_id=%s ORDER BY published_at DESC LIMIT %s",
            (user_id, limit),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception:
        return []


def count_posts_by_user(user_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Post WHERE user_id=%s", (user_id,))
        cnt = cur.fetchone()[0]
        cur.close()
        conn.close()
        return cnt
    except Exception:
        return 0
