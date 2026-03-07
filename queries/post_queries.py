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


def get_feed_posts(current_user_id, limit=50):
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
            s.profile_pic,

            COUNT(pl.user_id) AS like_count,

            CASE 
                WHEN EXISTS (
                    SELECT 1 
                    FROM PostLikes 
                    WHERE PostLikes.post_id = p.post_id 
                    AND PostLikes.user_id = %s
                )
                THEN TRUE
                ELSE FALSE
            END AS liked

        FROM Post p

        JOIN Student s 
        ON p.user_id = s.student_id

        LEFT JOIN PostLikes pl 
        ON p.post_id = pl.post_id

        GROUP BY 
            p.post_id,
            s.student_id

        ORDER BY p.published_at DESC

        LIMIT %s
        """, (current_user_id, limit))

        rows = cur.fetchall()

        columns = [desc[0] for desc in cur.description]

        posts = [dict(zip(columns, row)) for row in rows]

        cur.close()
        conn.close()

        return posts

    except Exception as e:
        print(e)
        return []

def toggle_post_like(user_id, post_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # check if already liked
        cur.execute(
            "SELECT 1 FROM PostLikes WHERE user_id=%s AND post_id=%s",
            (user_id, post_id)
        )

        exists = cur.fetchone()

        if exists:
            # remove like
            cur.execute(
                "DELETE FROM PostLikes WHERE user_id=%s AND post_id=%s",
                (user_id, post_id)
            )
            liked = False
        else:
            # add like
            cur.execute(
                "INSERT INTO PostLikes (user_id, post_id) VALUES (%s,%s)",
                (user_id, post_id)
            )
            liked = True

        # get like count
        cur.execute(
            "SELECT COUNT(*) FROM PostLikes WHERE post_id=%s",
            (post_id,)
        )

        like_count = cur.fetchone()[0]

        conn.commit()

        cur.close()
        conn.close()

        return {
            "liked": liked,
            "like_count": like_count
        }

    except Exception as e:
        print(e)
        try:
            cur.close()
            conn.close()
        except:
            pass
        return None