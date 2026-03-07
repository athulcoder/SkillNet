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


def get_user_id_by_username(username):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT student_id FROM Student WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user
    except Exception:
        return None



def get_user_profile_data(user_id):

    try:
        conn = get_connection()
        cur = conn.cursor()

        # user info
        cur.execute("""
        SELECT
            student_id,
            full_name,
            username,
            email,
            profile_pic,
            bio,
            dob,
            institution,
            location
        FROM Student
        WHERE student_id = %s
        """,(user_id,))

        user = cur.fetchone()

        if not user:
            return None


        # skills
        cur.execute("""
        SELECT s.skill_id, s.skill_name, s.skill_category
        FROM Skill s
        JOIN UserSkill us
        ON s.skill_id = us.skill_id
        WHERE us.user_id = %s
        """,(user_id,))

        skills = cur.fetchall()


        # projects
        cur.execute("""
        SELECT
            project_id,
            title,
            description,
            github_url,
            demo_url,
            visibility,
            created_at
        FROM Project
        WHERE user_id = %s
        ORDER BY created_at DESC
        """,(user_id,))

        projects = cur.fetchall()


        # posts
        cur.execute("""
        SELECT
            post_id,
            caption,
            image_url,
            location,
            published_at
        FROM Post
        WHERE user_id = %s
        ORDER BY published_at DESC
        """,(user_id,))

        posts = cur.fetchall()


        # followers
        cur.execute("""
        SELECT COUNT(*)
        FROM UserFollows
        WHERE following_id = %s
        """,(user_id,))

        followers = cur.fetchone()[0]


        # following
        cur.execute("""
        SELECT COUNT(*)
        FROM UserFollows
        WHERE follower_id = %s
        """,(user_id,))

        following = cur.fetchone()[0]


        cur.close()
        conn.close()

        return {
            "user": user,
            "skills": skills,
            "projects": projects,
            "posts": posts,
            "followers": followers,
            "following": following
        }

    except Exception as e:
        print(e)
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
    


    
def toggle_follow(follower_id, following_id):

    try:
        conn = get_connection()
        cur = conn.cursor()

        # check if already following
        cur.execute("""
        SELECT 1 FROM UserFollows
        WHERE follower_id=%s AND following_id=%s
        """,(follower_id,following_id))

        exists = cur.fetchone()

        if exists:
            # unfollow
            cur.execute("""
            DELETE FROM UserFollows
            WHERE follower_id=%s AND following_id=%s
            """,(follower_id,following_id))

            conn.commit()
            cur.close()
            conn.close()

            return {"following":False}

        else:
            # follow
            cur.execute("""
            INSERT INTO UserFollows (follower_id,following_id)
            VALUES (%s,%s)
            """,(follower_id,following_id))

            conn.commit()
            cur.close()
            conn.close()

            return {"following":True}

    except Exception as e:
        print(e)
        return None
    
def is_following(follower_id, following_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT 1 FROM UserFollows
    WHERE follower_id=%s AND following_id=%s
    """,(follower_id,following_id))

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result is not None