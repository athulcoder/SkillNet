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