from flask import render_template, url_for, flash, redirect, request, abort, jsonify, make_response
from app import app, db, bcrypt, mail
from forms import *
from models import *
from flask_login import login_user, current_user, logout_user, login_required
from routes.commonRoutes import save_picture



@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture('profile',current_user.image_file,form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data= current_user.contact
    image_file = url_for('static', filename='pictures/profile/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)
