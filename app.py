########################################################
# Project: basic web application for scraping          #
# Author: mrbacco                                      #
# email: mrbacco@mrbacco.com                           #
# Date: Q4/2019 - Q1/2020                              #
########################################################

from flask import Flask, render_template, url_for, session, request, redirect, logging, flash  # modules from flask for web server
from data import Items
import pymongo # driver for mongdb connectivity
import pandas as pd
import scrapy as scrapy
from bs4 import BeautifulSoup # used for web scraping
import requests # the request HTTP library allows managing HTTP request/responses to/from websites
from wtforms import Form, StringField, TextAreaField, PasswordField, validators #FOR THE WEBFORMS
from passlib.hash import sha512_crypt #passowrd hashing
import logging
from functools import wraps
from emails import send_mail
from flask_mail import Mail, Message
from datetime import datetime


app = Flask(__name__) # creating an instalnce of the Flask class for thsi app as web server

time = datetime.now()
readtime = time.strftime("%d-%b-%Y (%H:%M:%S.%f)")

############## email server SETUP START ##############
app.config.update(dict(
    MAIL_SERVER = 'smtp.googlemail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'campigotto111@gmail.com',
    MAIL_PASSWORD = 'Daoxiao99'
))

mail = Mail(app)

print(" connected to email ... probably")
############## email server SETUP END ##############


############## db SETUP START ##############
# using mongo db cloud version
# checking the connection to cloud ongodb and printing in the console the list of collections under the database

try:
    myclient = pymongo.MongoClient("mongodb://mrbacco:mongodb001@cluster0-shard-00-00-goutv.mongodb.net:27017,cluster0-shard-00-01-goutv.mongodb.net:27017,cluster0-shard-00-02-goutv.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
    mydb = myclient["lawyers"]
    mycol = mydb["feedback"]
    print("if connected to db, then these are the collections in mydb: ", mydb.list_collection_names()) #used to check if db is connected
except:
    logging.warning("Could not connect to MongoDB")

############## db SETUP END ##############

############## defining the routes for the different web pages START ##############
class Init(Form): #definition of a class for the init form
    name = StringField('Name', [validators.Length(min = 1, max = 100)])
    telefono = StringField('Telefono', [validators.Length(min = 5, max = 50)])
    email = StringField('Email', [validators.Length(min = 6, max = 50)])
    messaggio = StringField('Messaggio', [validators.DataRequired()])

@app.route("/", methods = ['GET', 'POST'])
def index():
    form = Init(request.form)
    if request.method == 'GET': # make sure the method used is define above
        return render_template('home.html', form = form), logging.warning("you are under the home page now using GET, well done bacco ")
    if request.method == 'POST' and form.validate():
        # the following are the data from the init form
        name = form.name.data 
        telefono = form.telefono.data
        email = form.email.data
        messaggio = form.messaggio.data

        # defining a new variable taking as input the values from the init form
        mymsg=[{
                "name": name, 
                "telefono": telefono, 
                "email" : email, 
                "messaggio" : messaggio
                }]
        # insert the list into the mongo db
        x = mycol.insert_many(mymsg), print("inserting this user: ", mymsg, "in the database called ", mycol)
        msg = Message('New message from: ', sender='campigotto111@gmail.com', recipients=['mrbacco@mrbacco.com'], html = f"<h3> new message from: </h3> <ul><li>NOME: {name}</li> <li>TELEFONO: {telefono}</li><li> EMAIL: {email}</li> <li> MESSAGGIO: {messaggio}</li> <li> DATA e ORA: {readtime}</li>" )
        mail.send(msg)
        
    return render_template('home.html', form = form), print("you are under the home page now using POST, data are sent to database")

############## defining the routes for the different web pages END ##############








####################################################################################################
# running app in debug mode so that I can update the app.py without the need of manual restart
if __name__ == "__main__":
    app.secret_key="mrbacco1974"
    app.run(debug=True)