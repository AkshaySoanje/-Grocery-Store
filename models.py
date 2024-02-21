from flask_sqlalchemy import SQLAlchemy
from database import db


user_cart_products = db.Table('user_cart_products',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('quantity', db.Integer, nullable = False, default = 1)
)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    address = db.Column(db.String, nullable=False)
    mobile = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String, nullable=False)
    first_order = db.Column(db.Boolean, default=True)


    cart = db.relationship('Cart', uselist=False, back_populates='user', cascade="all, delete-orphan")


    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.cart = Cart()

    def __repr__(self):
        return f'<User {self.username}>'

class Cart(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


     user = db.relationship('User', back_populates='cart')

     cart_products = db.relationship('Product', secondary=user_cart_products, lazy='subquery',
                                     backref=db.backref('carts', lazy=True),
                                     primaryjoin='Cart.id == user_cart_products.c.user_id',
                                     secondaryjoin='Product.id == user_cart_products.c.product_id')

     def __repr__(self):
        return f'<Cart {self.id}>'
class Manager(db.Model):
    __tablename__ = 'manager'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    managername = db.Column(db.String, unique = True, nullable = False)
    store = db.Column(db.String, nullable = False)

    password = db.Column(db.String, nullable = False)

class Section(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(100), nullable = False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(100), nullable = False)
    price = db.Column(db.Integer, nullable = False)
    stock = db.Column(db.Integer, nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    manager_id = db.Column(db.Integer, db.ForeignKey('manager.id')) 
    quantity = db.Column(db.Integer, nullable=False, default=1)
    description = db.Column(db.String(500), nullable =True) 
    frequency = db.Column(db.Integer, default=0)

    section = db.relationship('Section', backref = db.backref('product', lazy = True))
    manager = db.relationship('Manager', backref=db.backref('products', lazy=True))  

