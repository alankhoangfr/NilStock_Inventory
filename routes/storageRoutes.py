from flask import render_template, url_for, flash, redirect, request, abort, jsonify, make_response
from app import app, db, bcrypt, mail
from forms import *
from models import *
from flask_login import login_user, current_user, logout_user, login_required
from routes.commonRoutes import commonTempRoute,outputStates,findSupplierForm,convertJson





@app.route("/storage", methods=['GET', 'POST'])
@login_required
def storage():
    info = commonTempRoute(StorageCage,StorageForm())
    return render_template('commonTemps/common.html',  mainArray=info["mainArray"], funName='storage', mainLabel='Storage',
        formMain=info["formMain"], formLocation=info["formLocation"], formArea=info["formArea"], mainInd = 'storageInd')


@app.route("/storageCage/<int:main_id>", methods=['GET', 'POST'])
@login_required
def storageInd(main_id):
    user_storage = User_Storage.query.filter_by(storage_id=main_id).all()
    user_storage_id = [user.user_id for user in user_storage]
    if(current_user.id in user_storage_id or current_user.role=="Admin"):
        storage = StorageCage.query.get_or_404(main_id)
 
        listing = storage.subscription

        removeListing =RemoveListing()
        avaliableListings = [(listObj.id,listObj.name) for listObj in listing]
        removeListing.rl_listing.choices=avaliableListings

        updateBooking =UpdateBookings()
        updateBooking.up_listing.choices = avaliableListings


        apsl = AddProductStorageListing()


        productInStorageChoice = [p.product for p in Product_Storage.query.filter_by(storage_id=main_id).all()]
        apsl.apsl_product.choices=[(prod.id,prod.name+', '+prod.size) for prod in Product.query.all() if prod not in productInStorageChoice]
        

        removeProducts=[p for p in Product_Storage.query.filter_by(storage_id=main_id).all() if p.quantity==0]
        

        fs=findSupplierForm(storage)
        empty=0

        filterStorage = Product_Storage.query.filter_by(storage_id=main_id)
        uniqueProdStor = [prod.product_id for prod in filterStorage.distinct(Product_Storage.product_id).all()]
        productInStorage =[]
        for pid in uniqueProdStor:
            allLisings = Product_Storage_Listing.query.filter((Product_Storage_Listing.storage_id==main_id), (Product_Storage_Listing.product_id==pid), (Product_Storage_Listing.per_booking>0)).all()
            product_storage_info = Product_Storage.query.filter_by(storage_id=main_id, product_id=pid).first()
            empty+=product_storage_info.quantity
            productInStorage.append([product_storage_info,allLisings])


        add_users = [(user.id,user.username) for user in User.query.all() if user not in [user_stor.user for user_stor in user_storage]]

        stocktake = Verify_Product_Storage.query.filter_by(storage_id=main_id).distinct(Verify_Product_Storage.verify_id).all()
        stocktake.extend(Order_Product.query.filter_by(storage_id=main_id).distinct(Order_Product.verify_id).all())
        for lists in listing:
            stocktake.extend(Verify_Listing_Booking.query.filter_by(listing_id=lists.id).distinct(Verify_Listing_Booking.verify_id).all())
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

        possibleRemove=False
        possibleProductRemove=False
        if(empty==0 and len(listing)==0 and len(notificationVerify)==0):
            possibleRemove=True
        elif len(notificationVerify)==0:
            possibleProductRemove=True

        

        return render_template('commonTemps/storage/storageCage.html', listing=listing, areaSuppliers=fs["areaSuppliers"], fs=fs["fs"], role = current_user.role,possibleProductRemove=possibleProductRemove,
                removeProducts=removeProducts,rl=removeListing,apsl=apsl, storage=storage, 
                productInStorage=productInStorage, user_storage=user_storage,add_users=add_users, 
                notificationVerify=notificationVerify, possibleRemove=possibleRemove,updateBooking=updateBooking)
    else:
        return render_template('formLayout/noAccess.html')


@app.route("/product/addToStorage/search/<searchValue>/<int:storage_id>", methods=['GET'])
@login_required
def productStorageSearchAdd(searchValue,storage_id):
    productInStorageChoice = [p.product for p in Product_Storage.query.filter_by(storage_id=storage_id).all()]
    if(searchValue.lower().strip()=='all'):
        products = [prod for prod in Product.query.all() if prod not in productInStorageChoice]
    else:
        productsStorage = Product.query.filter((Product.name.ilike('%'+searchValue+'%')) | (Product.comment.ilike('%'+searchValue+'%'))).all()
        products = [prod for prod in productsStorage if  prod not in productInStorageChoice]
    productsArray = []
    for prod in products:
        prodObj = {}
        prodObj['name']=prod.name+', '+prod.size
        prodObj['id']=prod.id
        productsArray.append(prodObj)
    return jsonify({'productData':productsArray})

@app.route("/product/removeFromStorage/search/<searchValue>/<int:storage_id>", methods=['GET'])
@login_required
def productStorageSearchRemove(searchValue,storage_id):
    productInStorageChoice = [p.product for p in Product_Storage.query.filter_by(storage_id=storage_id).all() if p.quantity==0]
    if(searchValue.lower().strip()=='all'):
        products = [prod for prod in Product.query.all() if prod in productInStorageChoice]
    else:
        productsStorage = Product.query.filter((Product.name.ilike('%'+searchValue+'%')) | (Product.comment.ilike('%'+searchValue+'%'))).all()
        products = [prod for prod in productsStorage if  prod in productInStorageChoice]
    productsArray = []
    for prod in products:
        prodObj = {}
        prodObj['name']=prod.name+', '+prod.size
        prodObj['id']=prod.id
        productsArray.append(prodObj)
    return jsonify({'productData':productsArray})
        
@app.route("/storage/new", methods=['POST'])
@login_required
def addStorage():
    if (request.json!=None):
        if request.json.get('submit')=='storage':
            checkName = StorageCage.query.filter_by(name=request.json.get('name').strip()).all()
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
                    storageCage = StorageCage(name=request.json.get('name').strip(), location_id=location_id)
                    db.session.add(storageCage)
                    db.session.commit()
                    return jsonify({'status':'success'})
                    return redirect(url_for('storage'))
            else:
                    return jsonify({'status':'fail', 'reason':'Please try again'})
    else:
        return jsonify({'status':'fail', 'reason':'No data'})


@app.route("/storage/remove", methods=['POST'])
@login_required
def removeStorage():
    if (request.json!=None):
        if request.json.get('submit')=='removeStorage':
            deleteRecord = StorageCage.query.filter_by(id=request.json.get('storage_id')).first()
            if deleteRecord != None:
                db.session.delete(deleteRecord)
                db.session.commit()
                return jsonify({"status":"success"})
        return jsonify({"status":"fail"})
    else:
        return jsonify({'status':'fail', 'reason':'No data'})

@app.route("/storage/edit", methods=['POST'])
@login_required
def editStorage():
    if (request.json!=None):
        if request.json.get('submit')=='editStorage':
            editRecord = StorageCage.query.filter_by(id=request.json.get('storage_id')).first()
            if editRecord != None:
                editRecord.name=request.json.get('newName')
                db.session.commit()
                return jsonify({"status":"success"})
        return jsonify({"status":"fail"})
    else:
        return jsonify({'status':'fail', 'reason':'No data'})



@app.route("/storageAddListing/<int:storage_id>" , methods=['GET', 'POST'])
@login_required
def storageAddListing(storage_id): 

    sla = StorageListingAddForm()
    storage = StorageCage.query.get_or_404(storage_id)

    sla.sla_state.choices = outputStates()
    areaChoicesByState = sorted([(area.id,area.name) for area in Area.query.filter_by(state_id=1).all()]) 
    area_id = Area.query.filter_by(id=areaChoicesByState[0][0]).first().id
    sla.sla_area.choices =areaChoicesByState

    listingChoicesByArea = sorted([(listing.id,listing.name) for listing in 
            Listing.query.filter(Listing.location.has(Location.area_id==area_id)).all() 
            if listing not in storage.subscription]) 

    sla.sla_listing.choices =listingChoicesByArea
    productInStorage = Product_Storage.query.filter_by(storage_id=storage_id).all()
    
    apsl = AddProductStorageListing()
    fs =findSupplierForm(storage)
         
    if (request.json!=None):
        if request.json.get('submit')=='addProductListing':
            storage_id = request.json.get('storage_id')
            listing_id = request.json.get('listing_id')
            storageCage= StorageCage.query.filter_by(id=storage_id).all()
            if(len(storageCage)==0):
                    return jsonify({'status':'fail', 'reason':'Storage Cage does not exist'})
            
            listing = Listing.query.filter_by(id=listing_id).all()
            if(len(listing)==0):
                    return jsonify({'status':'fail', 'reason':'Listing does not exist'})
            info = request.json.get('info')
            if(len(info)<1 and request.json.get('infoCount')>0):
                    return jsonify({'status':'fail', 'reason':'Information was not sent'})
            for product in info:
                    productInfo = Product.query.filter_by(id=product).first()
                    psl = Product_Storage_Listing(
                            product_id=product,
                            storage_id=storage_id,
                            listing_id=listing_id,
                            supplier_id=info[product].get('supplier_id'),
                            orderentity=info[product].get('buyer'),
                            per_booking=info[product].get('booking'))
                    db.session.add(psl)
                    db.session.commit() 
            storage.subscribers.append(Listing.query.filter_by(id=listing_id).first())
            db.session.commit() 
            return jsonify({'status':'success', 'reason':''})
        return jsonify({'status':'success', 'reason':''})
    else:
        return render_template('commonTemps/storage/addListingInfo.html',apsl=apsl, areaSuppliers=fs["areaSuppliers"], fs=fs["fs"], sla=sla,productInStorage=productInStorage, storage=storage)



@app.route("/storageListingRemove",methods=['POST'])
@login_required
def storageListingRemove(): 
    storage_id=0
    if (request.json!=None):

        if request.json.get('submit')=='listingAdd':
            storage_id=request.json.get('storage_id')
            listing_id = request.json.get('listing_id')
            storage= StorageCage.query.filter_by(id=storage_id).first()
            listing = Listing.query.filter_by(id=listing_id).first()
            Product_Storage_Listing.query.filter_by(listing_id=listing_id).delete(synchronize_session=False)
            storage.subscription.remove(listing)
            db.session.commit()
                
    return redirect(url_for('storageInd',main_id=str(storage_id)))


@app.route("/storage/state/<int:state_id>",methods=['GET'])
@login_required
def storage_state(state_id):
    storages = StorageCage.query.filter(StorageCage.location.has(Location.state_id==state_id)).all()
    storageArray = []
    for stor in storages:
        storObj = {}
        storObj['id']=stor.id
        storObj['name']=stor.name+' - '+stor.location.suburb
        storageArray.append(storObj)
    return jsonify({'storages':storageArray})

@app.route("/storage/area/<int:area_id>",methods=['GET'])
@login_required
def storage_area(area_id):
    storages = StorageCage.query.filter(StorageCage.location.has(Location.area_id==area_id)).all()
    storageArray = []

    for stor in storages:
        storObj = {}
        storObj['id']=stor.id
        storObj['name']=stor.name+' - '+stor.location.suburb
        storageArray.append(storObj)
    return jsonify({'storages':storageArray})

@app.route("/storage/suburb/<suburb>",methods=['GET'])
@login_required
def storage_suburb(suburb):
    storages = StorageCage.query.filter(StorageCage.location.has(Location.suburb==suburb)).all()
    storageArray = []

    for stor in storages:
        storObj = {}
        storObj['id']=stor.id
        storObj['name']=stor.name+' - '+stor.location.suburb
        storageArray.append(storObj)
    return jsonify({'storages':storageArray})

@app.route("/storageInfo/<int:storage_id>",methods=['GET'])
@login_required
def storageInfo(storage_id):
    storage = StorageCage.query.filter_by(id=storage_id).first()

    state = State.query.filter(State.id!=storage.location.state_id).all()
    state.insert(0,State.query.filter_by(id=storage.location.state_id).first())
    stateJson = convertJson(state,True)

    area = Area.query.filter(Area.id!=storage.location.area_id).all()
    area.insert(0,Area.query.filter_by(id=storage.location.area_id).first())
    areaJson = convertJson(area,True)

    suburb = Location.query.filter(Location.id!=storage.location.id).distinct(Location.suburb).all()
    suburb.insert(0,Location.query.filter_by(id=storage.location.id).first())
    suburbJson = convertJson(suburb,False)

    listing=[(lists.id,lists.name) for lists in storage.subscription]
    

    return jsonify({'listing':listing,'state':stateJson,'area':areaJson,'suburb':suburbJson})
