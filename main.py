from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:12345@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "dZk8^fI$vd)E"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(120))
    post_message = db.Column(db.String(240))
    #owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, message):
        self.post_title = title
        self.post_message = message
        #self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    #tasks = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/', methods=['GET'])
def index():

    #owner = User.query.filter_by(email=session['email']).first()

    posts = Blog.query.all()

    return render_template('blog.html', title="Build A Blog", posts=posts)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/')
        else:
            flash("User password incorrect or user does not exist", 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['email']
    return redirect('/login')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO Make sure the email, password and verify all checkout

        existing_user = User.query.filter_by(email=email).first()

        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            # TODO Tell user that user already exists
            return '<h1>Duplicate User</h1>'


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

    

if __name__ == '__main__':
    app.run()