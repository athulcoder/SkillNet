from db import get_connection


def create_student(fullname, username, email,password):
    try:
        conn = get_connection()
        cur = conn.cursor()


        #check whether the user exists
        cur.execute("SELECT COUNT(*) FROM Student where email=%s ",(email,))

        count = cur.fetchone()[0]
        if(count>0):
            cur.close()
            conn.close()
            return False
        

        #create new user
        cur.execute("INSERT INTO Student (full_name,username,email,hashed_password) VALUES (%s, %s,%s,%s);", (fullname,username,email,password))

        conn.commit()
        cur.close()
        conn.close()

        return True
    except Exception as e:
        return False