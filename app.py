from flask import Flask, request, render_template, make_response, jsonify, session, url_for, redirect, flash
from functools import wraps
import os
import uuid
from werkzeug.utils import secure_filename
import cloudinary_config
from queries.profile_queries import update_profile,update_user_skills,get_all_skills,get_user_profile,get_user_skills
from queries.student_queries import create_student, check_student, get_user_profile_data, update_bio, is_following,toggle_follow,get_user_id_by_username
from queries.post_queries import create_post, count_posts_by_user,get_feed_posts,toggle_post_like
from queries.project_queries import create_project, get_projects_by_user, count_projects_by_user
from queries.search_queries import search_students
import cloudinary
import cloudinary.uploader
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'skillnetspecialkehkwefbwlfbwbefbwlbejfbjwleb')

# Upload configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/', methods=["GET"])
@login_required
def homePage():
     return redirect("/feed")


@app.route("/feed", methods=["POST", "GET"])
@login_required
def feedPage():
    
    if request.method=="POST":
        data = request.get_json()

        return data,200
    
    return make_response(render_template('/feed.html', active_page="feed")),200

@app.route("/search", methods=["POST", "GET"])
@login_required
def searchPage():
    
    if request.method=="POST":
        data = request.get_json()

        return data,200
    
    return make_response(render_template('/search.html', active_page="search")),200

@app.route("/profile/<username>")
@login_required
def profile(username):
    return render_template("profile.html")



@app.route("/post/create")
@login_required
def create_post_page():
    return render_template("add_post.html")


@app.route("/project/create")
@login_required
def create_project_page():
    return render_template("add_project.html")


@app.route("/api/profile-data")
@login_required
def profile_data():

    viewer_id = session["user"]["student_id"]



    username = request.args.get("username")
    # getting the user_id 
    user_id = get_user_id_by_username(username)
    following_state = False

    if viewer_id != user_id[0]:
        following_state = is_following(viewer_id, user_id[0])
    print()
    # if username provided → fetch that profile
    if username:
        print(username)
        data=get_user_profile_data(user_id[0]) #since tuple taking the first value (which is user_id of the given username)
    else:
        data = get_user_profile_data(viewer_id)

    if not data:
        return jsonify({"error": "User not found"}), 404


    user = data["user"]
    skills = data["skills"]
    projects = data["projects"]
    posts = data["posts"]


    user_json = {
        "student_id": user[0],
        "full_name": user[1],
        "username": user[2],
        "email": user[3],
        "profile_pic": user[4],
        "bio": user[5],
        "dob": user[6],
        "institution": user[7],
        "location": user[8]
    }


    skills_json = [
        {
            "skill_id": s[0],
            "skill_name": s[1],
            "category": s[2]
        }
        for s in skills
    ]


    projects_json = [
        {
            "project_id": p[0],
            "title": p[1],
            "description": p[2],
            "github_url": p[3],
            "demo_url": p[4],
            "visibility": p[5],
            "created_at": p[6]
        }
        for p in projects
    ]


    posts_json = [
        {
            "post_id": p[0],
            "caption": p[1],
            "image_url": p[2],
            "location": p[3],
            "published_at": p[4]
        }
        for p in posts
    ]


    return jsonify({

        "user": user_json,

        "stats": {
            "posts": len(posts),
            "projects": len(projects),
            "followers": data["followers"],
            "following": data["following"]
        },

        "skills": skills_json,
        "projects": projects_json,
        "posts": posts_json,

        "is_self": viewer_id == user[0],
        "following": following_state

    })

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return jsonify({"success": True})

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

        session['user'] = {
            'student_id': user[0],
            'fullname': user[1],
            'username': user[2],
            'email': user[3],
            'profileUrl': user[5] if len(user) > 5 else None,
            'bio': user[6] if len(user) > 6 else None,
        }

        return render_template(("feed.html"))
    
    return make_response(render_template('/login.html'))


@app.route("/signup", methods=["POST", "GET"])
def signup():

    if request.method=="POST":

        full_name = request.form.get('fullname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not full_name or not username or not email or not password :
                return render_template("signup.html", error="All feilds are required"),401

        
        result = create_student(full_name, username, email, password)

        if not result:
            return render_template("signup.html", error="User already exists"), 401

        # result is the created user row
        session["user"] = {
            'student_id': result[0],
            'fullname': result[1],
            'username': result[2],
            'email': result[3],
        }
        return render_template(("feed.html"))
        
        
    
    return make_response(render_template('signup.html'))

@app.route("/api/follow", methods=["POST"])
@login_required
def follow_user():

    viewer_id = session["user"]["student_id"]

    data = request.get_json()
    target_id = data.get("user_id")

    if viewer_id == target_id:
        return jsonify({"error":"Cannot follow yourself"}),400

    result = toggle_follow(viewer_id,target_id)

    if not result:
        return jsonify({"error":"database error"}),500

    return jsonify(result)
@app.route('/create-post', methods=['POST'])
@login_required
def create_post_route():
    try:
        user = session.get('user')
        user_id = user.get('student_id')

        if 'image' not in request.files:
            return jsonify({"success": False, "error": "No image provided"}), 400

        file = request.files['image']

        if not file or not allowed_file(file.filename):
            return jsonify({"success": False, "error": "Invalid image"}), 400

        upload_result = cloudinary.uploader.upload(file)

        image_url = upload_result["secure_url"]

        caption = request.form.get('caption', '')

        post = create_post(user_id, caption, image_url)

        if not post:
            return jsonify({"success": False, "error": "Post creation failed"}), 500

        return jsonify({"success": True, "image_url": image_url})

    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": "Internal server error"}), 500
    

@app.route('/publish-project', methods=['POST'])
@login_required
def publish_project_route():
    try:
        user = session.get('user')
        user_id = user.get('student_id')

        data = request.get_json()

        title = data.get('title')
        description = data.get('description')
        github_url = data.get('github_url')
        demo_url = data.get('demo_url')
        visibility = data.get('visibility', 'Public')

        if not title:
            return jsonify({"success": False, "error": "Title required"}), 400

        project = create_project(user_id, title, description, github_url, demo_url, visibility)

        if not project:
            return jsonify({"success": False, "error": "Project creation failed"}), 500

        return jsonify({"success": True})

    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": "Internal server error"}), 500
    

@app.route('/edit-bio', methods=['POST'])
@login_required
def edit_bio_route():
    try:
        user = session.get('user')
        user_id = user.get('student_id')
        bio_text = request.form.get('bio') or ''
        ok = update_bio(user_id, bio_text)
        if not ok:
            return render_template('profile.html', active_page='profile', error='Could not update bio'), 500

        # Update session copy
        session['user']['bio'] = bio_text
        return redirect(url_for('ProfilePage'))
    except Exception:
        return render_template('profile.html', active_page='profile', error='Internal server error'), 500





@app.route("/api/feed")
@login_required
def api_feed():


    posts = get_feed_posts(session['user'].get('student_id'))
    print(posts )
    return jsonify({
        "posts": posts
    })




@app.route("/api/post/like", methods=["POST"])
def like_post():

    user_id = session['user'].get('student_id')

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    post_id = data.get("post_id")

    result = toggle_post_like(user_id, post_id)

    if not result:
        return jsonify({"error": "Database error"}), 500

    return jsonify(result)



@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def profile_edit():

    user_id = session["user"]["student_id"]

    if request.method == "POST":

        bio = request.form.get("bio")
        dob = request.form.get("dob")
        institution = request.form.get("institution")
        location = request.form.get("location")

        skills = request.form.getlist("skills")
        file = request.files.get("profile_pic")

        # validation
        if not bio or not dob or not institution or not location:

            user = get_user_profile(user_id)
            skills_all = get_all_skills()
            user_skills = get_user_skills(user_id)

            return render_template(
                "edit_profile.html",
                user=user,
                skills=skills_all,
                user_skills=user_skills,
                error="Please fill all the details before saving."
            )

        # default profile picture
        profile = get_user_profile(user_id)
        profile_pic = profile[4]

        # upload new picture if provided
        if file and file.filename != "":

            if not allowed_file(file.filename):
                user = get_user_profile(user_id)
                skills_all = get_all_skills()
                user_skills = get_user_skills(user_id)

                return render_template(
                    "edit_profile.html",
                    user=user,
                    skills=skills_all,
                    user_skills=user_skills,
                    error="Invalid image format."
                )

            upload_result = cloudinary.uploader.upload(
                file,
                folder="skillnet/profile_pictures"
            )

            profile_pic = upload_result["secure_url"]

        # update profile
        update_profile(
            user_id,
            bio,
            dob,
            institution,
            location,
            profile_pic
        )

        # update skills
        update_user_skills(user_id, skills)

        # update session
        session["user"]["profileUrl"] = profile_pic
        session["user"]["bio"] = bio

        return redirect(url_for("profile", username=session["user"]["username"]))

    # GET request
    user = get_user_profile(user_id)
    skills = get_all_skills()
    user_skills = get_user_skills(user_id)

    return render_template(
        "edit_profile.html",
        user=user,
        skills=skills,
        user_skills=user_skills
    )


@app.route("/api/search")
@login_required
def api_search():

    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"results": []})

    rows = search_students(query)

    results = []

    for r in rows:
        results.append({
            "student_id": r[0],
            "full_name": r[1],
            "username": r[2],
            "avatar": r[3],
            "institution": r[4],
            "location": r[5],
            "skills": r[6] or ""
        })

    return jsonify({"results": results})



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)




