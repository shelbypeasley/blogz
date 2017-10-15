from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['GET', 'POST'])
def blogz():
    id = request.args.get("id")
    go = False
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
        lonepost = Blog(body=body, title=title)
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

@app.route('/', methods=['GET', 'POST'])
def index():

    return redirect('/blog')


app.secret_key = 'poop'

if __name__ == "__main__":
    app.run()
        