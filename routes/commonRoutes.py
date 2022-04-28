from flask import render_template, url_for, flash, redirect, request, abort, jsonify, make_response
from app import app, db, bcrypt, mail
from forms import *
from models import *
from sqlalchemy.sql import func
from flask_login import  current_user
from flask_mail import Message
import secrets
import os
from PIL import Image

def searchButton(table):
    
    searchValue = request.args.get('searchValue')
    if searchValue:
        result = table.query.filter((table.name.ilike('%'+searchValue+'%')) | (table.comment.ilike('%'+searchValue+'%'))).all()
    else: 
        result = table.query.all()
    return result

def outputBuyers():
    return ['Company','Cleaner','Owner']


def createNewVerify(title,comment):
    new_id_db=db.session.query(func.max(Verify.id)).scalar()
    if new_id_db is None:
        new_id=0
    else:
        new_id=new_id_db+1
    newVerification = Verify(id=new_id,user_id=current_user.id,comment=comment,title=title)
    db.session.add(newVerification)
    db.session.commit()
    return new_id

def updateVerify(comment,verifyId):
    verify = Verify.query.filter_by(id=verifyId).first()
    verify.user_id_confirm=current_user.id
    verify.date_verified=datetime.utcnow()
    verify.comment=comment
    db.session.commit()

def send_reset_email_verification(type,verify_id, user, tableName):
    title=""
    url_for_link=""
    if(type=="stocktake"):
        title="Stocktake"
        url_for_link='verifyStocktake' 
    elif(type=="transfer"):
        title="Transfer"
        url_for_link='verifyTransfer'  
    elif(type=="booking"):
        title="Update Booking"
        url_for_link='verifyUpdateBooking' 
    elif(type=="shopping"):
        title="Update Shopping"
        url_for_link='verifyShopping' 

    link=url_for(url_for_link, verify_id=verify_id, _external=True)
    for admin in User.query.filter_by(role='Admin').all():
        msg = Message('Verification '+title+' Request',
                      sender='noreply@demo.com',
                      recipients=[admin.email])
        msg.body = f'''To view the verification of {tableName.name}-{tableName.location.suburb} by {user.username} please click this link:
    {link}

    If you did not make this request then simply ignore this email and no changes will be made.
    '''
        mail.send(msg)


def convertJson(array,id):
    resultArray=[]
    if id==True:
        for elem in array:
            obj = {}
            obj['id']=elem.id
            obj['name']=elem.name
            resultArray.append(obj)
        return resultArray
    else:
        for elem in array:
            obj = {}
            obj['id']=elem.id
            obj['name']=elem.suburb
            resultArray.append(obj)
        return resultArray

def outputStates():
    return [(state.id,state.name) for state in State.query.all()]


def save_picture(folder,currentFile,form_picture):
    if(currentFile  !='default.jpg'):
        try:
            os.remove( 'static/pictures/'+folder+'/'+currentFile)
        except:
            print("NO image found")
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/pictures/'+folder, picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

    
def findSupplierForm(storage):
    fs =FindSupplier()
    areaOfStorageId = storage.location.area_id
    fs.fs_state.choices=outputStates()
    areaSuppliers=([(sup.id,str(sup.name+': '+ sup.location.numberAndStreet+' '+ 
        sup.location.suburb+' '+ sup.location.area_loc.name+' '+sup.location.state_loc.name)) 
    for sup in Supplier.query.filter(Supplier.location.has(Location.area_id==areaOfStorageId))])
    result = {}
    result["fs"]=fs
    result["areaSuppliers"]=areaSuppliers
    return result


def commonTempRoute( dbObject,  form ):

    page = request.args.get('page', 1, type=int)

    searchValue = request.args.get('searchValue')

    if dbObject == StorageCage and current_user.role=="Manager":
        storAvaliable = [(s.storage_id) for s in User_Storage.query.filter_by(user_id=current_user.id).all()]
        if searchValue:
            mainArray = dbObject.query.filter((dbObject.id.in_(storAvaliable))&((dbObject.name.ilike('%'+searchValue+'%')) |  (dbObject.location.has(Location.suburb.ilike('%'+searchValue+'%')))\
                | (dbObject.location.has(Location.numberAndStreet.ilike('%'+searchValue+'%'))) | (dbObject.location.has(Location.area_loc.has(Area.name.ilike('%'+searchValue+'%')))))).paginate(page=page, per_page=9) 
        else: 
            mainArray = dbObject.query.filter(dbObject.id.in_(storAvaliable)).paginate(page=page, per_page=9) 

    else:

        if searchValue:
            mainArray = dbObject.query.filter((dbObject.name.ilike('%'+searchValue+'%')) |  (dbObject.location.has(Location.suburb.ilike('%'+searchValue+'%')))\
                | (dbObject.location.has(Location.numberAndStreet.ilike('%'+searchValue+'%'))) | (dbObject.location.has(Location.area_loc.has(Area.name.ilike('%'+searchValue+'%'))))).paginate(page=page, per_page=9) 
        else: 
            mainArray = dbObject.query.paginate(page=page, per_page=9) 
       

    formMain = form
    formMain.state.choices = outputStates()

    '''
    if(len(Location.query.all())>0):
        formMain.suburb.choices =[loc.suburb for loc in Location.query.filter_by(state_id=1).distinct(Location.suburb).all()]
        formMain.address.choices =[loc.numberAndStreet for loc in Location.query
            .filter_by(state_id=1, suburb=formMain.suburb.choices[0])
            .distinct(Location.numberAndStreet).all()]
    '''
    formLocation = LocationForm()
    areaChoicesByState = sorted([(area.id,area.name) for area in Area.query.filter_by(state_id=1).all()]) 
    #formLocation.area.choices =areaChoicesByState
    formLocation.stateLoc.choices = outputStates()


    formArea = AreaForm()
    formArea.stateArea.choices = outputStates()


    return {"mainArray":mainArray,"formMain":formMain,"formLocation":formLocation,"formArea":formArea}

