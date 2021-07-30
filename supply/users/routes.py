from flask import render_template, url_for, redirect, flash, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from supply import db, bcrypt
from supply.users.forms import RequestResetForm, RegistrationForm, LoginForm, PasswordResetForm, UpdateAccountForm 
from supply.users.utils import save_picture, send_reset_email
from supply.models import User

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.add_item'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form, title="Register")

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.add_item'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('users.home'))
        else:
            flash('Login Unsuccessful. Please Try Again', 'danger')
    return render_template('login.html', form=form, title="Login")


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account has been updated successfully!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='images/'+ current_user.image_file)
    return render_template('account.html', title='Account Page', image_file=image_file, form=form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('users.add_item'))
    form = RequestResetForm()
    if form.validate_on_submit():
        #Get user by email and send mail message
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset password. Check Spam folder if not found in Inbox.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Request', form=form)


@users.route('/reset_password_request/<token>', methods=['GET','POST'])
def reset_password_request(token):
    if current_user.is_authenticated:
        return redirect(url_for('users.add_item'))

    user = User.verify_reset_token(token)
    #If user cannot be found(Invalid token or wxpired token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for('users.reset_request'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_pw
        db.session.commit()
        flash('Your Password has been updated! You are now able to log in.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_password.html', form=form, title="Reset Password")
