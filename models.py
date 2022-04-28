from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, login_manager, app
from flask_login import UserMixin
from sqlalchemy.orm import backref


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20),  nullable=False, default='Manager')
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    contact = db.Column(db.String(20), nullable = True)
    posts = db.relationship('Post', backref='author', lazy=True)

    upload = db.relationship('Verify', backref = 'upload', lazy = 'dynamic', foreign_keys = 'Verify.user_id')
    verify = db.relationship('Verify', backref = 'verify', lazy = 'dynamic', foreign_keys = 'Verify.user_id_confirm')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.contact}', '{self.role}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


storageCage_listing = db.Table('storagecage_listing',
    db.Column('storagecage_id', db.Integer, db.ForeignKey('storagecage.id'), primary_key=True),
    db.Column('listing_id', db.Integer, db.ForeignKey('listing.id'), primary_key=True)
)


class StorageCage(db.Model):
    __tablename__ = 'storagecage'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id') , nullable=False)
    location = db.relationship('Location', backref='locationStorage' , lazy=True)
    subscription = db.relationship('Listing', secondary=storageCage_listing, backref=db.backref('subscribers', lazy ='dynamic'))

    __table_args__ = (db.UniqueConstraint('name', 'location_id'),)

    def __repr__(self):
        return f"StorageCage('{self.name}','{self.location_id}')"  

class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key = True)
    numberAndStreet = db.Column(db.String(250), nullable=False)
    suburb = db.Column(db.String(50), nullable = False)
    postcode = db.Column(db.Integer, nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    area_loc = db.relationship('Area', backref='area_loc' , lazy=True)
    state_loc = db.relationship('State', backref='state_loc' , lazy=True)

    def __repr__(self):
        return f"Location('{self.numberAndStreet}','{self.suburb}','{self.postcode}','{self.state_id},'{self.area_id}')"  

class Area(db.Model):
    __tablename__ = 'area'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=False)
    

    def __repr__(self):
        return f"Area('{self.id}','{self.name}', '{self.state_id}')"

class State(db.Model):
    __tablename__ = 'state'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    area_state = db.relationship('Area', backref='area_state' , lazy=True)
    

    def __repr__(self):
        return f"State('{self.id}','{self.name}')"

class Listing(db.Model):
    __tablename__ = 'listing'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable =False)
    last_update = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    location = db.relationship('Location', backref='locationListing' , lazy=True)
    subscription = db.relationship('StorageCage', secondary=storageCage_listing, backref=db.backref('subscribers', lazy ='dynamic'))
    __table_args__ = (db.UniqueConstraint('name', 'location_id'),)

    def __repr__(self):
        return f"Listing('{self.name}','{self.location_id}',,'{self.last_update}')"  


class Product(db.Model):
    __tablename__='product'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), nullable = False)
    size = db.Column(db.String(50), nullable = False) 
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    subcategory = db.relationship('SubCategory', backref='subcategory' , lazy=True)
    comment = db.Column(db.Text, nullable=True)


    __table_args__ = (db.UniqueConstraint('name', 'size'),)

    def __repr__(self):
        return f"Product('{self.name}','{self.size}','{self.image_file}','{self.comment}')" 



class Category(db.Model):
    __tablename__='category'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    subcategory = db.relationship('SubCategory', backref='subcategory-parent' , lazy=True)


    def __repr__(self):
        return f"Category('{self.id}','{self.name}')" 


class SubCategory(db.Model):
    __tablename__='subcategory'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    products = db.relationship('Product', backref='productCategory', lazy=True)
    category = db.relationship('Category', backref='category' , lazy=True)

    def __repr__(self):
        return f"Category('{self.id}','{self.name}')" 


class Supplier(db.Model):
    __tablename__='supplier'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable =False)
    contact = db.Column(db.String(20), nullable = True)
    website = db.Column(db.String(250), nullable = True)
    location = db.relationship('Location', backref='locationSupplier' , lazy=True)

    def __repr__(self):
        return f"Supplier('{self.name}','{self.location_id}','{self.contact}','{self.website}')" 

class Product_Storage(db.Model):
    __tablename__ = 'product_storage'
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable =False , primary_key = True)
    storage_id = db.Column(db.Integer, db.ForeignKey('storagecage.id'), nullable =False , primary_key = True)
    quantity = db.Column(db.Integer, default =0 , nullable=False)

    storage = db.relationship('StorageCage', backref='storageProduct' , lazy=True)
    product = db.relationship('Product', backref='productStorage' , lazy=True)

    def __repr__(self):
        return f"Product_Storage('{self.product_id}','{self.storage_id}','{self.quantity}')" 

class Product_Storage_Listing(db.Model):
    __tablename__ = 'product_storage_listing'
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable =False , primary_key = True)
    storage_id = db.Column(db.Integer, db.ForeignKey('storagecage.id'), nullable =False , primary_key = True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable =False , primary_key = True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable =True)
    orderentity = db.Column(db.String(50), nullable = True)
    per_booking = db.Column(db.Float, nullable = False, default=0)

    storage = db.relationship('StorageCage', backref='storagecage' , lazy=True)
    listing = db.relationship('Listing', backref='listing' , lazy=True)
    product = db.relationship('Product', backref='product' , lazy=True)
    supplier = db.relationship('Supplier', backref='supplier' , lazy=True)

    def __repr__(self):
        return f"Product_Storage_Listing('{self.product_id}','{self.storage_id}','{self.listing_id}','{self.supplier_id}','{self.orderentity}','{self.per_booking}')" 

class Verify(db.Model):
    __tablename__ = 'verify'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable =False )
    title = db.Column(db.String(50), nullable = False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comment=db.Column(db.Text, nullable=False)
    user_id_confirm =db.Column(db.Integer, db.ForeignKey('user.id'), nullable =True )
    date_verified=db.Column(db.DateTime, nullable=True)
        
    
    def __repr__(self):
        return f"('{self.id}','{self.user_id}','{self.title}, '{self.date_posted}','{self.comment}','{self.user_id_confirm}','{self.date_verified}')" 

class Verify_Product_Storage(db.Model):
    __tablename__ = 'verify_product_storage'
    verify_id = db.Column(db.Integer, db.ForeignKey('verify.id'), nullable =False , primary_key = True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable =False , primary_key = True)
    storage_id = db.Column(db.Integer, db.ForeignKey('storagecage.id'), nullable =False , primary_key = True)
    quantity = db.Column(db.Integer, default =0 , nullable=False)

    storage = db.relationship('StorageCage', backref='storageProductVerify' , lazy=True)
    product = db.relationship('Product', backref='productStorageVerify' , lazy=True)
    verify = db.relationship('Verify', backref='ProductStorageVerifyStocktake' , lazy=True)

    def __repr__(self):
        return f"Verfiy_Product_Storage('{self.verify_id}','{self.product_id}','{self.storage_id}','{self.quantity}')" 

class Verify_Product_Storage_Listing(db.Model):
    __tablename__ = 'verify_product_storage_listing'
    verify_id = db.Column(db.Integer, db.ForeignKey('verify.id'), nullable =False , primary_key = True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable =False , primary_key = True)
    storage_id = db.Column(db.Integer, db.ForeignKey('storagecage.id'), nullable =False , primary_key = True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable =False , primary_key = True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable =True)
    orderentity = db.Column(db.String(50), nullable = True)
    per_booking = db.Column(db.Float, nullable = False, default=0)

    storage = db.relationship('StorageCage', backref='storagecageVerify' , lazy=True)
    listing = db.relationship('Listing', backref='listingVerify' , lazy=True)
    product = db.relationship('Product', backref='productVerify' , lazy=True)
    supplier = db.relationship('Supplier', backref='supplierVerify' , lazy=True)
    verify = db.relationship('Verify', backref='VerifyStocktakePSL' , lazy=True)

    def __repr__(self):
        return f"Verfiy_Product_Storage_Listing('{self.verify_id}','{self.product_id}','{self.storage_id}','{self.listing_id}','{self.supplier_id}','{self.orderentity}','{self.per_booking}')" 

class Verify_Listing_Booking(db.Model):
    __tablename__ = 'verify_listing_booking'
    verify_id = db.Column(db.Integer, db.ForeignKey('verify.id'), nullable =False , primary_key = True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable =False , primary_key = True)
    booking = db.Column(db.Integer, nullable = False, default=0)

    listing = db.relationship('Listing', backref='listingVerifyBooking' , lazy=True)
    verify = db.relationship('Verify', backref='VerifyBooking' , lazy=True)

    def __repr__(self):
        return f"Verify_Listing_Booking('{self.verify_id}','{self.listing_id}','{self.booking}')" 



class Order_Product(db.Model):
    __tablename__ = 'order_product'
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable =False , primary_key = True)
    storage_id = db.Column(db.Integer, db.ForeignKey('storagecage.id'), nullable =False , primary_key = True)
    verify_id = db.Column(db.Integer, db.ForeignKey('verify.id'), nullable =False , primary_key = True)
    status_posted = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    status = db.Column(db.String,nullable = False, default='order')
    quantity = db.Column(db.Integer, nullable=False, default=0)
    cost = db.Column(db.Float, nullable = True, default=0)

    storage = db.relationship('StorageCage', backref='storageProductOrder' , lazy=True)
    product = db.relationship('Product', backref='productStorageOrder' , lazy=True)
    verify = db.relationship('Verify', backref='VerifyStocktakeOrder' , lazy=True)
    def __repr__(self):
        return f"Order_Product('{self.product_id}','{self.storage_id}',{self.verify_id}','{self.status}','{self.status_posted}','{self.cost}')" 

class User_Storage(db.Model):
    __tablename__ = 'user_storage'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable =False , primary_key = True)
    storage_id = db.Column(db.Integer, db.ForeignKey('storagecage.id'), nullable =False , primary_key = True)

    storage = db.relationship('StorageCage', backref='storagecageUser' , lazy=True)
    user = db.relationship('User', backref='user_storage_info' , lazy=True)
    def __repr__(self):
        return f"User_Storage('{self.user_id}','{self.storage_id}')" 
