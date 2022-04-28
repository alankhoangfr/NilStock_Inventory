import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, jsonify, make_response
from app import app, db, bcrypt, mail
from forms import *
from models import *
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from routes.commonRoutes import outputStates

def infoArea(area_id):
    area = Area.query.get_or_404(area_id)
    info={}
    info["Supplier"]=Supplier.query.filter(Supplier.location.has(Location.area_id==area.id)).all()
    info["Listing"]=Listing.query.filter(Listing.location.has(Location.area_id==area.id)).all()
    info["StorageCage"]=StorageCage.query.filter(StorageCage.location.has(Location.area_id==area.id)).all()
    allLocationIds=[l.id for l in Location.query.filter(Location.area_id==area.id).all()]
    nonEmptyId = [l.location.id for l in info["Supplier"]]
    nonEmptyId.extend([l.location.id for l in info["Listing"]])
    nonEmptyId.extend([l.location.id for l in info["StorageCage"]])
    emptyLocationsId = list(set(allLocationIds)-set(nonEmptyId))
    info["emptyLocations"]=Location.query.filter(Location.id.in_(emptyLocationsId)).all()
    return info

def locationInfo(location_id):
    loc=Location.query.filter_by(id=location_id).first()
    countLoc={}
    countLoc["storageCage"]=StorageCage.query.filter(StorageCage.location.has(Location.id==location_id)).count()
    countLoc["suppliers"]=Supplier.query.filter(Supplier.location.has(Location.id==location_id)).count()
    countLoc["listing"]=Listing.query.filter(Listing.location.has(Location.id==location_id)).count()
    status="Not Empty"
    if(countLoc["storageCage"]+countLoc["suppliers"]+countLoc["listing"]==0):
        status="Empty"
    countLoc["status"]=status
    return countLoc

@app.route("/area", methods=['GET'])
@login_required
def area():
    page = request.args.get('page', 1, type=int)

    formArea= AreaForm()
    formArea.stateArea.choices = outputStates()

    searchValue = request.args.get('searchValue')

    if searchValue:
        allAreas = Area.query.filter((Area.name.ilike('%'+searchValue+'%'))|(Area.area_state.has(State.name.ilike('%'+searchValue+'%')))).paginate(page=page, per_page=9) 
    else: 
        allAreas = Area.query.paginate(page=page, per_page=9) 
    
    info={}
    for a in Area.query.all():
        temp={}
        ia=infoArea(a.id)
        temp["Supplier"]=len(ia["Supplier"])
        temp["Listing"]=len(ia["Listing"])
        temp["StorageCage"]=len(ia["StorageCage"])
        temp["emptyLocations"]=len(ia["emptyLocations"])
        info[a.id]=temp
    
    return render_template('location/area.html',info=info,allAreas=allAreas, formArea=formArea)

@app.route("/areaInd/<int:area_id>", methods=['GET', 'POST'])
@login_required
def areaInd(area_id):
    area = Area.query.get_or_404(area_id)
    info={}
    info["Supplier"]=Supplier.query.filter(Supplier.location.has(Location.area_id==area.id)).all()
    info["Listing"]=Listing.query.filter(Listing.location.has(Location.area_id==area.id)).all()
    info["StorageCage"]=StorageCage.query.filter(StorageCage.location.has(Location.area_id==area.id)).all()
    allLocationIds=[l.id for l in Location.query.filter(Location.area_id==area.id).all()]
    nonEmptyId = [l.location.id for l in info["Supplier"]]
    nonEmptyId.extend([l.location.id for l in info["Listing"]])
    nonEmptyId.extend([l.location.id for l in info["StorageCage"]])
    emptyLocationsId = list(set(allLocationIds)-set(nonEmptyId))
    info["emptyLocations"]=Location.query.filter(Location.id.in_(emptyLocationsId)).all()
    
    possibleRemove=False

    if len(info["Supplier"])==0 and len(info["Listing"])==0 and len(info["StorageCage"])==0 :
        possibleRemove=True


    return render_template('location/areaInd.html', role=current_user.role,area=area, info=info,possibleRemove=possibleRemove)



@app.route("/area/new", methods=['POST'])
@login_required
def addArea():
    if (request.json!=None):
        if request.json.get('submit')=='Add Area':
            state_id  = request.json.get('stateArea')
            area_name = request.json.get('area_name').strip()
            exist = Area.query.filter_by(name=area_name, state_id=state_id).all()
            if(len(exist)>0):
                return jsonify({'status':'fail','reason':'The Area has already been added'})
            if(len(area_name)==0):
                return jsonify({'status':'fail','reason':'Please complete the form'})
            if(len(exist)==0):
                area = Area(name=area_name , state_id =state_id)
                db.session.add(area)
                db.session.commit()
                return jsonify({'status':'success'})
            else:
                return jsonify({'status':'fail'})
    return jsonify({'status':'fail'})


@app.route("/area/remove", methods=['POST'])
@login_required
def removeArea():
    if (request.json!=None):
        if request.json.get('submit')=='removeArea':
            deleteRecord = Area.query.filter_by(id=request.json.get('area_id')).first()
            if deleteRecord != None:
                db.session.delete(deleteRecord)
                db.session.commit()
                return jsonify({"status":"success"})
        return jsonify({"status":"fail"})
    else:
        return jsonify({'status':'fail', 'reason':'No data'})

@app.route("/area/edit", methods=['POST'])
@login_required
def editArea():
    if (request.json!=None):
        if request.json.get('submit')=='editArea':
            editRecord = Area.query.filter_by(id=request.json.get('area_id')).first()
            if editRecord != None:
                editRecord.name=request.json.get('newName')
                db.session.commit()
                return jsonify({"status":"success"})
        return jsonify({"status":"fail"})
    else:
        return jsonify({'status':'fail', 'reason':'No data'})




@app.route("/location", methods=['GET'])
@login_required
def location():

    formLocation= LocationForm()
    formLocation.stateLoc.choices = outputStates()

    searchValue = request.args.get('searchValue')

    if searchValue:
        allLocations = Location.query.filter((Location.numberAndStreet.ilike('%'+searchValue+'%'))|(Location.state_loc.has(State.name.ilike('%'+searchValue+'%')))
            |(Location.area_loc.has(Area.name.ilike('%'+searchValue+'%')))|(Location.suburb.ilike('%'+searchValue+'%'))).all() 
    else: 
        allLocations = Location.query.all()
    allLocationInfo=[]
    for loc in allLocations:
        allLocationInfo.append([loc,locationInfo(loc.id)])
    
    return render_template('location/location.html',allLocationInfo=allLocationInfo, formLocation=formLocation)

@app.route("/getLocationInfo/<int:location_id>", methods=['GET'])
@login_required
def getLocationInfo(location_id):
    info=Location.query.filter_by(id=location_id).first()
    infoJson=locationInfo(location_id)
    infoJson["id"]=info.id
    infoJson["fullAddress"]=info.numberAndStreet+', '+info.suburb+ ', '+str(info.postcode)+', '+info.state_loc.name
    return jsonify(infoJson)


@app.route("/location/new", methods=['POST'])
@login_required
def addLocation():
    if (request.json!=None):
        if request.json.get('submit')=='location':
            state_id = request.json.get('stateLoc')
            area_id = Area.query.filter_by(name=request.json.get('area').strip()).first().id
            areaAndState = Area.query.filter_by(state_id = state_id, id=area_id).all()
            numberAndStreet=request.json.get('addressLoc').strip()
            suburb=request.json.get('suburbLoc').strip()
            try:
                postcode=int(request.json.get('postcode'))
            except:
                return jsonify({'status':'fail','reason':'Invalid Postcode'})
            testLocation = Location.query.filter_by(
                numberAndStreet=numberAndStreet,
                suburb=suburb,
                postcode=postcode,
                state_id=state_id,
                area_id=area_id).all()
            if(len(areaAndState)==0):
                return jsonify({'status':'fail','reason':'Wrong combination of Area and State'})
            if(len(numberAndStreet)==0 or len(suburb)==0):
                return jsonify({'status':'fail','reason':'Please complete the form'})
            if(len(testLocation)>0):
                return jsonify({'status':'fail','reason':'The address has already been added'})
            if(len(areaAndState)>0 and len(numberAndStreet)>0 and len(suburb)>0):
                new_location = Location(
                numberAndStreet=numberAndStreet,
                suburb=suburb,
                postcode=postcode,
                state_id=state_id,
                area_id=area_id)
                db.session.add(new_location)
                db.session.commit()
                return jsonify({'status':'success'})
            else:
                return jsonify({'status':'fail','reason':'Error in adding Location. Please try again'})
    else:
        return jsonify({'status':'fail', 'reason':'No data'})

@app.route("/location/remove", methods=['POST'])
@login_required
def removeLocation():
    if (request.json!=None):
        if request.json.get('submit')=='removeLocation':
            deleteRecord = Location.query.filter_by(id=request.json.get('location_id')).first()
            if deleteRecord != None:
                db.session.delete(deleteRecord)
                db.session.commit()
                return jsonify({"status":"success"})
        return jsonify({"status":"fail"})
    else:
        return jsonify({'status':'fail', 'reason':'No data'})


@app.route("/locations/<state_id>/suburb",methods=['GET'])
@login_required
def suburbFromState(state_id):
    locations = Location.query.filter_by(state_id = state_id).distinct(Location.suburb).all()
    locationArray = []

    for loc in locations:
        locObj = {}
        locObj['suburb']=loc.suburb
        locationArray.append(locObj)
    return jsonify({'locations':locationArray})

@app.route("/locations/<state_id>/<suburb>/address",methods=['GET'])
@login_required
def addressFromStateSuburb(state_id,suburb):
    locations = Location.query.filter_by(suburb = suburb, state_id=state_id).distinct(Location.numberAndStreet).all()
    locationArray = []

    for loc in locations:
        locObj = {}
        locObj['address']=loc.numberAndStreet
        locationArray.append(locObj)
    return jsonify({'locations':locationArray})

@app.route("/locations/<state_id>/address",methods=['GET'])
@login_required
def addressFromState(state_id):
    locations = Location.query.filter_by(state_id=state_id).distinct(Location.numberAndStreet).all()
    locationArray = []

    for loc in locations:
        locObj = {}
        locObj['address']=loc.numberAndStreet
        locationArray.append(locObj)
    return jsonify({'locations':locationArray})

@app.route("/locations/<state_id>/area",methods=['GET'])
@login_required
def areaFromState(state_id):
    areas = Area.query.filter_by(state_id = state_id).distinct(Area.name).all()
    locationArray = []

    for loc in areas:
        locObj = {}
        locObj['id']=loc.id
        locObj['name']=loc.name
        locationArray.append(locObj)
    return jsonify({'locations':locationArray})

@app.route("/locations/area/<area_id>/suburb",methods=['GET'])
@login_required
def suburbFromArea(area_id):
    locations = Location.query.filter_by(area_id = area_id).distinct(Location.suburb).all()
    locationArray = []

    for loc in locations:
        locObj = {}
        locObj['id']=loc.id
        locObj['suburb']=loc.suburb
        locationArray.append(locObj)
    return jsonify({'locations':locationArray})