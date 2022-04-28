from flask import render_template, url_for, flash, redirect, request, abort, jsonify, make_response
from app import app, db, bcrypt, mail
from forms import *
from models import *
from flask_login import login_user, current_user, logout_user, login_required
from routes.commonRoutes import outputStates,findSupplierForm,convertJson,createNewVerify,send_reset_email_verification,updateVerify
import math

@app.route("/verification/updateBooking/<int:verify_id>")
@login_required
def verifyUpdateBooking(verify_id):    
    verifyInfo = Verify.query.get_or_404(verify_id)
    user=User.query.filter_by(id=verifyInfo.user_id).first()
    if(current_user.role=='Admin' or current_user.id==user.id):
        verifyListingInfo  = Verify_Listing_Booking.query.filter_by(verify_id=verify_id).first()
        listing = Listing.query.filter_by(id=verifyListingInfo.listing_id).first()

        updateBooking =UpdateBookings()
        updateBooking.up_listing.choices=[(listing.id,listing.name +' - '+listing.location.suburb)]
        updateBooking.up_bookings.data=verifyListingInfo.booking
        updateBooking.up_comment.data=verifyInfo.comment
        return render_template('commonTemps/storage/verifyUpdateBooking.html',user=user, listing=listing, verifyInfo=verifyInfo,updateBooking=updateBooking, role=current_user.role)
    else:
        return render_template('formLayout/noAccess.html')




@app.route("/update/updateBooking" , methods=['GET', 'POST'])
@login_required
def updateUpdateBooking():
    if(current_user.role=="Admin"):
        if (request.json!=None):
            if(request.json.get('submit')=="updateBooking"):
                listing_id= request.json.get('listing_id')
                booking= request.json.get('booking')
                comment=request.json.get('comment')
                verifyId=None
                if(request.json.get('verifyId')!=""):
                    verifyId=request.json.get('verifyId')
                    updateVerify(comment,verifyId)
                all_storages = Listing.query.filter_by(id=listing_id).first().subscription
                for stor in all_storages:
                    for prodStor in Product_Storage.query.filter_by(storage_id=stor.id).all():
                        productStorageListingInfo=Product_Storage_Listing.query.filter_by(product_id=prodStor.product_id,listing_id=listing_id,storage_id=stor.id).first()
                        if(productStorageListingInfo is None):
                            newRecord=Product_Storage_Listing(product_id=prodStor.product_id,listing_id=listing_id,storage_id=stor.id,supplier_id=None,orderentity="Company")
                            db.session.add(newRecord)
                            db.session.commit()
                            perBooking=0
                            print("created")
                        else:
                            perBooking=productStorageListingInfo.per_booking
                        if prodStor.quantity>math.ceil(int(booking)*perBooking):
                            prodStor.quantity-=math.ceil(int(booking)*perBooking)
                        else:
                            prodStor.quantity=0
                Listing.query.filter_by(id=listing_id).last_update=datetime.utcnow()
                db.session.commit()
                return jsonify({'status':"success"})
            return jsonify({'status':'fail'})
        else:
            return jsonify({'status':"fail", "reason":"No Post"})
    else:
        if(request.json!=None):
            if(request.json.get('submit')=="updateBooking"):
                comment=request.json.get('comment')
                new_id=createNewVerify("Update Booking", comment)
                listing_id= request.json.get('listing_id')
                booking= request.json.get('booking')
                info = request.json.get("info")
                listing=Listing.query.filter_by(id=listing_id).first()
                newBooking = Verify_Listing_Booking(verify_id=new_id,listing_id=listing_id,booking=booking)
                db.session.add(newBooking)
                db.session.commit()
                send_reset_email_verification("booking",new_id, current_user, listing)
                return jsonify({'status':"success"})
        else:
            return jsonify({'status':"fail", "reason":"No Admin"})

@app.route("/verification/updateBooking/remove/<int:verify_id>")
@login_required
def removUpdateBookingTransfer(verify_id):    
    verifyInfo = Verify.query.get_or_404(verify_id)
    user=User.query.filter_by(id=verifyInfo.user_id).first()
    if(current_user.role=='Admin' or current_user.id==user.id):
        Verify_Listing_Booking  .query.filter_by(verify_id=verify_id).delete(synchronize_session=False)
        Verify.query.filter_by(id=verify_id).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({'status':"success"})
    else:
        return jsonify({'status':"fail"})
