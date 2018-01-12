from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'JPO(HF(HW#FP)FHP$RPJFP)@U#R#)R'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'mainblog'] 
    
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()
        if user is None:
            flash('Username is incorrect.', 'error') 
        if user and user.password != password:
            flash('Password is incorrect.', 'error')
        elif user and user.password == password:
            session['username'] = username
            flash("Logged in!")
            return redirect('/newpost')
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if username == "" or password == "" or verify == "":
            flash('Each field must be completed.', 'error')
            return redirect('signup')
        if password != verify:
            flash('Passwords must match.', 'error')
            return redirect('signup')
        if len(username) < 4 or len(password) < 4:
            flash("Invalid username or password.", "error")
            return redirect('signup')
        elif not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash("Duplicate user", 'error')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route("/", methods=['POST', 'GET'])
def index():
    users = User.query.all()
    userId = request.args.get("owner_id")
    userposts = Blog.query.filter_by(owner_id=userId).all()

    return render_template('index.html', users=users)

@app.route("/blog", methods=['POST', 'GET'])
def mainblog():

    posts = Blog.query.all()

    
    if request.method == "GET" and 'id' in request.args:
        blogid = request.args.get("id")
        blogpost = Blog.query.get(blogid)
        blogowner = Blog.query.get(blogpost.owner_id)
        owner = User.query.get(blogowner.owner_id)
        username = User.query.get(owner.username)
        return render_template('blog_post.html', blogpost=blogpost, owner=owner, username=username)
    elif request.method == 'GET' and 'user' in request.args:
        userid = request.args.get("user")
        userposts = Blog.query.filter_by(owner_id=userid).all()
        selecteduser = User.query.filter_by(id=userid).first()
        return render_template('singleUser.html', title="Blogz", userposts=userposts, selecteduser=selecteduser)
    else:
        for post in posts:
            postowner = Blog.query.get(post.owner_id)
            bpostowner = User.query.get(postowner.id)
            postusername = User.query.get(bpostowner.username)
            return render_template('blog.html', title="Blogz", posts=posts, postowner=postowner,
                 bpostowner=bpostowner, postusername=postusername)

@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_post = request.form['content']
        if blog_title != "" and blog_post != "":
            new_blog = Blog(blog_title, blog_post, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect ("/blog?id={0}".format(new_blog.id))
        else:
            flash('Both the title and body need to have content.', 'error')
    if owner == "":
        return redirect('/login')
    return render_template('newpost.html', title="New Post")

if __name__ == '__main__':
    app.run()