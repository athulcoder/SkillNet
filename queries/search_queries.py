from db import get_connection


def search_students(query):

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT
            s.student_id,
            s.full_name,
            s.username,
            s.profile_pic,
            s.institution,
            s.location,
            STRING_AGG(sk.skill_name, ', ') as skills

        FROM Student s

        LEFT JOIN UserSkill us
            ON s.student_id = us.user_id

        LEFT JOIN Skill sk
            ON us.skill_id = sk.skill_id

        WHERE
            s.full_name ILIKE %s
            OR s.username ILIKE %s
            OR sk.skill_name ILIKE %s

        GROUP BY s.student_id

        ORDER BY s.full_name
        LIMIT 20
        """,
        (f"%{query}%", f"%{query}%", f"%{query}%"))

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows

    except Exception as e:
        print(e)
        return []