from flask import Flask, request, redirect, render_template, session, flash
import cgi
import os
import jinja2

from flask_sqlalchemy import SQLAlchemy

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:cheese@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = 'QAkD6McykLGW5y9d'

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, body, owner):
        self.name = name
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship('Post', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


def check_for_space(astring):
    if len(astring) == 0:
        return True
    else:
        return False

@app.before_request
def require_login():
    allowed_routes = ['login','register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

#@app.route('/')
#def index():
#    template = jinja_env.get_template('index.html')
#    return template.render()

@app.route('/blog')
def blog():
    if request.method == 'GET':  
        owner_id = int(request.args.get('user'))
        owner = User.query.get(owner_id)
        owner_email = User.query.filter_by(email=owner.email).first()
        posts = Post.query.order_by(Post.id.desc()).filter_by(owner=owner_email).all() #.filter_by(owner=owner)
        return render_template('blog.html', posts=posts)

    owner = User.query.all() 
    posts = Post.query.order_by(Post.id.desc()).all() #.filter_by(owner=owner)
    #template = jinja_env.get_template('blog.html')
    return render_template('blog.html', posts=posts)

###
@app.route('/blogselecteduser')  #userblogs #########post.owner.email, owner = User.que...filter_by
def blogselecteduser():
    
    owner = User.query.filter_by(email=session['email']).first() #
    posts = Post.query.order_by(Post.id.desc()).filter_by(owner=owner).all() #.filter_by(owner=owner)
    #template = jinja_env.get_template('blog.html')
    return render_template('blog.html', posts=posts)

###
@app.route('/allusers')
def allusers():
    owners = User.query.all()
    return render_template('allusers.html', owners=owners)

@app.route('/userblogs')
def userblogs():
    owner = User.query.filter_by(email=session['email']).first() #
    posts = Post.query.order_by(Post.id.desc()).filter_by(owner=owner).all() #.filter_by(owner=owner)
    #template = jinja_env.get_template('blog.html')
    return render_template('blog.html', posts=posts)


@app.route('/addpost', methods=['POST', 'GET'])
def a_post():

    if request.method == 'POST':
        post_name = request.form['a_post'] #name= from .html
        post_body = request.form['a_body']
        owner = User.query.filter_by(email=session['email']).first()
        post_error = ""

        if check_for_space(post_name) or check_for_space(post_body) or post_name.isspace() or post_body.isspace():
            post_error = "Please no posts that are empty or only spaces."
            #template = jinja_env.get_template('addpost.html') 
            #return template.render(post_name=post_name, post_body=post_body, post_error = post_error)
            return render_template('addpost.html', post_name=post_name, post_body=post_body, post_error = post_error)

        else:
            #posts.append(post) #using list b4 sqlalchemy
            new_post = Post(post_name, post_body, owner)#### next argument?(post_name, post_body)
            db.session.add(new_post)
            db.session.commit()

            #template = jinja_env.get_template('viewblog2.html')
            #return template.render(post_name=post_name, post_body=post_body)
            return render_template('viewblog2.html', post_name=post_name, post_body=post_body)


    posts = Post.query.all()

    #b4jinja#return render_template('addpost.html', title ="A POST", posts=posts)
       
    #template = jinja_env.get_template('addpost.html') 
    #return template.render(posts=posts) #variables auto ="", no need to set-up

    return render_template('addpost.html', posts=posts)


@app.route('/delete-post', methods=["POST"])
def delete_post():

    post_id = int(request.form['post-id'])
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit() 

    return redirect('/blog') 

@app.route('/view-post', methods=['POST', 'GET'])
def view_post():
    
    post_id = int(request.args.get('post-ideal'))
    post = Post.query.get(post_id)

    #template = jinja_env.get_template('viewblog.html')
    #return template.render(post=post)
    return render_template('viewblog.html', post=post)


#    

##

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            #TODO - "remember" that user has logged in
            session['email'] = email
            flash("Logged in")
            return redirect('/blog')
        else:
            #TODO - explain why login failed
            flash("User password incorrect, or user does not exist", "error")
            #return redirect('/login')

    return render_template('login.html')

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        
        #TODO - validate email and password

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            #TODO - "remember" the user
            session['email'] = email
            return redirect('/blog')
        else:
            #TODO - user better response messaging
            return '<h1>Duplicate user!</h1>'

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()
