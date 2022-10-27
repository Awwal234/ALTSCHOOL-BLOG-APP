from enum import unique
from os import abort
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '12448493sgdeyehjloiw09'

login_manager = LoginManager(app)
# login_manager.init_app(app)
# login_manager.login_view = 'login'
# login_manager._load_user()


@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))

# creating models for signup and login


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

# creating model for blog


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(1000))
    author = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Post %r>' % self.title

# route for home


@app.route('/')
def home():
    # view blogs of other users in home
    blogs = Post.query.all()
    return render_template('index.html', blogs=blogs)

# route for signup


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        user_exist = User.query.filter_by(
            name=name, email=email, password=password).first()
        if user_exist:
            flash('User already exist', 'error')
            return redirect(url_for('signup'))

        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

# route for login


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            login_user(user)
            flash('You were successfully logged in', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

# route for dashboard


@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    blogs = Post.query.all()
    return render_template('dashboard.html', blogs=blogs, user=user)


# route for create blog for a particular user

@app.route('/create/<int:id>', methods=['GET', 'POST'])
@login_required
def create(id):
    user = current_user
    blog = Post.query.all()
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = request.form.get('author')
        blog = Post(title=title, content=content, author=author)
        db.session.add(blog)
        db.session.commit()
        return redirect(url_for('dashboard'))

    # create blog only for the current user

    return render_template('createblog.html', user=user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# route for deleting a blog


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    user = current_user
    blog = Post.query.get_or_404(id)
    if blog.author == user.name:
        db.session.delete(blog)
        db.session.commit()
        return redirect(url_for('dashboard', id=id))
    else:
        return redirect(url_for('dashboard'))


# route for updating a blog
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    blog = Post.query.get_or_404(id)
    user = current_user
    if request.method == 'POST':
        blog.title = request.form.get('title')
        blog.content = request.form.get('content')
        db.session.commit()
        return redirect(url_for('dashboard'))

    # update blog only for the correct current user
    if blog.author != user.name:
        return redirect(url_for('dashboard'))
    if blog.author == user.name:
        return render_template('update.html', blog=blog, user=user)


if __name__ == '__main__':
    app.run(debug=True)
