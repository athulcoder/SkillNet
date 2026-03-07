from db import get_connection
conn = get_connection()
def get_user_profile(user_id):

    cur = conn.cursor()

    cur.execute("""
    SELECT student_id, full_name, username, email, profile_pic,
           bio, dob, institution, location
    FROM Student
    WHERE student_id = %s
    """,(user_id,))

    return cur.fetchone()


def get_all_skills():

    cur = conn.cursor()

    cur.execute("""
    SELECT skill_id, skill_name
    FROM Skill
    ORDER BY skill_name
    """)

    return cur.fetchall()


def get_user_skills(user_id):

    cur = conn.cursor()

    cur.execute("""
    SELECT skill_id
    FROM UserSkill
    WHERE user_id=%s
    """,(user_id,))

    return [x[0] for x in cur.fetchall()]


def update_profile(user_id,bio,dob,institution,location,profile_pic):

    cur = conn.cursor()

    cur.execute("""
    UPDATE Student
    SET bio=%s,
        dob=%s,
        institution=%s,
        location=%s,
        profile_pic=%s
    WHERE student_id=%s
    """,(bio,dob,institution,location,profile_pic,user_id))

    conn.commit()


def update_user_skills(user_id,skills):

    cur = conn.cursor()

    cur.execute("DELETE FROM UserSkill WHERE user_id=%s",(user_id,))

    for skill in skills:

        cur.execute("""
        INSERT INTO UserSkill (user_id,skill_id)
        VALUES (%s,%s)
        """,(user_id,skill))

    conn.commit()