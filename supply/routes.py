import secrets
import os
from PIL import Image
from supply.models import User, Items, SentItems
from flask import render_template, url_for, redirect, flash, request
from supply import app, bcrypt, db, mail 
from flask_mail import Message
from supply.forms import RegistrationForm, LoginForm, AddItemsForm, SendItemsForm, RequestResetForm, PasswordResetForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/", methods=['GET', 'POST'])
def home():  
    if current_user.is_authenticated:
        return redirect(url_for('add_item'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please Try Again', 'danger')
    return render_template('login.html', form=form, title="Login")


@app.route("/add_item", methods=['GET','POST'])
@login_required
def add_item():
    form = AddItemsForm()
    if form.validate_on_submit():
        #Get values form add_items form
        descr = form.descr.data
        card = form.card.data
        date = form.date.data
        usrv = form.usrv.data
        fr_om = form.fr_om.data
        inp_ut = form.inp_ut.data
        balance = form.balance.data
        cedis = form.cedis.data
        pesewas = form.pesewas.data

        items = Items(descr=descr, card=card, date=date, usrv=usrv, fr_om=fr_om, inp_ut=inp_ut, 
                        curr_balance=balance, cedis=cedis, pesewas=pesewas)
        db.session.add(items)
        db.session.commit()
        flash("New Items added successfully!", "success")
        return redirect(url_for('add_item'))
    return render_template("add_item.html", form=form, title="Add Items")

@app.route("/send_item/<int:item_id>/req", methods=['GET', 'POST'])
@login_required
def send_item(item_id):
    item = Items.query.get_or_404(item_id)
    form = SendItemsForm()

    if form.validate_on_submit():
        descr = form.descr.data
        card = form.card.data
        date = form.date.data
        requisit = form.requisit.data
        t_o = form.t_o.data
        out_put = form.out_put.data
        balance = form.balance.data
        avail_bal = request.form.get('balan')

        sent_item = SentItems(descr=descr, card=card, date=date, requisit=requisit, 
                                t_o=t_o, out_put=out_put, avail_balance=avail_bal, curr_balance=balance, item_id=item.id)

        db.session.add(sent_item)
        Items.query.filter_by(card=item.card).update(dict(curr_balance=balance))
        db.session.commit()
        flash('Items submitted successfully!', 'success')
        return redirect(url_for('send_item', item_id=item.id))
    return render_template("send_item.html", form=form, item=item, title="Send Items")

@app.route("/restock/<int:item_id>/orders", methods=['GET','POST'])
@login_required
def restock(item_id):
    item = Items.query.get_or_404(item_id)

    form = AddItemsForm()
    if form.validate_on_submit():
        descr = form.descr.data
        card = form.card.data
        date = form.date.data
        usrv = form.usrv.data
        fr_om = form.fr_om.data
        inp_ut = form.inp_ut.data
        curr_balance = form.balance.data
        cedis = form.cedis.data
        pesewas = form.pesewas.data

        items = Items(descr=descr, card=card, date=date, usrv=usrv, fr_om=fr_om, inp_ut=inp_ut, 
                        curr_balance=curr_balance, cedis=cedis, pesewas=pesewas)

        db.session.add(items)
        
        search = SentItems.query.filter_by(card=card).first()
        
        print(search)
        if search is None:
            Items.query.filter_by(card=item.card).update(dict(curr_balance=curr_balance))
            db.session.commit()
            flash("Items added successfully!", "success")
            return redirect(url_for('add_item'))

        else:
            Items.query.filter_by(card=item.card).update(dict(curr_balance=curr_balance))
            c=db.session.query(SentItems).filter_by(card=card).order_by(SentItems.id.desc()).limit(1).first()
            c.curr_balance=curr_balance
            db.session.commit()
            flash("Items added successfully!", "success")
            return redirect(url_for('add_item'))
    return render_template("restock.html", form=form, item=item, title="Re-Stock")

@app.route("/view_items", methods=['GET', 'POST'])
@login_required
def view_items():
    items = Items.query.all()
    return render_template("view_items.html", items=items, title="View Items")

@app.route("/requisition_req", methods=['GET', 'POST'])
@login_required 
def requisition_req():

    sent_items = SentItems.query.all()
    return render_template("requisition.html", sent_items=sent_items, title="Requisitions")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('add_item'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title="Register")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('add_item'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please Try Again', 'danger')
    return render_template('login.html', form=form, title="Login")

#Function to save picture
def save_picture(form_picture):
    #Randomize name of picture file
    random_hex = secrets.token_hex(8)
    #Get extension of image submitted
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)

    #Resize Image before Save
    output_size = (195, 158)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    #Save to path
    i.save(picture_path)
    return picture_fn

@app.route('/account', methods=['GET', 'POST'])
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
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='images/'+ current_user.image_file)
    return render_template('account.html', title='Account Page', image_file=image_file, form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])

    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_password_request', token=token, _external=True)}

If you did not make this request then please ignore this email.
    '''
    mail.send(msg)


@app.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('add_item'))
    form = RequestResetForm()
    if form.validate_on_submit():
        #Get user by email and send mail message
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset password. Check Spam folder if not found in Inbox.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Request', form=form)


@app.route('/reset_password_request/<token>', methods=['GET','POST'])
def reset_password_request(token):
    if current_user.is_authenticated:
        return redirect(url_for('add_item'))

    user = User.verify_reset_token(token)
    #If user cannot be found(Invalid token or wxpired token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for('reset_request'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_pw
        db.session.commit()
        flash('Your Password has been updated! You are now able to log in.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form, title="Reset Password")


@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', title='404 Page not Found'), 404

@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', title='403 Access Forbidden'), 403

@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', title='500 Error'), 500




    