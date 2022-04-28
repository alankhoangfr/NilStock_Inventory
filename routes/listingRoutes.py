from flask import render_template, url_for, flash, redirect, request, abort, jsonify, make_response
from app import app, db, bcrypt, mail
from forms import *
from models import *
from flask_login import login_user, current_user, logout_user, login_required
from routes.commonRoutes import commonTempRoute,convertJson



@app.route("/listing", methods=['GET', 'POST'])
@login_required
def listing():
    info = commonTempRoute(Listing, ListingForm())
    return render_template('commonTemps/common.html',  mainArray=info["mainArray"], funName='listing', mainLabel='Listing',
        formMain=info["formMain"], formLocation=info["formLocation"], formArea=info["formArea"], mainInd = 'listingInd')



@app.route("/listingind/<int:main_id>", methods=['GET', 'POST'])
@login_required
def listingInd(main_id):
    listing = Listing.query.get_or_404(main_id)
    storages = listing.subscription

    storageIds = list(set([stor.id for stor in storages]))
    usersInStorage = []
    for stor in storageIds:
        users = [user.user_id for user in User_Storage.query.filter_by(storage_id=stor).all()]
        usersInStorage.extend(users)
    allUsersInStorage = list(set(usersInStorage))
    if(current_user.id in allUsersInStorage or current_user.role=="Admin"):
        allProduct_Storage=Product_Storage_Listing.query.filter_by(listing_id=main_id)

        uniqueProdStor=[aps.product for aps in allProduct_Storage.distinct(Product_Storage_Listing.product_id)]
        productInStorage=[]
        for pid in uniqueProdStor:
            allStorage = Product_Storage_Listing.query.filter((Product_Storage_Listing.listing_id==main_id), (Product_Storage_Listing.product_id==pid.id)).all()
            product_storage_info=[]
            for stor in allStorage:
                product_storage_info.append(Product_Storage.query.filter_by(storage_id=stor.storage_id, product_id=pid.id).first())
            productInStorage.append([product_storage_info,allStorage])

        stocktake = Verify_Product_Storage.query.filter(Verify_Product_Storage.storage_id.in_(storageIds)).distinct(Verify_Product_Storage.verify_id).all()

        possibleRemove=False

        if(len(productInStorage)==0 and len(storages)==0 and len(stocktake)==0):
            possibleRemove=True

        stocktake = []

        stocktake.extend(Verify_Listing_Booking.query.filter_by(listing_id=main_id).distinct(Verify_Listing_Booking.verify_id).all())
        notificationVerify=[]
        for stock in stocktake:
            temp=[]
            st = Verify.query.filter_by(id=stock.verify_id, user_id_confirm = None, date_verified = None).first()
            if(st!=None):
                temp={}
                temp["title"]=st.title
                temp["date"]=st.date_posted.strftime('%Y-%m-%d at %H:%M')
                temp["verify_id"]=st.id
                temp["username"]=User.query.filter_by(id=st.user_id).first().username
                if(st.title=="Stocktake"):
                    temp["url"]="verifyStocktake"
                elif(st.title=="Transfer"):
                    temp["url"]="verifyTransfer"
                elif(st.title=="Shopping"):
                    temp["url"]="verifyShopping"
                elif(st.title=="Update Booking"):
                    temp["url"]="verifyUpdateBooking"
                notificationVerify.append(temp)
        return render_template('commonTemps/listing/listingInd.html', notificationVerify=notificationVerify,storages=storages, listing=listing, productInStorage=productInStorage,possibleRemove=possibleRemove, role=current_user.role)
    else:
        return render_template('formLayout/noAccess.html')


   

        
@app.route("/listing/new", methods=['POST'])
@login_required
def addListing():
    if (request.json!=None):
        if request.json.get('submit')=='listing':
            checkName = Listing.query.filter_by(name=request.json.get('name').strip()).all()
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
                listing = Listing(name=request.json.get('name').strip(), location_id=location_id)
                db.session.add(listing)
                db.session.commit()
                return jsonify({'status':'success'})
                return redirect(url_for('storage'))
            else:
                return jsonify({'status':'fail', 'reason':'Please try again'})
    else:
        return jsonify({'status':'fail', 'reason':'No data'})

@app.route("/listing/remove", methods=['POST'])
@login_required
def removeListing():
    if (request.json!=None):
        if request.json.get('submit')=='removeListing':
            deleteRecord = Listing.query.filter_by(id=request.json.get('listing_id')).first()
            if deleteRecord != None:
                db.session.delete(deleteRecord)
                db.session.commit()
                return jsonify({"status":"success"})
        return jsonify({"status":"fail"})
    else:
        return jsonify({'status':'fail', 'reason':'No data'})


@app.route("/listing/edit", methods=['POST'])
@login_required
def editListing():
    if (request.json!=None):
        if request.json.get('submit')=='editListing':
            editRecord = Listing.query.filter_by(id=request.json.get('listing_id')).first()
            if editRecord != None:
                editRecord.name=request.json.get('newName')
                db.session.commit()
                return jsonify({"status":"success"})
        return jsonify({"status":"fail"})
    else:
        return jsonify({'status':'fail', 'reason':'No data'})




@app.route("/listing/area/<area_id>",methods=['GET'])
@login_required
def listingFromArea(area_id):
    listings = Listing.query.filter(Listing.location.has(Location.area_id==area_id)).all()
    listingArray = []
    
    for lis in listings:
        lisObj = {}
        lisObj['name']=lis.name
        lisObj['id']=lis.id
        listingArray.append(lisObj)
    return jsonify({'listings':listingArray})

@app.route("/listing/state/<state_id>",methods=['GET'])
@login_required
def listingFromState(state_id):
    listings = Listing.query.filter(Listing.location.has(Location.state_id==state_id)).all()
    listingArray = []
    
    for lis in listings:
        lisObj = {}
        lisObj['name']=lis.name
        lisObj['id']=lis.id
        listingArray.append(lisObj)
    return jsonify({'listings':listingArray})


@app.route("/listing/suburb/<suburb>",methods=['GET'])
@login_required
def listingFromSuburb(suburb):
    listings = Listing.query.filter(Listing.location.has(Location.suburb==suburb)).all()
    listingArray = []
    
    for lis in listings:
        lisObj = {}
        lisObj['name']=lis.name
        lisObj['id']=lis.id
        listingArray.append(lisObj)
    return jsonify({'listings':listingArray})

@app.route("/notlisting/area/<area_id>/storage/<storage_id>",methods=['GET'])
@login_required
def nolistingFromArea(area_id,storage_id):
    allListing = Listing.query.filter(Listing.location.has(Location.area_id==area_id)).all()
    storageListing = [a for a in StorageCage.query.filter_by(id=storage_id).first().subscription]
    listings = [a for a in allListing if a not in storageListing]
    
    listingArray = []

    for lis in listings:
        lisObj = {}
        lisObj['name']=lis.name
        lisObj['id']=lis.id
        listingArray.append(lisObj)
    return jsonify({'listings':listingArray})

@app.route("/notlisting/state/<state_id>/storage/<storage_id>",methods=['GET'])
@login_required
def nolistingFromState(state_id,storage_id):
    allListing = Listing.query.filter(Listing.location.has(Location.state_id==state_id)).all()
    storageListing = [a for a in StorageCage.query.filter_by(id=storage_id).first().subscription]
    listings = [a for a in allListing if a not in storageListing]

    listingArray = []
    
    for lis in listings:
        lisObj = {}
        lisObj['name']=lis.name
        lisObj['id']=lis.id
        listingArray.append(lisObj)
    return jsonify({'listings':listingArray})


@app.route("/listingInfo/<int:listing_id>",methods=['GET'])
@login_required
def listingInfo(listing_id):
    listingInd = Listing.query.filter_by(id=listing_id).first()

    state = State.query.filter(State.id!=listingInd.location.state_id).all()
    state.insert(0,State.query.filter_by(id=listingInd.location.state_id).first())
    stateJson = convertJson(state,True)

    area = Area.query.filter(Area.id!=listingInd.location.area_id).all()
    area.insert(0,Area.query.filter_by(id=listingInd.location.area_id).first())
    areaJson = convertJson(area,True)

    suburb = Location.query.filter(Location.id!=listingInd.location.id).distinct(Location.suburb).all()
    suburb.insert(0,Location.query.filter_by(id=listingInd.location.id).first())
    suburbJson = convertJson(suburb,False)

    storages=[(stor.id,stor.name) for stor in listingInd.subscription]
    

    return jsonify({'storages':storages,'state':stateJson,'area':areaJson,'suburb':suburbJson})


