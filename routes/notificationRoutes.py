
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, jsonify, make_response
from app import app, db, bcrypt, mail
from forms import *
from models import *
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime,timedelta 



@app.route("/notification", methods=['GET','POST'])
def notification():
    
    page = request.args.get('page', 1, type=int)
    current_time = datetime.utcnow()
    four_weeks_ago = current_time - timedelta(weeks=4)
    posts = Post.query.filter(Post.date_posted>four_weeks_ago).order_by(Post.date_posted.desc()).paginate(page=page, per_page=6)

    stocktakeAll = Verify_Product_Storage.query.distinct(Verify_Product_Storage.verify_id).all()
    stocktakeAll.extend(Order_Product.query.distinct(Order_Product.verify_id).all())
    allUpdatebooking=Verify_Listing_Booking.query.distinct(Verify_Listing_Booking.verify_id).all()
    allUpdatebooking_verfiyid=[(v.verify_id) for v in allUpdatebooking]
    if current_user.role=="Manager":
        validStorageId = [user.user_id for user in User_Storage.query.filter_by(user_id=current_user.id).all()]
        stocktake=[s for s in stocktakeAll if s.storage_id in validStorageId]
        validVerify = [(v.id) for v in Verify.query.filter(Verify.id.in_(allUpdatebooking_verfiyid),(Verify.user_id==current_user.id)).distinct(Verify.id).all()]
        stocktake.extend([s for s in allUpdatebooking if s.verify_id in validVerify])
    else:
        stocktakeAll.extend(allUpdatebooking)
        stocktake=stocktakeAll

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
            if(st.title=="Update Booking"):
                temp["id"]=stock.listing_id
                temp["name"]=stock.listing.name+' - '+stock.listing.location.suburb
            else:
                temp["id"]=stock.storage_id
                temp["name"]=stock.storage.name+' - '+stock.storage.location.suburb
            if(st.title=="Stocktake"):
                temp["url"]="verifyStocktake"
            elif(st.title=="Transfer"):
                temp["url"]="verifyTransfer"
            elif(st.title=="Shopping"):
                temp["url"]="verifyShopping"
            elif(st.title=="Update Booking"):
                temp["url"]="verifyUpdateBooking"
            notificationVerify.append(temp)
            


    form = PostForm()


    return render_template('notification/notification.html', posts=posts,notificationVerify=notificationVerify, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    if (request.json!=None):
        if request.json.get('submit')=='post':
            post = Post(title=request.json.get('title'), content=request.json.get('content'), author=current_user)
            db.session.add(post)
            db.session.commit()
            return jsonify({'status':'success'})
    return jsonify({'status':'fail'})



@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user/user_posts.html', posts=posts, user=user)


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    userPost = User.query.filter_by(id=post.user_id).first()
    image_file = url_for('static', filename='pictures/profile/' + userPost.image_file)
    return render_template('notification/post.html', post=post, role=current_user.role,image_file=image_file)

'''
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('notification/create_post.html', 
                           form=form, legend='Update Post')
'''

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('notification'))


 