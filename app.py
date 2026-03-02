from flask import Flask, request,render_template,make_response


app = Flask(__name__)




@app.route("/login", methods=["POST", "GET"])
def login():
    
    if request.method=="POST":
        data = request.get_json()
        
        return data,200
    
    return make_response(render_template('/login.html'))

@app.route("/signup", methods=["POST", "GET"])
def signup():
    
    if request.method=="POST":
        data = request.get_json()
        print(data.get('name'))
        return data,200
    
    return make_response(render_template('/signup.html'))



app.run(debug=True, host="0.0.0.0", port=8000)

