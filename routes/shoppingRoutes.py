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




@app.route("/shopping/<int:storage_id>" , methods=['GET', 'POST'])
@login_required
def shopping(storage_id): 
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
     fs=fs["fs"], role=role, site="shopping", verifyInfo=None, completed=False)


@app.route("/verification/shopping/<int:verify_id>")
@login_required
def verifyShopping(verify_id):    
    verifyInfo = Verify.query.get_or_404(verify_id)
    storage_id  = Order_Product.query.filter_by(verify_id=verify_id).first().storage_id
    user=User.query.filter_by(id=verifyInfo.user_id).first()
    validUsersId = [user.user_id for user in User_Storage.query.filter_by(storage_id=storage_id).all()]
    validUser = False
    if current_user.id in validUsersId:
        validUser=True
    if(current_user.role=='Admin' or validUser):
        
        storage = StorageCage.query.filter_by(id=storage_id).first()

        products = searchButton(Product)

        filterStorage = Product_Storage.query.filter_by(storage_id=storage.id)
        uniqueProdStor = [prod.product_id for prod in filterStorage.distinct(Product_Storage.product_id).all() if prod.product in products]
        productInStorage =[]
        for pid in uniqueProdStor:
            allListings = Product_Storage_Listing.query.filter((Product_Storage_Listing.storage_id==storage_id), (Product_Storage_Listing.product_id==pid)).all()
            product_storage_info = Product_Storage.query.filter_by(storage_id=storage_id, product_id=pid).first()
            product_storage_order = Order_Product.query.filter_by(storage_id=storage_id, product_id=pid,verify_id=verify_id).first()
             
            productInStorage.append([product_storage_info,allListings,product_storage_order])

        if(verifyInfo.user_id_confirm==None and verifyInfo.date_verified==None):
            completed=False
        else:
            completed=True
        if(current_user.role=="Admin"):
            shoppingStatus=["Ordered","Dispatched","Delivered","Verified"]
        else:
            shoppingStatus=["Ordered","Dispatched","Delivered"]
        return render_template('commonTemps/storage/stocktakeAndShopping.html', productInStorage=productInStorage,storage=storage,
            site="verifyShopping", user=user, verifyInfo=verifyInfo, role=current_user.role, completed=completed,
            shoppingStatus=shoppingStatus, validUser=validUser)
    else:
        return render_template('formLayout/noAccess.html')





@app.route("/update/shopping/" , methods=['GET', 'POST'])
@login_required
def updateShopping():
    if(request.json.get('submit')=='sendShopping'):
        storage_id= request.json.get('storage_id')
        comment=request.json.get('comment')
        new_id=createNewVerify("Shopping", comment)
        info = request.json.get("info")
        if(new_id!=None):
            for productInfo in info:
                product_id=productInfo['product_id']
                quantity=productInfo['quantity']
                order_product_storage=Order_Product(verify_id=new_id,storage_id=storage_id, product_id=product_id,status="Ordered",quantity=quantity)
                db.session.add(order_product_storage)
                db.session.commit()
            if(current_user.role=="Manager"):
                storage = StorageCage.query.filter_by(id=storage_id).first()
                send_reset_email_verification("shopping",new_id, current_user, storage)
            return jsonify({'status':"success"})
        return jsonify({'status':"fail",'reason':"Not valid verfiyId"})
    else:
        if(current_user.role=='Admin'):
            if (request.json!=None):
                if(request.json.get('submit')=="verifyShopping"):
                    storage_id= request.json.get('storage_id')
                    comment=request.json.get('comment')
                    verifyId=request.json.get('verifyId')
                    info = request.json.get("info")
                    countVerified=0
                    if(verifyId!=None):
                        for productInfo in info:
                            product_id=productInfo['product_id']
                            quantity=productInfo['quantity']
                            status=productInfo['status']
                            prod_stor = Product_Storage.query.filter_by(storage_id=storage_id, product_id=product_id)
                            ver_prod_stor=Order_Product.query.filter_by(verify_id=verifyId,storage_id=storage_id, product_id=product_id)
                            if(status=="Verified"):
                                countVerified+=1
                            if(status=="Verified" and ver_prod_stor.first().status!="Verified"):
                                ver_prod_stor.first().status=status
                                ver_prod_stor.first().quantity=quantity
                                ver_prod_stor.first().status_posted=datetime.utcnow()
                                prod_stor.first().quantity=quantity
                                db.session.commit()
                            elif(status!="Verified" and ver_prod_stor.first().status!="Verified"):
                                ver_prod_stor.first().status=status
                                ver_prod_stor.first().quantity=quantity
                                ver_prod_stor.first().status_posted=datetime.utcnow()
                                db.session.commit()
                        verifyInfo=Verify.query.filter_by(id=verifyId).first()
                        if(countVerified==len(info)):
                            verifyInfo.user_id_confirm=current_user.id
                            verifyInfo.date_verified=datetime.utcnow()
                            verifyInfo.comment=comment
                            db.session.commit()
                        else:
                            verifyInfo.comment=comment
                            db.session.commit()
                        return jsonify({'status':"success"})

                    return jsonify({'status':"fail",'reason':"Not valid verfiyId"})
                return jsonify({'status':"fail","reason":"not correct submit"})
            else:
                return jsonify({'status':"fail", "reason":"No Post"})
        else:
            if (request.json!=None):
                if(request.json.get('submit')=="verifyShopping"):
                    comment=request.json.get('comment')
                    storage_id= request.json.get('storage_id')
                    info = request.json.get("info")
                    verifyId=request.json.get('verifyId')
                    if(verifyId!=None):
                        verifyInfo=Verify.query.filter_by(id=verifyId).first()
                        verifyInfo.comment=comment
                        for productInfo in info:
                            product_id=productInfo['product_id']
                            quantity=productInfo['quantity']
                            status=productInfo['status']
                            prod_stor = Product_Storage.query.filter_by(storage_id=storage_id, product_id=product_id)
                            ver_prod_stor=Order_Product.query.filter_by(verify_id=verifyId,storage_id=storage_id, product_id=product_id)
                            if(status!="Verified" and ver_prod_stor.first().status!="Verified"):
                                ver_prod_stor.first().status=status
                                ver_prod_stor.first().quantity=quantity
                                ver_prod_stor.first().status_posted=datetime.utcnow()
                                db.session.commit()
                        return jsonify({'status':"success"})
                    return jsonify({'status':"fail",'reason':"Not valid verfiyId"})
                return jsonify({'status':"fail","reason":"not correct submit"})
            else:
                return jsonify({'status':"fail", "reason":"No Post"})
        return jsonify({'status':"fail", "reason":"No valid entry"})

@app.route("/verification/shopping/remove/<int:verify_id>")
@login_required
def removeVerifyShopping(verify_id):    
    verifyInfo = Verify.query.get_or_404(verify_id)
    user=User.query.filter_by(id=verifyInfo.user_id).first()
    if(current_user.role=='Admin' or current_user.id==user.id):
        Order_Product.query.filter_by(verify_id=verify_id).delete(synchronize_session=False)
        Verify.query.filter_by(id=verify_id).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({'status':"success"})
    else:
        return jsonify({'status':"fail"})
