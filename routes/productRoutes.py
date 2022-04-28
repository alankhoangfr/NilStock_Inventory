
from flask import render_template, url_for, flash, redirect, request, abort, jsonify, make_response
from app import app, db, bcrypt, mail
from forms import *
from models import *
from flask_login import login_user, current_user, logout_user, login_required
from routes.commonRoutes import save_picture




@app.route("/product", methods=['GET','POST'])
@login_required
def products():
    page = request.args.get('page', 1, type=int)

    searchValue = request.args.get('searchValue')

    if searchValue:
        products = Product.query.filter((Product.name.ilike('%'+searchValue+'%')) | (Product.comment.ilike('%'+searchValue+'%'))).all()
    else: 
        products = Product.query.all()

    form =AddProduct()
    form.ap_category.choices=[(int(cate.id),cate.name) for cate in Category.query.all()]
    if form.validate_on_submit():
        print(form)
        image_file = 'default.jpg'
        if form.ap_picture.data:
            picture_file = save_picture('product','',form.ap_picture.data)
            image_file = picture_file
        size = str(form.ap_size.data)+' '+form.ap_size_name.data
        newproduct = Product(name=form.ap_name.data,size=size, subcategory_id=form.ap_subcategory.data, image_file=image_file, comment=form.ap_comment.data)
        db.session.add(newproduct)
        db.session.commit()
        comment = form.ap_name.data+' has been added!'
        flash(str(comment), 'success')
        return redirect(url_for('products'))

    return render_template('product/product.html', products=products, addProduct = form)


@app.route("/product/search/<searchValue>", methods=['GET','POST'])
@login_required
def productSearch(searchValue):
    if(searchValue.lower().strip()=='all'):
        products = Product.query.all()
    else:
        products = Product.query.filter((Product.name.ilike('%'+searchValue+'%')) | (Product.comment.ilike('%'+searchValue+'%'))).all()
    productsArray = []
    for prod in products:
        prodObj = {}
        prodObj['name']=prod.name+', '+prod.size
        prodObj['id']=prod.id
        productsArray.append(prodObj)

    return jsonify({'productData':productsArray})



@app.route("/product/<int:product_id>", methods=['GET','POST'])
@login_required
def productsInd(product_id):
    product = Product.query.get_or_404(product_id)
    form = UpdateProductForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture('product',product.image_file,form.picture.data)
            product.image_file = picture_file
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('productsInd', product_id=product_id))
    storageListingArray = Product_Storage_Listing.query.filter_by(product_id=product_id)
    storageProductArray = Product_Storage.query.filter_by(product_id=product_id)
    storages = [storageListing for storageListing in storageProductArray.distinct(Product_Storage.storage_id).all()]
    listings = [storageListing for storageListing in storageListingArray.distinct(Product_Storage_Listing.listing_id).all()]
    return render_template('product/productInd.html', product=product , form=form, storages=storages, listings =listings)


@app.route("/product/storage/listing/add", methods=['GET','POST'])
@login_required
def productStorageListingAdd():
    if (request.json!=None):
        if request.json.get('submit')=='addProductListingStorage':
            storage_id = request.json.get('storage_id')
            product_id = request.json.get('product_id')
            quantity = request.json.get('quantity')
            storageCage= StorageCage.query.filter_by(id=storage_id).all()
            if(len(storageCage)==0):
                return jsonify({'status':'fail', 'reason':'Storage Cage does not exist'})
            product= Product.query.filter_by(id=product_id).all()
            if(len(product)==0):
                return jsonify({'status':'fail', 'reason':'Product does not exist'})
            
            if(quantity==''):
                quantity=0
            else:
                quantity=int(quantity)
            ps=Product_Storage(
                product_id=product_id,
                storage_id=storage_id,
                quantity=quantity)
            db.session.add(ps)
            db.session.commit()
            info = request.json.get('info')

            for listingId in info:
                if(info[listingId].get('supplier_id')!=None and len(info[listingId].get('buyer'))>0 and
                    len(info[listingId].get('booking'))>0):
                    psl = Product_Storage_Listing(
                        product_id=product_id,
                        storage_id=storage_id,
                        listing_id=listingId,
                        supplier_id=info[listingId].get('supplier_id'),
                        orderentity=info[listingId].get('buyer'),
                        per_booking=info[listingId].get('booking'))
                else:
                    psl = Product_Storage_Listing(
                        product_id=product_id,
                        storage_id=storage_id,
                        listing_id=listingId
                        )
                db.session.add(psl)
                db.session.commit()
            return jsonify({'status':'Success'})
        return jsonify({'status':'fail'})
    else:
        return jsonify({'status':'fail', 'reason':'No data'})


@app.route("/product/storage/listing/remove", methods=['GET','POST'])
@login_required
def productStorageListingRemove():
    if (request.json!=None):
        if request.json.get('submit')=='productStorageListingRemove':
            storage_id = request.json.get('storage_id')
            product_id = request.json.get('product_id')
            Product_Storage_Listing.query.filter_by(product_id =product_id, storage_id=storage_id).delete(synchronize_session=False)
            Product_Storage.query.filter_by(product_id =product_id, storage_id=storage_id).delete(synchronize_session=False)
            db.session.commit()
            return jsonify({'status':'Success'})
        return jsonify({'status':'fail'})
    else:
        return jsonify({'status':'fail', 'reason':'No data'})

     