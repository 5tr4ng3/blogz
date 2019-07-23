from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:1234@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "dZk8^fI$vd)E"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(120))
    post_message = db.Column(db.String(240))
    user = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, message):
        self.post_title = title
        self.post_message = message
        self.user = user


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship('Blog', backref='user')

    def __init__(self, username, password, posts):
        self.username = username
        self.password = password
        self.posts = posts


@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['GET'])
def index():

    users = User.query.all()

    return render_template('users.html', title="Build A Blog", users=users)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash("User password incorrect or user does not exist", 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if not username or not password:
            flash("Must enter a username and password")
            return render_template('register.html')
        elif password != verify:
            flash("Passwords did not match")
            return render_template('register.html')

        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            flash("User already exists", "error")
            return render_template('register.html')


    return render_template('register.html')


@app.route('/blog', methods=['GET'])
def blog():
    
    posts = Blog.query.all()

    return render_template('blog.html', posts=posts)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    
    if request.method == 'POST':
        post_title = request.form['post_title']
        post_message = request.form['post_message']
        if post_title and post_message:
            new_post = Blog(post_title, post_message)
            db.session.add(new_post)
            db.session.commit()
            return render_template('post_entry.html', post=new_post)
        else:
            flash("Post must have a title and message", "error")
            return render_template('newpost.html', post_title=post_title, post_message=post_message)

    return render_template('newpost.html')


@app.route('/post_entry')
def post_entry():

    post_id = request.args.get('post')
    post = Blog.query.filter_by(id=post_id).first()
    
    return render_template('post_entry.html', post=post)


@app.route('/user_posts')
def user_posts():

    username = request.args.get('user')
    user = User.query.filter_by(username=username).first()
    posts = Blog.query.filter_by(user=user).all()

    return render_template('user_posts.html', posts=posts)
    


if __name__ == '__main__':
    app.run()