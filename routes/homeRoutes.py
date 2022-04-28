
from flask import render_template, url_for, flash, redirect, request, abort, jsonify, make_response
from app import app, db, bcrypt, mail
from forms import *
from models import *
from flask_login import login_user, current_user, logout_user, login_required
from routes.commonRoutes import outputStates

@app.route("/")
@app.route("/home",  methods=['GET'])
@login_required
def home():
	filterProducts = FilterProducts()
	filterProducts.state.choices = insertAll(outputStates())
	filterProducts.storageCage.choices=insertAll([(stor.id,stor.name) for stor in StorageCage.query.all()])
	filterProducts.listing.choices=insertAll([(lists.id,lists.name) for lists in Listing.query.all()])

	stateLabel = 'All'
	areaLabel='All'
	suburbLabel='All'
	bookingLabel=''
	storageCageLabel='All'
	listingLabel='All'

	alloutput=[]
	if(request.args.get('search')=='Filter'):
		state_id= 	request.args.get('state')
		area_id= request.args.get('area')
		suburb = request.args.get('suburb')
		numberOfBooking=request.args.get('numberOfBooking')
		storage_id=request.args.get('storageCage')
		listing_id=request.args.get('listing')
		allStorage=[]
		storages=[]
		
		if suburb not in ['0',None]:
			suburbInfo=Location.query.filter_by(id=int(request.args.get('suburb'))).first().suburb
			suburbLabel=suburbInfo
			allStorage = StorageCage.query.filter(StorageCage.location.has(Location.suburb==suburbInfo)).all()
		elif area_id not in ['0',None] :
			allStorage = StorageCage.query.filter(StorageCage.location.has(Location.area_id==int(area_id))).all()
			areaLabel=Area.query.filter_by(id=area_id).first().name
		elif state_id not in ['0',None]: 
			allStorage = StorageCage.query.filter(StorageCage.location.has(Location.state_id==int(state_id))).all()
			stateLabel=State.query.filter_by(id=state_id).first().name
		else:
			allStorage=StorageCage.query.all()
		if storage_id =='0':
			storages=allStorage
		elif storage_id ==None:
			stroages=[]
			storageCageLabel=''
		else:
			storages=[stor for stor in allStorage if stor.id==int(storage_id)]

		if numberOfBooking in ['',None]:
			booking=0
		else:
			if(int(numberOfBooking)>0):
				booking = int(numberOfBooking)
				bookingLabel=booking
			else:
				booking=0

		for stor in storages:
			filterStorage = Product_Storage.query.filter_by(storage_id=stor.id)
			uniqueProdStor = [prod.product_id for prod in filterStorage.distinct(Product_Storage.product_id).all()]
			productInStorage =[]
			for pid in uniqueProdStor:
				product_storage_info = Product_Storage.query.filter_by(storage_id=stor.id, product_id=pid).first()
				quantity = product_storage_info.quantity
				allLisings=[]
				if listing_id not in ['0',None]:
					if booking>0:
						allLisings = Product_Storage_Listing.query.filter((Product_Storage_Listing.storage_id==stor.id),(Product_Storage_Listing.listing_id==listing_id), (Product_Storage_Listing.product_id==pid),
					 (Product_Storage_Listing.per_booking>0),(quantity/Product_Storage_Listing.per_booking<=booking)).all()
						listingLabel=Listing.query.filter_by(id=listing_id).first().name
					else:
						allLisings = Product_Storage_Listing.query.filter((Product_Storage_Listing.storage_id==stor.id),(Product_Storage_Listing.listing_id==listing_id), (Product_Storage_Listing.product_id==pid)).all()
						listingLabel=Listing.query.filter_by(id=listing_id).first().name
				else:
					if booking>0:
						allLisings = Product_Storage_Listing.query.filter((Product_Storage_Listing.storage_id==stor.id), (Product_Storage_Listing.product_id==pid), (Product_Storage_Listing.per_booking>0)
							,(quantity/Product_Storage_Listing.per_booking<=booking)).all()
					else:
						allLisings = Product_Storage_Listing.query.filter((Product_Storage_Listing.storage_id==stor.id), (Product_Storage_Listing.product_id==pid)).all()
					if(listing_id==None):
						listingLabel=''
				if(len(allLisings)>0):
					productInStorage.append([product_storage_info,allLisings])
			alloutput.extend(productInStorage)
		requestInfo=request.args
	else:
		for stor in StorageCage.query.all():
			filterStorage = Product_Storage.query.filter_by(storage_id=stor.id)
			uniqueProdStor = [prod.product_id for prod in filterStorage.distinct(Product_Storage.product_id).all()]
			productInStorage =[]
			for pid in uniqueProdStor:
				allLisings = Product_Storage_Listing.query.filter((Product_Storage_Listing.storage_id==stor.id), (Product_Storage_Listing.product_id==pid), (Product_Storage_Listing.per_booking>0)).all()
				product_storage_info = Product_Storage.query.filter_by(storage_id=stor.id, product_id=pid).first()
				productInStorage.append([product_storage_info,allLisings])
			alloutput.extend(productInStorage)
		requestInfo=None

	return render_template('home/home.html', filterProducts=filterProducts,alloutput=alloutput, requestInfo={'storage':storageCageLabel,'listing':listingLabel,'state':stateLabel,'area':areaLabel,'suburb':suburbLabel,'booking':bookingLabel})


def insertAll(array):
	array.insert(0,(0,"All"))
	return array

@app.route("/about")
def about():
	return render_template('about.html', title='About')