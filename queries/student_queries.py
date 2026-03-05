from db import get_connection


def create_student(fullname, username, email,password,profile_pic,bio,dob,institution,location):
    conn = get_connection()
    cur = conn.cursor()


    #check whether the user exists
    cur.execute("SELECT COUNT(*) FROM Student where email=%s ",(email,))

    count = cur.fetchone()[0]
    if(count>0):
        cur.close()
        conn.close()
        return "User already exsits"
    

    #create new user
    cur.execute("INSERT INTO Student (full_name,username,email,hashed_password,profile_pic,bio,dob,institution) VALUES (%s, %s,%s,%s,%s,%s,%s,%s);", (fullname,username,email,password,profile_pic,bio,dob,institution))

    conn.commit()
    cur.close()
    conn.close()

    return "User Created Successfully "