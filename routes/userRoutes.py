
from flask import render_template, url_for, flash, redirect, request, abort, jsonify, make_response
from app import app, db, bcrypt, mail
from forms import *
from models import *
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/users", methods=['GET', 'POST'])
@login_required
def user_all():
    if current_user.role=="Admin":
        searchValue = request.args.get('searchValue')
        if searchValue:
            users = User.query.filter((User.username.ilike('%'+searchValue+'%')))
        else: 
            users = User.query       

        storageCages = StorageCage.query.all()
        userAndStorage = []
        for user in users:
            temp=[]
            temp.append(user)
            temp.append(User_Storage.query.filter_by(user_id=user.id).all())
            userAndStorage.append(temp)
        
        return render_template('user/user.html' , users=userAndStorage,storageCages=storageCages )
    else:
        return render_template('formLayout/noAccess.html')


@app.route("/users_storage/<int:user_id>/<storageSearch>", methods=['GET', 'POST'])
@login_required
def search_storage(user_id,storageSearch):
    if(current_user.role=="Admin"):
        removeStorage = [(user.storage.id,user.storage.name+' - '+user.storage.location.suburb) for user in User_Storage.query.filter_by(user_id=user_id).all()]
        userStorage = [user.storage for user in User_Storage.query.filter_by(user_id=user_id).all()]
        if(storageSearch=="nothing"):
            storageCages = [(stor.id,stor.name+' - '+stor.location.suburb) for stor in StorageCage.query.all() if stor not in userStorage]
        else:
            storageCagesObject=StorageCage.query.filter((StorageCage.name.ilike('%'+storageSearch+'%')) |  (StorageCage.location.has(Location.suburb.ilike('%'+storageSearch+'%')))\
                | (StorageCage.location.has(Location.numberAndStreet.ilike('%'+storageSearch+'%'))) | (StorageCage.location.has(Location.area_loc.has(Area.name.ilike('%'+storageSearch+'%'))))).all()
            storageCages = [(stor.id,stor.name+' - '+stor.location.suburb) for stor in storageCagesObject]
        return jsonify({'storageCages':storageCages, 'removeStorage':removeStorage})
    else:
       return jsonify({'storageCages':[]}) 

@app.route("/add_storage_user", methods=['GET', 'POST'])
@login_required
def add_storage_user():
    if(current_user.role=="Admin"):
        if (request.json!=None):
            if(request.json.get('submit')=="add_user_storage"):
                new_storage_user = User_Storage(user_id=request.json.get('user_id'),storage_id=request.json.get('storage_id'))
                db.session.add(new_storage_user)
                db.session.commit()
                return jsonify({"status":"success"})
        return jsonify({"status":"fail"})
    else:
        return jsonify({"status":"fail"})

@app.route("/remove_storage_user", methods=['GET', 'POST'])
@login_required
def remove_storage_user():
    if(current_user.role=="Admin"):
        if (request.json!=None):
            if(request.json.get('submit')=="remove_user_storage"):
                deleteRecord = User_Storage.query.filter_by(user_id=request.json.get('user_id'),storage_id=request.json.get('storage_id')).first()
                if deleteRecord != None:
                    db.session.delete(deleteRecord)
                    db.session.commit()
                    return jsonify({"status":"success"})
        return jsonify({"status":"fail"})
    else:
        return jsonify({"status":"fail"})


@app.route("/user/search/<searchValue>/<int:storage_id>", methods=['GET','POST'])
@login_required
def userSearch(searchValue,storage_id):
    if(searchValue.lower().strip()=='all'):
        userAll = User.query.all()
    else:
        userAll = User.query.filter((User.username.ilike('%'+searchValue+'%'))).all()
    users = [user for user in userAll if user not in [user.user for user in User_Storage.query.filter_by(storage_id=storage_id)]]
    usersArray = []
    for user in users:
        userObj = {}
        userObj['name']=user.username
        userObj['id']=user.id
        usersArray.append(userObj)

    return jsonify({'usersArray':usersArray})
