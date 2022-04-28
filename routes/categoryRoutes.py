from flask import render_template, url_for, flash, redirect, request, abort, jsonify, make_response
from app import app, db, bcrypt, mail
from forms import *
from models import *
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/category", methods=['GET'])
@login_required
def category():
    searchValue = request.args.get('searchValue')

    if searchValue:
        products = Product.query.filter((Product.name.ilike('%'+searchValue+'%')) | (Product.comment.ilike('%'+searchValue+'%')) 
            | (Product.subcategory.has(SubCategory.name.ilike('%'+searchValue+'%'))))
    else: 
        products = Product.query
    category =[{'name':cate.name, 'products':products.filter(Product.subcategory.has(SubCategory.category.has(Category.name==cate.name))).all()} for cate in Category.query.all()]

    return render_template('product/category.html', category=category , products=products)


@app.route("/subcategory/<int:category_id>", methods=['GET'])
@login_required
def searchSubcategory(category_id):
    subcategory = SubCategory.query.filter_by(category_id = category_id).distinct(SubCategory.name).all()
    subCategoryArray = []
    for sub in subcategory:
        subObj = {}
        subObj['name']=sub.name
        subObj['id']=int(sub.id)
        subCategoryArray.append(subObj)

    return jsonify({'subcategoryData':subCategoryArray})



@app.route("/subcategory", methods=['GET'])
@login_required
def subcategory():
    searchValue = request.args.get('searchValue')

    if searchValue:
        products = Product.query.filter((Product.name.ilike('%'+searchValue+'%')) | (Product.comment.ilike('%'+searchValue+'%')))
    else: 
        products = Product.query
    subcategory =[{'name':cate.name, 'products':products.filter(Product.subcategory.has(SubCategory.name==cate.name)).all()} for cate in SubCategory.query.all()]

    return render_template('product/subCategory.html' ,subcategory=subcategory , products=products)
