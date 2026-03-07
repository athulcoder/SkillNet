from flask import Flask, request, render_template, make_response, jsonify, session, url_for, redirect, flash
from functools import wraps
import os
import uuid
from werkzeug.utils import secure_filename
import cloudinary_config
from queries.student_queries import create_student, check_student, get_user_by_id, update_bio, get_followers_count, get_following_count
from queries.post_queries import create_post, get_posts_by_user, count_posts_by_user,get_feed_posts,toggle_post_like
from queries.project_queries import create_project, get_projects_by_user, count_projects_by_user
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


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@app.route("/profile/edit", methods=["GET","POST"])
@login_required
def edit_profile():

    user = session.get("user")

    if request.method == "POST":

        bio = request.form.get("bio")

        update_bio(user["student_id"], bio)


        return redirect(url_for("profile"))

    return render_template("profile_edit.html")


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
    user_id = session['user'].get('student_id')
    row = get_user_by_id(user_id=user_id)
    myuser = {
    "student_id": row[0],
    "fullname": row[1],
    "username": row[2],
    "email": row[3],
    "password": row[4],
    "profile_url": row[5],
    "bio": row[6],
    "college": row[7],
    "location": row[8],
    "skills": row[9],
    "created_at": row[10]
}
    print(myuser)
    
    post_count = count_posts_by_user(user_id)
    project_count = count_projects_by_user(user_id)
    followers_count = get_followers_count(user_id)
    following_count = get_following_count(user_id)

    posts = get_posts_by_user(user_id)
    projects = get_projects_by_user(user_id)

    return jsonify({
        "user":myuser,
        "post_count": post_count,
        "project_count": project_count,
        "followers_count": followers_count,
        "following_count": following_count,
        "posts": posts,
        "projects": projects
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
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)




