from db import get_connection


def create_student(fullname, username, email,password):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # check whether the user exists
        cur.execute("SELECT COUNT(*) FROM Student where email=%s ", (email,))
        count = cur.fetchone()[0]
        if count > 0:
            cur.close()
            conn.close()
            return False

        # create new user and return the created row
        cur.execute(
            "INSERT INTO Student (full_name,username,email,hashed_password) VALUES (%s, %s, %s, %s) RETURNING *;",
            (fullname, username, email, password),
        )
        user = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return user
    except Exception:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass
        return False
    


def check_student(email ,password):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Student WHERE email=%s AND hashed_password = %s",(email,password))

        user = cur.fetchone()

        print(user)
       
        
        conn.commit()
        cur.close()
        conn.close()
        return user
       
    except Exception as e:
        return None


def get_user_by_id(user_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Student WHERE student_id=%s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user
    except Exception:
        return None


def update_bio(user_id, bio_text):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE Student SET bio=%s WHERE student_id=%s", (bio_text, user_id))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(e)
        try:
            cur.close()
            conn.close()
        except Exception:
            pass
        return False


def get_followers_count(user_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM UserFollows WHERE following_id=%s", (user_id,))
        cnt = cur.fetchone()[0]
        cur.close()
        conn.close()
        return cnt
    except Exception:
        return 0


def get_following_count(user_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM UserFollows WHERE follower_id=%s", (user_id,))
        cnt = cur.fetchone()[0]
        cur.close()
        conn.close()
        return cnt
    except Exception:
        return 0