from flask import Blueprint
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_bootstrap import Bootstrap
from sqlalchemy import select
import sqlalchemy
import boto3
import uuid 
import os
from .filters import datetimeformat, file_type
from .config import S3_BUCKET, S3_KEY, S3_SECRET, SECRET_KEY, SQL_Host, SQL_User, SQL_Password, URI
from .main import main as app
from .models import Entry
from . import db

class aws_s3_url():
  def __init__(self):
    self.url = None
    self.last_modified = None
    self.qty = None
    self.id = None
    self.car_type = None
    self.top_speed = None
    self.first_100K = None
    self.price = None 
    self.unit_price = None
    self.sub_total = None

s3 = Blueprint('s3', __name__)

@s3.route('/files')
@login_required
def files():
    s3_resource = boto3.resource(
         's3',
         aws_access_key_id=S3_KEY,
         aws_secret_access_key= S3_SECRET
      )
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=S3_KEY,
        aws_secret_access_key= S3_SECRET
    )

    my_bucket = s3_resource.Bucket(S3_BUCKET)

    summaries = my_bucket.objects.all()

    print(f'retriving records for user {current_user.name} ')

    list = Entry.query.filter_by(name=current_user.name).all()

    print_list = []

    for picture in list:
        entry_list=aws_s3_url()
        entry_list.url = s3_client.generate_presigned_url('get_object',
                            Params={'Bucket': S3_BUCKET,
                                    'Key': picture.url},
                                    ExpiresIn=900)
        entry_list.qty = picture.qty
        entry_list.id = picture.id
        entry_list.car_type = picture.car_type
        entry_list.first_100K = picture.first_100K
        entry_list.top_speed = picture.top_speed
        entry_list.price = picture.price
        print_list.append(entry_list)

    return render_template('files.html', my_bucket=my_bucket, files=print_list)

@s3.route('/add',methods=['POST'])
@login_required
def add_to_cart():
    
    item = request.form.get('item')
    qty = request.form.get('quantity')
    id = request.form.get('id')
    
    print(f'adding {qty} copies of {item}, id = {id} to cart')

    picture = Entry.query.get_or_404(id)

    picture.qty = qty

    db.session.add(picture)
    db.session.commit()
    
    print(picture.qty)

    return redirect(url_for('s3.files'))

@s3.route('/update_inventory')
@login_required
def update_inventory():
    return render_template('update_inventory.html')

@s3.route('/update_inventory', methods=['POST'])
def add_inventory():
    file = request.files['file']
    car_type = request.form.get('car_type')
    first_100K = request.form.get('first_100K')
    top_speed = request.form.get('top_speed')
    price = request.form.get('price')
    qty = request.form.get('qty')
    print(f'Car type = {car_type}')
    print(f'0 - 100 Km/h = {first_100K}')
    print(f'Top Speed = {top_speed}')
    print(f'Price = {price}')
    print(f'Qty = {qty}')
    
    dst_filename = str(uuid.uuid1()) + os.path.splitext(file.filename)[1]

    s3_resource = boto3.resource('s3',
      aws_access_key_id=S3_KEY,
      aws_secret_access_key=S3_SECRET
    )

    my_bucket = s3_resource.Bucket(S3_BUCKET)
    tag = 'user=' + current_user.name

    my_bucket.Object(dst_filename).put(Body=file,Tagging='uuid=' + dst_filename)

    flash('File uploaded successfully')
    
    new_entry = Entry(
                  name = current_user.name,
                  url = dst_filename,
                  origfilename = file.filename,
                  qty = qty,
                  car_type = car_type,
                  first_100K = first_100K,
                  top_speed = top_speed,
                  price = price
                  )
    db.session.add(new_entry)
    db.session.commit()


    return redirect(url_for('s3.files'))