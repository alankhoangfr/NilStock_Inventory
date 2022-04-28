from flask import render_template, url_for, flash, redirect, request, abort, jsonify, make_response
from app import app, db, bcrypt, mail
from forms import *
from models import *
from flask_login import login_user, current_user, logout_user, login_required
from routes.commonRoutes import outputStates,findSupplierForm,convertJson,createNewVerify,send_reset_email_verification,updateVerify



@app.route("/transfer/<int:storage_id>",methods=['GET'])
@login_required
def transfer(storage_id):
    common =CommonProducts()
    storage=StorageCage.query.filter_by(id=storage_id).first()
    common.storageCage2.choices =[(stor.id,stor.name+" - "+stor.location.suburb) for stor in StorageCage.query.all() if stor.id!=storage_id]
    columnName = common.storageCage2.choices[0][1]
    if(request.args.get('submit')=='Find'):
        selectedStorage = request.args.get('storageCage2')
        stor2 = StorageCage.query.filter_by(id=selectedStorage).first()
        columnName = stor2.name +" - "+stor2.location.suburb

        combine = (storage_id,selectedStorage)
        allProducts = Product_Storage.query.filter(Product_Storage.storage_id.in_(combine))
        uniqueProducts = allProducts.distinct(Product_Storage.product_id).all()

        commonProducts=[]
        for pid in uniqueProducts:
            count = 0
            pStororage=[]
            infoStr = {}
            for st in combine:
                pstor=Product_Storage.query.filter_by(storage_id=st,product_id=pid.product_id).all()
                if len(pstor):
                    pStororage.extend(pstor)
                    infoStr[str(pstor[0].storage.name)]=pstor[0].quantity
                    count+=1
            if count==2:
                pStororage.append(infoStr)
                commonProducts.append(pStororage)
        return render_template('commonTemps/storage/transfer.html',common=common,stor2=stor2, storage=storage, columnName=columnName,commonProducts=commonProducts,
            site="Transfer",role=current_user.role,completed=False)



    return render_template('commonTemps/storage/transfer.html',common=common, storage=storage, columnName=columnName,site="Transfer")



@app.route("/verification/transfer/<int:verify_id>")
@login_required
def verifyTransfer(verify_id):    
    verifyInfo = Verify.query.get_or_404(verify_id)
    user=User.query.filter_by(id=verifyInfo.user_id).first()
    if(current_user.role=='Admin' or current_user.id==user.id):
        storage_id1  = Verify_Product_Storage.query.filter_by(verify_id=verify_id).first().storage_id
        storage = StorageCage.query.filter_by(id=storage_id1).first()

        verifyProductStorage=Verify_Product_Storage.query.filter_by(verify_id=verify_id)
        

        uniqueProdStor = [prod.product_id for prod in verifyProductStorage.distinct(Verify_Product_Storage.product_id).all()]
        storage_id2 = [stor.storage_id for stor in verifyProductStorage.distinct(Verify_Product_Storage.storage_id).all() if stor.storage_id != storage_id1][0]
        stor2 = StorageCage.query.filter_by(id=storage_id2).first()

        columnName=stor2.name +" - "+stor2.location.suburb
        commonProducts =[]

        for pid in uniqueProdStor:
            pStororage=[]
            infoStr = {}
            product_storage_info1 = Verify_Product_Storage.query.filter_by(verify_id=verify_id,storage_id=storage_id1, product_id=pid).all()
            product_storage_info2 = Verify_Product_Storage.query.filter_by(verify_id=verify_id,storage_id=storage_id2, product_id=pid).all()
            product_storage_info1_real = Product_Storage.query.filter_by(storage_id=storage_id1, product_id=pid).all()
            product_storage_info2_real = Product_Storage.query.filter_by(storage_id=storage_id2, product_id=pid).all()
            pStororage.extend(product_storage_info1)
            pStororage.extend(product_storage_info2)
            infoStr[str(product_storage_info1_real[0].storage.name)]=product_storage_info1_real[0].quantity
            infoStr[str(product_storage_info2_real[0].storage.name)]=product_storage_info2_real[0].quantity
            quantityTransfered = product_storage_info1_real[0].quantity-product_storage_info1[0].quantity
            pStororage.append(infoStr) 
            pStororage.append(quantityTransfered) 
            commonProducts.append(pStororage)

        if(verifyInfo.user_id_confirm==None and verifyInfo.date_verified==None):
            completed=False
        else:
            completed=True
        return render_template('commonTemps/storage/transfer.html', commonProducts=commonProducts,storage=storage, columnName=columnName,stor2=stor2,
            site="verify", user=user, verifyInfo=verifyInfo, role=current_user.role, completed=completed)
    else:
        return render_template('formLayout/noAccess.html')




@app.route("/update/transfer/" , methods=['GET', 'POST'])
@login_required
def updateTransfer():
    if(current_user.role=="Admin"):
        if (request.json!=None):
            if(request.json.get('submit')=="transfer"):
                storage_id1= request.json.get('storage_id1')
                storage_id2= request.json.get('storage_id2')
                comment=request.json.get('comment')
                verifyId=None
                if(request.json.get('verifyId')!=""):
                    verifyId=request.json.get('verifyId')
                    updateVerify(comment,verifyId)
                info = request.json.get("info")
                for productInfo in info:
                    product_id=productInfo['product_id']
                    quantity1=productInfo['quantity1']
                    quantity2=productInfo['quantity2']
                    prod_stor1 = Product_Storage.query.filter_by(storage_id=storage_id1, product_id=product_id)
                    prod_stor2 = Product_Storage.query.filter_by(storage_id=storage_id2, product_id=product_id)
                    prod_stor1.first().quantity=quantity1
                    prod_stor2.first().quantity=quantity2
                    ver_prod_stor1=None
                    ver_prod_stor2=None
                    if verifyId !=None:
                        ver_prod_stor1=Verify_Product_Storage.query.filter_by(verify_id=verifyId,storage_id=storage_id1, product_id=product_id)
                        ver_prod_stor2=Verify_Product_Storage.query.filter_by(verify_id=verifyId,storage_id=storage_id2, product_id=product_id)
                        ver_prod_stor1.first().quantity=quantity1 
                        ver_prod_stor2.first().quantity=quantity2 
                    db.session.commit()
                return jsonify({'status':"success"})
            return jsonify({'status':'fail'})
        else:
            return jsonify({'status':"fail", "reason":"No Post"})
    else:
        if(request.json!=None):
            if(request.json.get('submit')=="transfer"):
                comment=request.json.get('comment')
                new_id=createNewVerify("Transfer", comment)
                storage_id1= request.json.get('storage_id1')
                storage_id2= request.json.get('storage_id2')
                info = request.json.get("info")
                for productInfo in info:
                    product_id=productInfo['product_id']
                    quantity1=productInfo['quantity1']
                    quantity2=productInfo['quantity2']
                    newProductStorage1=Verify_Product_Storage(verify_id=new_id,product_id=product_id,storage_id=storage_id1,quantity=quantity1)
                    newProductStorage2=Verify_Product_Storage(verify_id=new_id,product_id=product_id,storage_id=storage_id2,quantity=quantity2)
                    db.session.add(newProductStorage1)
                    db.session.add(newProductStorage2)
                    db.session.commit()
                storage = StorageCage.query.filter_by(id=storage_id1).first()
                send_reset_email_verification("transfer",new_id, current_user, storage)
                return jsonify({'status':"success"})
        else:
            return jsonify({'status':"fail", "reason":"No Admin"})



@app.route("/verification/transfer/remove/<int:verify_id>")
@login_required
def removeVerifyTransfer(verify_id):    
    verifyInfo = Verify.query.get_or_404(verify_id)
    user=User.query.filter_by(id=verifyInfo.user_id).first()
    if(current_user.role=='Admin' or current_user.id==user.id):
        Verify_Product_Storage.query.filter_by(verify_id=verify_id).delete(synchronize_session=False)
        Verify.query.filter_by(id=verify_id).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({'status':"success"})
    else:
        return jsonify({'status':"fail"})
