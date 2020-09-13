from flask import render_template, url_for, redirect, flash, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskwebapp.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                     RequestPasswordResetForm, PasswordResetForm)
from flaskwebapp import db, bcrypt
from flaskwebapp.models import User, Post
from flaskwebapp.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)
home = 'main.home'
login = 'users.login'


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(home))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        # app.logger.info('passed')
        return redirect(url_for(login))
    return render_template('register.html', title='register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(home))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for(home))
        else:
            flash('login failed, check email and password', 'danger')
    return render_template('login.html', title='login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for(home))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    print(current_user.username)
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # update profile pic
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('updated', 'success')
        # post/get redirect pattern
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='account', image_file=image_file, form=form)


@users.route("/user/<string:username>")
def get_user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)

    return render_template('user_post.html', posts=posts, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for(home))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('email sent', 'success')
        return redirect(url_for(login))
    return render_template('reset_request.html', title="reset password", form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for(home))
    user = User.verify_reset_token(token)
    if not user:
        flash('invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed
        db.session.commit()
        db.session.commit()
        flash('password updated', 'success')
        return redirect(url_for(login))
        # app.logger.info('passed')
    return render_template('reset_token.html', title="enter new password", form=form)
