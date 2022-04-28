from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField,DecimalField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import *
import phonenumbers


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=['Manager','Admin'])
    phone = StringField('Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Add User')

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')
    phone = StringField('Phone', validators=[DataRequired()])
    

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')


    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class StorageForm(FlaskForm):
    name = StringField('Storage Cage Name', validators=[DataRequired()])
    state = SelectField('State', choices=[])
    suburb = SelectField('Suburb', choices=[])
    address = SelectField('Address', choices=[])
    submit = SubmitField('Add Storage')

    
class NameSearch(FlaskForm):
    searchName = StringField('Name')
    search = SubmitField('Search')
    clear = SubmitField('Clear')
    

class ListingForm(FlaskForm):
    name = StringField('Listing Name', validators=[DataRequired()])
    state = SelectField('State', choices=[])
    suburb = SelectField('Suburb', choices=[])
    address = SelectField('Address', choices=[])
    submit = SubmitField('Add Listing')


class LocationForm(FlaskForm):
    addressLoc = StringField('Address', validators=[DataRequired()])
    suburbLoc = StringField('Suburb', validators=[DataRequired()])
    postcode = IntegerField('Postcode', validators=[DataRequired()])
    stateLoc = SelectField('State', choices=[])
    area = SelectField('Area', choices=[])
    submit = SubmitField('Add Location')


class AreaForm(FlaskForm):
    area_name = StringField('Area Name', validators=[DataRequired()])
    stateArea = SelectField('State', validators=[DataRequired()], choices=[])
    submit = SubmitField('Add Area')

class StorageListingAddForm(FlaskForm):
    sla_state = SelectField('State', choices=[])
    sla_area = SelectField('Area', choices=[], validate_choice=False)
    sla_listing = SelectField('Listings', choices=[],validate_choice=False) 
    sla_submit = SubmitField('Add Listing')

class RemoveListing(FlaskForm):
    rl_listing = SelectField('Avaliable Listings', choices=[]) 
    rl_submit = SubmitField('Remove Listing')


class UpdateBookings(FlaskForm):
    up_listing = SelectField('Avaliable Listings', choices=[]) 
    up_bookings= IntegerField('Number of Bookings', validators=[DataRequired()])
    up_comment = TextAreaField('Comment')
    up_submit_admin = SubmitField('Update')
    up_submit_manager = SubmitField('Send')


class AddProduct(FlaskForm):
    ap_name = StringField('Name', validators=[DataRequired(), Length(min=2)])
    ap_size = DecimalField('Size', validators=[DataRequired()],render_kw={"placeholder": "For XXXml, enter XXX. For example 600ml, Enter 600"})
    ap_size_name = SelectField('Size Type', choices=["Units","Milliliters","Litres","Milimeters","Meters","Grams","Kilograms","Sheets","Rolls","Blocks","Bottles","Cans","Tubs","Packets","Bags","Items","Box"])
    ap_category = SelectField('Category', coerce=int,choices=[])
    ap_subcategory = SelectField('SubCategory',coerce=int, choices=[],validate_choice=False)
    ap_picture = FileField('Update Photo', validators=[FileAllowed(['jpg', 'png'])])
    ap_comment = TextAreaField('Comment')
    ap_submit = SubmitField('Add Product')

class UpdateProductForm(FlaskForm):
    picture = FileField('Update Photo', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

class AddProductStorageListing(FlaskForm):
    apsl_product = SelectField('Product', choices=[])
    apsl_listing = SelectField('Product', choices=[])

    apsl_supplier = SelectField('Supplier', choices=[])
    apsl_buyer = SelectField('Buyer', choices=['Company','Cleaner','Owner'])
    apsl_perBooking = DecimalField('Per Booking', validators=[DataRequired()])
    apsl_quantity = IntegerField('Quantity', validators=[DataRequired()])
    apsl_submit = SubmitField('Add Product')

class FindSupplier(FlaskForm):
    fs_state = SelectField('State of Supplier', choices=[])
    fs_area = SelectField('Area of Supplier', choices=[])
    fs_supplier = SelectField('Supplier', choices=[])
    fs_submit = SubmitField('Select Supplier')

class AddSuppliers(FlaskForm):
    name = StringField('Supplier Name', validators=[DataRequired()])
    contact = StringField('Phone')
    website = StringField('Website')
    state = SelectField('State', choices=[])
    suburb = SelectField('Suburb', choices=[])
    address = SelectField('Address', choices=[])
    submit = SubmitField('Add Suppliers')

class FilterProducts(FlaskForm):
    state = SelectField('State', choices=[])
    area = SelectField('Area', choices=[])
    suburb = SelectField('Suburb', choices=[])
    storageCage  = SelectField('Storage Cage', choices=[])
    listing  = SelectField('Listing', choices=[])
    numberOfBooking = IntegerField('Bookings')
    search = SubmitField('Filter')

class CommonProducts(FlaskForm):
    storageCage2 = SelectField('Transfer Inventory to', choices=[])
    submit=SubmitField('Find')

