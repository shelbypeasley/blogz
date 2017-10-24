from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/blog', methods=['GET', 'POST'])
def blogz():
    id = request.args.get("id")
    user = request.args.get("user")
    go = False
    if user:
        users = Blog.query.filter_by(owner_id = user).all()
        return render_template ('blog.html', blog=users)
    if id:
        go = Blog.query.filter_by(id = id)[0]

        return render_template('lonepost.html', go=go)

    blog = Blog.query.all()
    return render_template('blog.html', blog=blog)



@app.route('/newpost', methods=['GET', 'POST'])
def new_post():
    error1 = ""
    error2 = ""
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['user']).first()
        lonepost = Blog(body=body, title=title, owner=owner)
        db.session.add(lonepost)
        db.session.commit()
        id = lonepost.id
        if title == "":
            error1 = "You have to have a title"
        if body == "":
            error2 = "You need some body"
        if error1 or error2:
            return render_template('newpost.html', title=title, body=body, error1=error1, error2=error2)
        
        return redirect("/blog?id=" + str(id))

    else:
        return render_template('newpost.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user'] = user.username
            flash('Welcome back, ' + user.username)
            return redirect("/newpost")
        
        else:
            flash('bad username or password')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if username == "":
            flash('You need to add a username')
        if password == "":
            flash('You need to add a password')
        if verify == "":
            flash('You need to verify passwords')
            return redirect('/signup')
        if len(username) < 3:
            flash('Username is not valid')
        if len(password) < 3:
            flash('Password is not valid')
            return redirect('/signup')
        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            flash(username + 'is already taken')
            return redirect('/signup')
        if password != verify:
            flash('passwords did not match')
            return redirect('/signup')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return redirect("/newpost")
    else:
        return render_template('signup.html')

@app.route("/logout")
def logout():
    del session['user']
    flash('You have logged out')
    return redirect("/login")

@app.route('/', methods=['GET', 'POST'])
def index():
    id = request.args.get("id")
    go = False
    if id:
        go = User.query.filter_by(id = id)[0]

        return render_template('index.html', go=go)

    users = User.query.all()
    return render_template('index.html', users=users)

endpoints_without_login = ['login', 'signup', 'blogz', 'index']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/login")


app.secret_key = 'poop'

if __name__ == "__main__":
    app.run()
        