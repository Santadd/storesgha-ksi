from supply.models import User, Items, SentItems
from flask import render_template, url_for, redirect, flash, request
from supply import app, bcrypt, db, mail 
from flask_mail import Message
from supply.forms import RegistrationForm, LoginForm, AddItemsForm, SendItemsForm, RequestResetForm, PasswordResetForm
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@login_required
def home():  
    form = AddItemsForm()
    return render_template("add_item.html", form=form, title="Add Items")



@app.route("/add_item", methods=['GET','POST'])
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
                        avail_balance=balance, curr_balance=balance, cedis=cedis, pesewas=pesewas)
        db.session.add(items)
        db.session.commit()
        flash("New Items added successfully!", "success")
        return redirect(url_for('add_item'))
    return render_template("add_item.html", form=form, title="Add Items")

@app.route("/send_item/<int:item_id>/req", methods=['GET', 'POST'])
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
                        avail_balance=curr_balance, curr_balance=curr_balance, cedis=cedis, pesewas=pesewas)

        db.session.add(items)
        search = SentItems.query.filter_by(card=card).first()
        print(search)
        if search is None:
            db.session.commit()
            flash("Items added successfully!", "success")
            return redirect(url_for('add_item'))
        else:
            Items.query.filter_by(card=item.card).update(dict(curr_balance=curr_balance))
            c=db.session.query(SentItems).filter_by(card=card).order_by(SentItems.id.desc()).limit(1).first()
            c.curr_balance=curr_balance
            db.session.commit()
            flash("Items added successfully!", "success")
            flash(search, 'success')
            return redirect(url_for('add_item'))
    return render_template("restock.html", form=form, item=item, title="Re-Stock")

@app.route("/view_items")
def view_items():
    items = Items.query.all()
    return render_template("view_items.html", items=items, title="View Items")

@app.route("/requisition_req") 
def requisition_req():

    sent_items = SentItems.query.all()
    c=db.session.query(SentItems).filter_by(card='YU98E').order_by(SentItems.id.desc()).limit(1).first()
    flash(c.curr_balance, 'success')
    return render_template("requisition.html", sent_items=sent_items, title="Requisitions")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('send_item'))
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
        return redirect(url_for('home'))
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
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        #Get user by email and send mail message
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Request', form=form)


@app.route('/reset_password_request/<token>', methods=['GET','POST'])
def reset_password_request(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

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



    