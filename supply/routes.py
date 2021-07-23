from re import T
from flask.globals import request
from wtforms.validators import URL
from supply.models import User, Items, SentItems
from flask import render_template, url_for, redirect, flash
from supply import app, bcrypt, db
from supply.forms import RegistrationForm, LoginForm, AddItemsForm, SendItemsForm
from flask_login import login_user, current_user, logout_user


@app.route("/")
def home():  
    form = AddItemsForm()
    return render_template("add_item.html", form=form)

@app.route("/send_item/<int:item_id>/req", methods=['GET', 'POST'])
def send_item(item_id):
    item = Items.query.get_or_404(item_id)
    form = SendItemsForm(request.form)

    if form.validate_on_submit():
        descr = form.descr.data
        card = form.card.data
        date = form.date.data
        requisit = form.requisit.data
        t_o = form.t_o.data
        out_put = form.out_put.data
        balance = form.balance.data

        sent_item = SentItems(descr=descr, card=card, date=date, requisit=requisit, 
                                t_o=t_o, out_put=out_put, balance=balance, item_id=item.id)

        db.session.add(sent_item)
        item.balance = balance
        db.session.commit()
        flash('Items submitted successfully!', 'success')
        return redirect(url_for('view_items'))
    return render_template("send_item.html", form=form, item=item)

@app.route("/issue_item", methods=['POST'])
def issue_item():
    
    return render_template("view_items.html")

@app.route("/view_items")
def view_items():
    items = Items.query.all()
    return render_template("view_items.html", items=items)

@app.route("/requisition_req") 
def requisition_req():

    sent_items = SentItems.query.all()
    return render_template("requisition.html", sent_items=sent_items)

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
                        balance=balance, cedis=cedis, pesewas=pesewas)
        db.session.add(items)
        db.session.commit()
        flash("New Items added successfully!", "success")
        return redirect(url_for('add_item'))
    return render_template("add_item.html", form=form)

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
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please Try Again', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



    