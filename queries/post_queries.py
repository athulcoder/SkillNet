from db import get_connection


def create_post(user_id, caption, image_url):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO Post (user_id, caption, image_url) VALUES (%s,%s,%s) RETURNING *;",
            (user_id, caption, image_url),
        )

        row = cur.fetchone()

        columns = [desc[0] for desc in cur.description]

        post = dict(zip(columns, row))

        conn.commit()

        cur.close()
        conn.close()

        return post

    except Exception:
        try:
            cur.close()
            conn.close()
        except:
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

        columns = [desc[0] for desc in cur.description]

        posts = [dict(zip(columns, row)) for row in rows]

        cur.close()
        conn.close()

        return posts

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


def get_feed_posts(limit=50):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT 
            p.post_id,
            p.caption,
            p.image_url,
            p.published_at,
            s.student_id,
            s.full_name,
            s.username,
            s.profile_pic
        FROM Post p
        JOIN Student s ON p.user_id = s.student_id
        ORDER BY p.published_at DESC
        LIMIT %s
        """, (limit,))

        rows = cur.fetchall()

        columns = [desc[0] for desc in cur.description]

        posts = [dict(zip(columns,row)) for row in rows]

        cur.close()
        conn.close()

        return posts

    except Exception as e:
        print(e)
        return []