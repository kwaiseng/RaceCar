from flask import Blueprint
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_bootstrap import Bootstrap
import boto3
import uuid 
import os
from .filters import datetimeformat, file_type
from .config import S3_BUCKET, S3_KEY, S3_SECRET, SECRET_KEY, SQL_Host, SQL_User, SQL_Password, URI
from .main import main as app
from .models import Entry
from .s3 import aws_s3_url
from . import db

order = Blueprint('order', __name__)


@order.route('/vieworder')
@login_required
def vieworder():
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



       list = Entry.query.filter_by(name=current_user.name).all()

       print_list = []

       total_price = 0

       for picture in list:
              
              print(f'Quantity = {picture.qty} ')

              if picture.qty > 0:
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
                     entry_list.sub_total = picture.price * entry_list.qty
                     total_price = total_price + entry_list.sub_total

                     print(f'{picture.car_type} {picture.first_100K} {picture.top_speed} {picture.price}  {picture.qty}')
    
                     print_list.append(entry_list)

       return render_template('vieworder.html', files=print_list, total=total_price)



@order.route('/trackorder')
@login_required
def trackorder():
    return render_template('trackorder.html')
