from flask import Flask, request,render_template,make_response,jsonify,session,url_for,redirect

from queries.student_queries import create_student,check_student
app = Flask(__name__)
app.secret_key = "skillnetspecialkehkwefbwlfbwbefbwlbejfbjwleb"

@app.route("/feed", methods=["POST", "GET"])
def feedPage():
    
    if request.method=="POST":
        data = request.get_json()

        return data,200
    
    return make_response(render_template('/feed.html', active_page="feed"))

@app.route("/search", methods=["POST", "GET"])
def searchPage():
    
    if request.method=="POST":
        data = request.get_json()

        return data,200
    
    return make_response(render_template('/search.html', active_page="search"))




@app.route("/profile", methods=["POST", "GET"])
def ProfilePage():
    
    if request.method=="POST":
        data = request.get_json()

        return data,200
    
    return make_response(render_template('/profile.html', active_page="profile"))

@app.route("/login", methods=["POST", "GET"])
def login():
    
    if request.method=="POST":
        email = request.form.get('email')
        password = request.form.get('password')


        if not email and not password:
                return render_template("login.html", error="All feilds are required")
        

        user = check_student(email=email, password=password)

        if not user:
            return render_template("login.html", error="Invalid credentials entered")
        
        print(user)
        session['user'] = {
            "email":user[3],
            "username":user[2],
            "fullname":user[1]
        }

        return redirect(url_for("feedPage"))
    
    return make_response(render_template('/login.html'))


@app.route("/signup", methods=["POST", "GET"])
def signup():

    if request.method=="POST":

        full_name = request.form.get('fullname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not full_name or not username or not email or not password :
                return render_template("signup.html", error="All feilds are required")

        
        result = create_student(
            full_name,
            username,
            email,
            password
        )

        if not result:
            return render_template("signup.html", error="User already exists")

        
        session["user"] ={
            "email":email,
            "username":username,
            "fullname":full_name
        }
        return redirect(url_for("feedPage"))
        
        
    
    return make_response(render_template('/signup.html'))



app.run(debug=True, host="0.0.0.0", port=8000)

