
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from supply import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

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

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    #Set roles when user registers
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        #Use email to determine the type of roles that would be set
        if self.role is None:
            if self.email == 'storesghaksi21@gmail.com':
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    #Role verification
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)


    #Create methods that allows to create tokens
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        #Create_token
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    ##Create a method that verifies token
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser



#Define Roles for User
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(150), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    #Set permissions column to 0 when no value is added
    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    #Methods to manage role permissions
    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self):
        self.permissions = 0
    
    def has_permission(self, perm):
        return self.permissions & perm == perm
    
    #Method to add roles to the Class(Role)
    @staticmethod
    def insert_roles():
        roles = {
            'User' : [Permission.UPDATE],
            'Administrator' : [Permission.UPDATE, Permission.DELETE, Permission.ADMIN] 
        }

        default_role = 'User'
        for r in roles:
            #Search for a role in the Roles table
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permission()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return f"Role('{self.name}')"  
        
#Define Permission Constants
class Permission:
    UPDATE = 1
    DELETE = 2
    ADMIN = 4
    

class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descr = db.Column(db.String(150), nullable=False)
    card = db.Column(db.String(150), nullable=False)
    date = db.Column(db.Date, nullable=False)
    usrv = db.Column(db.String(150))
    fr_om = db.Column(db.String(150))
    inp_ut = db.Column(db.String(150))
    curr_balance = db.Column(db.String(150), nullable=False)
    unit = db.Column(db.Integer)
    price = db.Column(db.Numeric(10,2))
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
    avail_balance = db.Column(db.String(150), nullable=False, default=0)
    curr_balance = db.Column(db.String(150), nullable=False, default=0)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))

    def __repr__(self):
        return f"SentItems('{self.descr}', '{self.date}', '{self.requisit}')"

class AllTrans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descr = db.Column(db.String(150)) 
    card = db.Column(db.String(150))
    date = db.Column(db.Date)
    usrv = db.Column(db.String(150))
    requisit = db.Column(db.String(150))
    fr_om = db.Column(db.String(150))
    t_o = db.Column(db.String(150))
    inp_ut = db.Column(db.String(150))
    out_put = db.Column(db.String(150))
    curr_balance = db.Column(db.String(150))
    bal = db.Column(db.String(150)) 
    unit = db.Column(db.Integer)
    price = db.Column(db.Numeric(10,2))
    

    def __repr__(self):
        return f"AllTrans('{self.descr}', '{self.date}', '{self.card}', '{self.curr_balance}')"
