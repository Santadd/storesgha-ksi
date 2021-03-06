from supply.users.utils import admin_required
from flask import render_template, url_for, redirect, flash,request, Blueprint
from flask_login import current_user, login_user, login_required
from supply import bcrypt, db
from supply.users.forms import LoginForm
from supply.main.forms import AddItemsForm, SendItemsForm
from supply.models import User, AllTrans, Items, SentItems



main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
def home():  
    if current_user.is_authenticated:
        return redirect(url_for('main.add_item'))
    form = LoginForm()
    if form.validate_on_submit(): 
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please Try Again', 'danger')
    
    return render_template('login.html', form=form, title="Login")


@main.route("/add_item", methods=['GET','POST'])
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
        unit = form.unit.data
        price = form.price.data

        items = Items(descr=descr, card=card, date=date, usrv=usrv, fr_om=fr_om, inp_ut=inp_ut, 
                        curr_balance=balance, unit=unit, price=price)

        all_items = AllTrans(descr=descr, card=card, date=date, usrv=usrv, fr_om=fr_om, inp_ut=inp_ut, 
                        curr_balance=balance, bal=balance, unit=unit, price=price)

        db.session.add(items)
        db.session.add(all_items)
        db.session.commit()
        flash("New Items added successfully!", "success")
        return redirect(url_for('main.add_item'))
    
    return render_template("add_item.html", form=form, title="Add Items")

@main.route("/send_item/<int:item_id>/req", methods=['GET', 'POST'])
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
        
        all_items = AllTrans(descr=descr, card=card, date=date, requisit=requisit, 
                                t_o=t_o, out_put=out_put, curr_balance=balance)
        db.session.add(sent_item)
        db.session.add(all_items)
        Items.query.filter_by(card=item.card).update(dict(curr_balance=balance))
        AllTrans.query.filter_by(card=item.card).update(dict(bal=balance))
        db.session.commit()
        flash('Items submitted successfully!', 'success')
        return redirect(url_for('main.view_items'))
    
    return render_template("send_item.html", form=form, item=item, title="Send Items")

@main.route("/restock/<int:item_id>/orders", methods=['GET','POST'])
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
        unit = form.unit.data
        price = form.price.data

        items = Items(descr=descr, card=card, date=date, usrv=usrv, fr_om=fr_om, inp_ut=inp_ut, 
                        curr_balance=curr_balance, unit=unit, price=price)
        
        all_items = AllTrans(descr=descr, card=card, date=date, usrv=usrv, fr_om=fr_om, inp_ut=inp_ut, 
                        curr_balance=curr_balance, bal=curr_balance, unit=unit, price=price)

        db.session.add(items)
        db.session.add(all_items)
        search = SentItems.query.filter_by(card=card).first()
        
        print(search)
        if search is None:
            Items.query.filter_by(card=item.card).update(dict(curr_balance=curr_balance))
            AllTrans.query.filter_by(card=item.card).update(dict(bal=curr_balance))
            db.session.commit()
            flash("Items added successfully!", "success") 
            return redirect(url_for('main.view_items'))

        else:
            Items.query.filter_by(card=item.card).update(dict(curr_balance=curr_balance))
            AllTrans.query.filter_by(card=item.card).update(dict(bal=curr_balance))
            c=db.session.query(SentItems).filter_by(card=card).order_by(SentItems.id.desc()).limit(1).first()
            c.curr_balance=curr_balance
            db.session.commit()
            flash("Items added successfully!", "success")
            return redirect(url_for('main.view_items'))
    
    return render_template("restock.html", form=form, item=item, title="Re-Stock")

@main.route("/view_items", methods=['GET', 'POST'])
@login_required
def view_items():
    items = Items.query.all()
    
    return render_template("view_items.html", items=items, title="View Items")


@main.route("/all_trans", methods=['GET', 'POST'])
@login_required

def all_trans():

    items = AllTrans.query.all()
    
    return render_template("all_items.html", items=items, title="All Transactions")

#View transactions to perform operations
@main.route("/trans_operations", methods=['GET', 'POST'])
@login_required
@admin_required
def trans_operations():

    prod = Items.query.all()
    items = AllTrans.query.all()
    c=db.session.query(AllTrans).order_by(AllTrans.id.desc()).limit(1).first()
    return render_template("trans_operations.html", items=items, title="Transactions Operations")


@main.route('/delete_transaction/requisit/<int:prod_id>', methods=['POST'])
def delete_req_trans(prod_id):
    prod = AllTrans.query.get_or_404(prod_id)
    if request.method == 'POST':
        out_put = request.form.get('out_put')
        balance = request.form.get('bal')
        card = request.form.get('card')

        rem = int(balance) + int(out_put)

        db.session.delete(prod)
        Items.query.filter_by(card=prod.card).update(dict(curr_balance=rem))
        AllTrans.query.filter_by(card=prod.card).update(dict(bal=rem))
        c=db.session.query(SentItems).filter_by(card=card, requisit=prod.requisit).order_by(SentItems.id.desc()).limit(1).first()
        a=db.session.query(AllTrans).filter_by(card=card).order_by(AllTrans.id.desc()).limit(1).first()
        db.session.delete(c)
        a.curr_balance=rem
        last_trans=db.session.query(SentItems).filter_by(card=card).order_by(SentItems.id.desc()).limit(1).first()
        if last_trans:
            last_trans.curr_balance = rem
        db.session.commit()
        flash(f'The transaction on {prod.date} has been deleted successfully', 'success')
        return redirect(url_for('main.trans_operations'))
    flash(f'The transaction on {prod.date} cannot be deleted', 'warning')
    return redirect(url_for('main.trans_operations'))

@main.route('/delete_transaction/usrv/<int:prod_id>', methods=['POST'])
def delete_srv_trans(prod_id):
    
    prod = AllTrans.query.get_or_404(prod_id)

    if request.method == 'POST':
        inp_ut = request.form.get('inp_ut')
        balance = request.form.get('bal')
        card = request.form.get('card')

        rem = int(balance) - int(inp_ut)
        if rem >= 0:
            db.session.delete(prod)
            Items.query.filter_by(card=prod.card).update(dict(curr_balance=rem))
            AllTrans.query.filter_by(card=prod.card).update(dict(bal=rem))
            c=db.session.query(Items).filter_by(card=card, usrv=prod.usrv).order_by(Items.id.desc()).limit(1).first()
            a=db.session.query(AllTrans).filter_by(card=card).order_by(AllTrans.id.desc()).limit(1).first()
            db.session.delete(c)
            a.curr_balance=rem
            last_trans=db.session.query(SentItems).filter_by(card=card).order_by(SentItems.id.desc()).limit(1).first()
            if last_trans:
                last_trans.curr_balance = rem

            db.session.commit()
            flash(f'The transaction on {prod.date} has been deleted successfully', 'success')
            return redirect(url_for('main.trans_operations'))
        else:
            flash('The remaining balance cannot be negative! Check items again.', 'danger')
            return redirect(url_for('main.trans_operations'))
    flash(f'The transaction on {prod.date} cannot be deleted', 'warning')
    return redirect(url_for('main.trans_operations'))
       


@main.route("/requisition_req", methods=['GET', 'POST'])
@login_required 
def requisition_req():

    sent_items = SentItems.query.all()
    
    return render_template("requisition.html", sent_items=sent_items, title="Requisitions")
