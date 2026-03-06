from flask import Flask, request, render_template, make_response, jsonify, session, url_for, redirect, flash
from functools import wraps
import os
import uuid
from werkzeug.utils import secure_filename
import cloudinary_config
from queries.student_queries import create_student, check_student, get_user_by_id, update_bio, get_followers_count, get_following_count
from queries.post_queries import create_post, get_posts_by_user, count_posts_by_user
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




@app.route("/profile", methods=["POST", "GET"])
@login_required
def ProfilePage():
    try:
        user = session.get('user')
        user_id = user.get('id') if user else None

        post_count = count_posts_by_user(user_id)
        project_count = count_projects_by_user(user_id)
        followers_count = get_followers_count(user_id)
        following_count = get_following_count(user_id)

        posts = get_posts_by_user(user_id)
        projects = get_projects_by_user(user_id)

        return make_response(
            render_template(
                'profile.html',
                active_page='profile',
                post_count=post_count,
                project_count=project_count,
                followers_count=followers_count,
                following_count=following_count,
                posts=posts,
                projects=projects,
            )
        ), 200
    except Exception as e:
        return make_response(render_template('profile.html', active_page='profile', error='Could not load profile')), 500

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
            'id': user[0],
            'fullname': user[1],
            'username': user[2],
            'email': user[3],
            'profileUrl': user[5] if len(user) > 5 else None,
            'bio': user[6] if len(user) > 6 else None,
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
                return render_template("signup.html", error="All feilds are required"),401

        
        result = create_student(full_name, username, email, password)

        if not result:
            return render_template("signup.html", error="User already exists"), 401

        # result is the created user row
        session["user"] = {
            'id': result[0],
            'fullname': result[1],
            'username': result[2],
            'email': result[3],
        }
        return redirect(url_for("feedPage")), 200
        
        
    
    return make_response(render_template('/signup.html'))


@app.route('/create-post', methods=['POST'])
@login_required
def create_post_route():
    try:
        user = session.get('user')
        user_id = user.get('id')

        if 'image' not in request.files:
            return render_template('profile.html',
                                   active_page='profile',
                                   error='No image provided'), 400

        file = request.files['image']

        if file and allowed_file(file.filename):

            upload_result = cloudinary.uploader.upload(file)

            image_url = upload_result["secure_url"]

        else:
            return render_template('profile.html',
                                   active_page='profile',
                                   error='Invalid image'), 400

        caption = request.form.get('caption') or ''

        post = create_post(user_id, caption, image_url)

        if not post:
            return render_template('profile.html',
                                   active_page='profile',
                                   error='Could not create post'), 500

        return redirect(url_for('ProfilePage'))

    except Exception as e:
        print(e)
        return render_template('profile.html',
                               active_page='profile',
                               error='Internal server error'), 500

@app.route('/publish-project', methods=['POST'])
@login_required
def publish_project_route():
    try:
        user = session.get('user')
        user_id = user.get('id')
        title = request.form.get('title')
        description = request.form.get('description')
        github_url = request.form.get('github_url') or None
        demo_url = request.form.get('demo_url') or None
        visibility = request.form.get('visibility') or 'Public'

        if not title:
            return render_template('profile.html', active_page='profile', error='Title required'), 400

        project = create_project(user_id, title, description, github_url, demo_url, visibility)
        if not project:
            return render_template('profile.html', active_page='profile', error='Could not create project'), 500

        return redirect(url_for('ProfilePage'))
    except Exception:
        return render_template('profile.html', active_page='profile', error='Internal server error'), 500


@app.route('/edit-bio', methods=['POST'])
@login_required
def edit_bio_route():
    try:
        user = session.get('user')
        user_id = user.get('id')
        bio_text = request.form.get('bio') or ''
        ok = update_bio(user_id, bio_text)
        if not ok:
            return render_template('profile.html', active_page='profile', error='Could not update bio'), 500

        # Update session copy
        session['user']['bio'] = bio_text
        return redirect(url_for('ProfilePage'))
    except Exception:
        return render_template('profile.html', active_page='profile', error='Internal server error'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

