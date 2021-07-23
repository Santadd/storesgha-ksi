from sqlalchemy.orm import backref
from supply import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    image_file = db.Column(db.String(50), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descr = db.Column(db.String(150), nullable=False)
    card = db.Column(db.String(150), nullable=False)
    date = db.Column(db.Date, nullable=False)
    usrv = db.Column(db.String(150))
    fr_om = db.Column(db.String(150))
    inp_ut = db.Column(db.String(150))
    balance = db.Column(db.String(150), nullable=False)
    cedis = db.Column(db.String(150))
    pesewas = db.Column(db.String(150))
    issued = db.relationship('SentItems', backref='sent_items', lazy=True)

    def __repr__(self):
        return f"Items('{self.descr}', '{self.date}', '{self.usrv}')"

class SentItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descr = db.Column(db.String(150), nullable=False)
    card = db.Column(db.String(150), nullable=False)
    date = db.Column(db.Date, nullable=False)
    requisit = db.Column(db.String(150))
    t_o = db.Column(db.String(150))
    out_put = db.Column(db.String(150))
    balance = db.Column(db.String(150), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))

    def __repr__(self):
        return f"SentItems('{self.descr}', '{self.date}', '{self.requisit}')"
