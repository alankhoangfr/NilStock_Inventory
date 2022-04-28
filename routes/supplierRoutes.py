from flask import render_template, url_for, flash, redirect, request, abort, jsonify, make_response
from app import app, db, bcrypt, mail
from forms import *
from models import *
from flask_login import login_user, current_user, logout_user, login_required
from routes.commonRoutes import commonTempRoute



@app.route("/supplier", methods=['GET', 'POST'])
@login_required
def suppliers():
    info = commonTempRoute(Supplier, AddSuppliers())
    return render_template('supplier/supplier.html',  mainArray=info["mainArray"], funName='listing', mainLabel='Supplier',
        formMain=info["formMain"], formLocation=info["formLocation"], formArea=info["formArea"], mainInd = 'listingInd')

@app.route("/supplier/new", methods=['POST'])
@login_required
def addSupplier():
    if (request.json!=None):
        if request.json.get('submit')=='supplier':
            checkName = Supplier.query.filter_by(name=request.json.get('name').strip()).all()
            locations = Location.query.filter_by(
                numberAndStreet=request.json.get('address').strip(),
                suburb=request.json.get('suburb').strip(),
                state_id = request.json.get('state')).first()
            if(len(checkName)>0):
                return jsonify({'status':'fail','reason':'Name already taken'})
            if(locations==None):
                return jsonify({'status':'fail','reason':'Location has not been registered'})
            if(len(request.json.get('name').strip())<1):
                return jsonify({'status':'fail','reason':'Invalid Name'})
            if(locations!=None and len(checkName)==0 and len(request.json.get('name').strip())>0):
                location_id  = locations.id
                supplier = Supplier(name=request.json.get('name').strip(), location_id=location_id, contact=request.json.get('contact'), website=request.json.get('website'))
                db.session.add(supplier)
                db.session.commit()
                return jsonify({'status':'success'})
                return redirect(url_for('storage'))
            else:
                return jsonify({'status':'fail', 'reason':'Please try again'})
    else:
        return jsonify({'status':'fail', 'reason':'No data'})


@app.route("/getSupplierInfo/<int:supplier_id>", methods=['GET'])
@login_required
def getSupplierInfo(supplier_id):
    info=Supplier.query.filter_by(id=supplier_id).first()
    infoJson={}
    infoJson["product_storage_listing"]=Product_Storage_Listing.query.filter_by(supplier_id=supplier_id).count()
    infoJson["verify_product_storage_listing"]=Verify_Product_Storage_Listing.query.filter_by(supplier_id=supplier_id).count()
    infoJson["id"]=info.id
    infoJson["name"]=info.name
    infoJson["contact"]=info.contact
    infoJson["website"]=info.website
    return jsonify(infoJson)

@app.route("/supplier/remove", methods=['POST'])
@login_required
def removeSupplier():
    if (request.json!=None):
        if request.json.get('submit')=='removeSupplier':
            deleteRecord = Supplier.query.filter_by(id=request.json.get('supplier_id')).first()
            if deleteRecord != None:
                db.session.delete(deleteRecord)
                db.session.commit()
                return jsonify({"status":"success"})
        return jsonify({"status":"fail"})
    else:
        return jsonify({'status':'fail', 'reason':'No data'})

@app.route("/supplier/edit", methods=['POST'])
@login_required
def editSupplier():
    if (request.json!=None):
        if request.json.get('submit')=='supplier edit':
            editRecord = Supplier.query.filter_by(id=request.json.get('supplier_id')).first()
            if editRecord != None:
                editRecord.name=request.json.get('newName')
                editRecord.contact=request.json.get('newContact')
                editRecord.website=request.json.get('newWebsite')
                db.session.commit()
                return jsonify({"status":"success"})
        return jsonify({"status":"fail"})
    else:
        return jsonify({'status':'fail', 'reason':'No data'})



@app.route("/supplier/area/<area_id>")
@login_required
def supplierFromArea(area_id):
    supplier = Supplier.query.filter(Supplier.location.has(Location.area_id==area_id)).all()
    supplierArray = []
    
    for sup in supplier:
        supObj = {}
        supObj['name']=sup.name+': '+ sup.location.numberAndStreet+' '+ sup.location.suburb+' '+ sup.location.area_loc.name+' '+sup.location.state_loc.name
        supObj['id']=sup.id
        supplierArray.append(supObj)
    return jsonify({'suppliers':supplierArray})

@app.route("/supplier/state/<state_id>")
@login_required
def supplierFromState(state_id):
    supplier = Supplier.query.filter(Supplier.location.has(Location.state_id==state_id)).all()
    supplierArray = []
    
    for sup in supplier:
        supObj = {}
        supObj['name']=sup.name+': '+ sup.location.numberAndStreet+' '+ sup.location.suburb+' '+ sup.location.area_loc.name+' '+sup.location.state_loc.name
        supObj['id']=sup.id
        supplierArray.append(supObj)
    return jsonify({'suppliers':supplierArray})
