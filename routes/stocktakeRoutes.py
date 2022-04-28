import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, jsonify, make_response
from app import app, db, bcrypt, mail
from forms import *
from models import *
from flask_login import login_user, current_user, logout_user, login_required
import phonenumbers
from datetime import datetime
from routes.commonRoutes import findSupplierForm,send_reset_email_verification,createNewVerify,updateVerify,searchButton,outputBuyers





@app.route("/stocktake/<int:storage_id>" , methods=['GET', 'POST'])
@login_required
def stocktake(storage_id): 
    storage = StorageCage.query.get_or_404(storage_id)
    filterStorage = Product_Storage.query.filter_by(storage_id=storage_id)
    listing = storage.subscription
    products = searchButton(Product)
    fs=findSupplierForm(storage)

    uniqueProdStor = [prod.product_id for prod in filterStorage.distinct(Product_Storage.product_id).all() if prod.product in products]
    productInStorage =[]
    for pid in uniqueProdStor:
        
        product_storage_info = Product_Storage.query.filter_by(storage_id=storage_id, product_id=pid).first()
        infoStr = {}
        infoStr["product_id"]=product_storage_info.product.id
        infoStr["Quantity"]=product_storage_info.quantity
        allListingInfo={}
        allListings = []
        for lis in listing:
            listingsInfo={}
            lisStorageProductInfo=Product_Storage_Listing.query.filter((Product_Storage_Listing.storage_id==storage_id), (Product_Storage_Listing.product_id==pid), 
                (Product_Storage_Listing.listing_id==lis.id)).first()
            if(lisStorageProductInfo is None):
                newRecord=Product_Storage_Listing(product_id=pid,storage_id=storage_id,listing_id=lis.id,supplier_id=None,orderentity="Company")
                db.session.add(newRecord)
                db.session.commit()
                print("created")
                allListings.append(newRecord)
            else:
                allListings.append(lisStorageProductInfo)
                listingsInfo["Per_Booking"]=str(lisStorageProductInfo.per_booking)
                if(lisStorageProductInfo.supplier!=None):
                    listingsInfo["Supplier"] =str(lisStorageProductInfo.supplier.name) +" - "+str(lisStorageProductInfo.supplier.location.suburb)
                else:
                    listingsInfo["Supplier"]=None
                listingsInfo["Buyer"]=str(lisStorageProductInfo.orderentity)
                allListingInfo[lisStorageProductInfo.listing.name]=listingsInfo
        infoStr["Listings"]=allListingInfo
        productInStorage.append([product_storage_info,allListings,infoStr])
    

    role=current_user.role
    return render_template('commonTemps/storage/stocktakeAndShopping.html',productInStorage=productInStorage, storage=storage, buyers=outputBuyers(), areaSuppliers=fs["areaSuppliers"],
     fs=fs["fs"], role=role, site="stocktake", verifyInfo=None, completed=False)


@app.route("/verification/stocktake/<int:verify_id>")
@login_required
def verifyStocktake(verify_id):    
    verifyInfo = Verify.query.get_or_404(verify_id)
    user=User.query.filter_by(id=verifyInfo.user_id).first()
    if(current_user.role=='Admin' or current_user.id==user.id):
        storage_id  = Verify_Product_Storage.query.filter_by(verify_id=verify_id).first().storage_id
        storage = StorageCage.query.filter_by(id=storage_id).first()

        verifyProductStorage=Verify_Product_Storage.query.filter_by(verify_id=verify_id, storage_id =storage_id)

        fs=findSupplierForm(storage)

        products = searchButton(Product)

        uniqueProdStor = [prod.product_id for prod in verifyProductStorage.distinct(Verify_Product_Storage.product_id).all() if prod.product in products]
        productInStorage =[]
        for pid in uniqueProdStor:
            allLisings = Verify_Product_Storage_Listing.query.filter((Verify_Product_Storage_Listing.verify_id==verify_id),(Verify_Product_Storage_Listing.storage_id==storage_id), (Verify_Product_Storage_Listing.product_id==pid)).all()
            product_storage_info = Verify_Product_Storage.query.filter_by(verify_id=verify_id,storage_id=storage_id, product_id=pid).first()
            allLisings_real = Product_Storage_Listing.query.filter((Product_Storage_Listing.storage_id==storage_id), (Product_Storage_Listing.product_id==pid)).all()
            product_storage_info_real = Product_Storage.query.filter_by(storage_id=storage_id, product_id=pid).first()
            infoStr = {}
            infoStr["product_id"]=product_storage_info.product.id
            infoStr["Quantity"]=product_storage_info_real.quantity
            allListingInfo={}
            for lis in allLisings_real:
                listingsInfo={}
                listingsInfo["Per_Booking"]=str(lis.per_booking)
                if(lis.supplier!=None):
                    listingsInfo["Supplier"] =str(lis.supplier.name) +" - "+str(lis.supplier.location.suburb)
                else:
                    listingsInfo["Supplier"]=None
                listingsInfo["Buyer"]=str(lis.orderentity)
                allListingInfo[lis.listing.name]=listingsInfo
            infoStr["Listings"]=allListingInfo
            productInStorage.append([product_storage_info,allLisings,infoStr])


        if(verifyInfo.user_id_confirm==None and verifyInfo.date_verified==None):
            completed=False
        else:
            completed=True
        return render_template('commonTemps/storage/stocktakeAndShopping.html', productInStorage=productInStorage,storage=storage,buyers =outputBuyers(), areaSuppliers=fs["areaSuppliers"], 
            fs=fs["fs"], site="verifyStocktake", user=user, verifyInfo=verifyInfo, role=current_user.role, completed=completed)
    else:
        return render_template('formLayout/noAccess.html')




@app.route("/update/stocktake/" , methods=['GET', 'POST'])
@login_required
def updateStocktake():
    print(request.json)
    if(current_user.role=='Admin'):
        if (request.json!=None):
            if(request.json.get('submit')=="stocktake"):
                storage_id= request.json.get('storage_id')
                comment=request.json.get('comment')
                verifyId=None
                if(request.json.get('verifyId')!=""):
                    verifyId=request.json.get('verifyId')
                    updateVerify(comment,verifyId)
                info = request.json.get("info")

                for productInfo in info:
                    product_id=productInfo['product_id']
                    quantity=productInfo['quantity']
                    prod_stor = Product_Storage.query.filter_by(storage_id=storage_id, product_id=product_id)
                    ver_prod_stor=None
                    if verifyId !=None:
                        ver_prod_stor=Verify_Product_Storage.query.filter_by(verify_id=verifyId,storage_id=storage_id, product_id=product_id)
                    if(prod_stor.scalar() is not None):
                        prod_stor.first().quantity=quantity
                        if verifyId!=None:
                            ver_prod_stor.first().quantity=quantity 
                        db.session.commit()
                    else:
                        newRow= Product_Storage(product_id=product_id, storage_id=storage_id, quantity=quantity)
                        db.session.add(newRow)
                        db.session.commit()
                    for listingInfo in productInfo['listingInfo']:
                        listing_id=listingInfo['listing_id']
                        orderentity = listingInfo['buyer']
                        try:
                            supplier_id = listingInfo['supplier_id']
                        except:
                            supplier_id=None
                        try:
                            per_booking = listingInfo['per_booking']
                        except:
                            per_booking=0
                        prod_stor_list = Product_Storage_Listing.query.filter_by(storage_id=storage_id, product_id=product_id, listing_id=listing_id)
                        ver_prod_stor_list=None
                        if verifyId !=None:
                            ver_prod_stor_list=Verify_Product_Storage_Listing.query.filter_by(verify_id=verifyId,storage_id=storage_id, product_id=product_id, listing_id=listing_id)
                        if(prod_stor_list.scalar() is not None):
                            prod_stor_list.first().orderentity=orderentity
                            prod_stor_list.first().supplier_id=supplier_id
                            prod_stor_list.first().per_booking=per_booking
                            if ver_prod_stor_list!=None:
                                ver_prod_stor_list.first().orderentity=orderentity
                                ver_prod_stor_list.first().supplier_id=supplier_id
                                ver_prod_stor_list.first().per_booking=per_booking
                            db.session.commit()
                        else:
                            newRow= Product_Storage_Listing(product_id=product_id, storage_id=storage_id,listing_id=listing_id,supplier_id=supplier_id,orderentity=orderentity, per_booking=per_booking)
                            db.session.add(newRow)
                            db.session.commit()
                return jsonify({'status':"success"})

            return jsonify({'status':"fail"})
        else:
            return jsonify({'status':"fail", "reason":"No Post"})
    else:
        if (request.json!=None):
            if(request.json.get('submit')=="stocktake"):
                comment=request.json.get('comment')
                new_id=createNewVerify("Stocktake",comment)
                storage_id= request.json.get('storage_id')
                info = request.json.get("info")
                for productInfo in info:
                    product_id=productInfo['product_id']
                    quantity=productInfo['quantity']
                    newProductStorage=Verify_Product_Storage(verify_id=new_id,product_id=product_id,storage_id=storage_id,quantity=quantity)
                    db.session.add(newProductStorage)
                    db.session.commit()

                    for listingInfo in productInfo['listingInfo']:

                        listing_id=listingInfo['listing_id']
                        orderentity = listingInfo['buyer']
                        try:
                            supplier_id = listingInfo['supplier_id']
                        except:
                            supplier_id=None
                        try:
                            per_booking = listingInfo['per_booking']
                        except:
                            per_booking=0
                        newProductStorageListing=Verify_Product_Storage_Listing(verify_id=new_id,product_id=product_id,listing_id=listing_id,storage_id=storage_id,supplier_id=supplier_id,orderentity=orderentity, per_booking=per_booking)
                        db.session.add(newProductStorageListing)
                        db.session.commit()
                storage = StorageCage.query.filter_by(id=storage_id).first()
                send_reset_email_verification("stocktake",new_id, current_user, storage)
            return jsonify({'status':"success"})
        else:
            return jsonify({'status':"fail", "reason":"No Admin"})

@app.route("/verification/stocktake/remove/<int:verify_id>")
@login_required
def removeVerifyStocktake(verify_id):    
    verifyInfo = Verify.query.get_or_404(verify_id)
    user=User.query.filter_by(id=verifyInfo.user_id).first()
    if(current_user.role=='Admin' or current_user.id==user.id):
        Verify_Product_Storage_Listing.query.filter_by(verify_id=verify_id).delete(synchronize_session=False)
        Verify_Product_Storage.query.filter_by(verify_id=verify_id).delete(synchronize_session=False)
        Verify.query.filter_by(id=verify_id).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({'status':"success"})
    else:
        return jsonify({'status':"fail"})
