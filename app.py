########################################################
# Project: basic web application for scraping          #
# Author: mrbacco                                      #
# email: mrbacco@mrbacco.com                           #
# Date: Q4/2019 - Q1/2020                              #
# main file: app.py                                    #
########################################################

from flask import Flask, render_template, url_for, session, request, redirect, logging, flash  # modules from flask for web server
from data import Items
import pymongo # driver for mongdb connectivity
import pandas as pd
import scrapy as scrapy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators # FOR THE WEBFORMS
#from flask_wtf import URLField
from passlib.hash import sha512_crypt # passowrd hashing
import logging
from functools import wraps
from emails import send_mail
from flask_mail import Mail, Message
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import pprint

app = Flask(__name__) # creating an instalnce of the Flask class for thsi app as web server

# creation of a date&time object to be used in the databse
time = datetime.now() 
readtime = time.strftime("%d-%b-%Y (%H:%M:%S.%f)")

############## email server SETUP START ##############
app.config.update(dict(
    MAIL_SERVER = 'smtp.googlemail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'mistalj85@gmail.com',
    MAIL_PASSWORD = 'mrbacco2013'
))

mail = Mail(app)

print(" connected to email ... probably")
############## email server SETUP END ##############

############## db SETUP START ##############
# using mongo db cloud version
# checking the connection to cloud ongodb and printing in the console the list of collections under the database

try:
    myclient = pymongo.MongoClient("mongodb://mrbacco:mongodb001@cluster0-shard-00-00-goutv.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
    mydb = myclient["webscraping"] 
    mycol = mydb["scraping"]
    print("if connected to db, then these are the collections in mydb: ", mydb.list_collection_names()) # used to check if db is connected
except:
    logging.warning("not connected to mongodb")

############## db SETUP END ##############



############## defining the routes for the different web pages START ##############

class Init(Form): # definition of a class for the init form
    url = StringField('URL', [validators.URL()])
    email = StringField('Email', [validators.Email()])

@app.route("/", methods = ['GET', 'POST']) # this is the route to the homepage for scraping
def index():
    form = Init(request.form)
    if request.method == 'GET': # make sure the method used is define above
        return render_template('home.html', form = form), logging.warning("you are under the home page now using GET, well done mrbacco ")
    if request.method == 'POST' and form.validate():
        # the following are the data from the init form
        url = form.url.data
        email = form.email.data
        
        result = requests.get(url) # getting the url from the webform
        print("the requested url is: ", url) # printing the url to make sure the variable contains it
        print("the response code is: ", result.status_code)            
        print(result.headers)
        
        # now I can apply the BS4 class to the content of the page
        payload = result.content # defining a new variable that takes the content of the web page
        soup = BeautifulSoup(payload, "lxml") # created "soup": the beautiful soup object to use for scraping
        
        links=[] # I'm creating an empty list that will be filled with the result of the findings

        # this is the actual block of code for the core web scraping
        '''
        for var in soup.find_all("div"): # looping to find all the "div" of the page
            a_tag = var.find_all("a")
            links.append(a_tag)
        '''
        for www in soup.find_all('a'): # looking for all the hyperlinks in the page and printing them
            print("the following are the hypelinks available: ", www.get('href'))

        for para in soup.find_all('p'): # looping to find all the "paragraphs" of the page and printing the results
            print("the paragraphs are: ", str(para.text))
            # print(links,"\n")
            # value = [a.text for a in soup.find_all("links")] #looping to find all the links in the page references
            # values.append(value)
        # tot = values.count("...")
        # pprint.pprint(values) #using .text allows to extract only the text on the webpage and not the tags
        
        print("the requested title name is  :", soup.title.name)
        print("the requested title is  :", soup.title)
        print("the requested title parent name is  :", soup.title.parent.name)

        # defining a new variable taking as input the values from the init form to populate the DB
        mymsg=[{
                "url": url,
                "response code": result.status_code,
                "email" : email,
                "date": readtime,
              }]

        x = mycol.insert_many(mymsg), print("inserting this item: ", mymsg) # insert the list into the mongo db

        """
        # send an email to mrbacco@mrbacco.com for testing purposes: PLEASE DISABLE THIS IN PRODUCTION!!!!!       
        msg = Message("NEW MESSAGE: ", sender='campigotto111@gmail.com', recipients=["mrbacco@mrbacco.com"], html = f"<h3> new message from: </h3> <ul><li>URL: {url}</li> <li> EMAIL: {email}</li> <li> DATA e ORA: {readtime}</li>")
        mail.send(msg)
        validating the url in the form http://...
        url1="http://"+url #making sure the parser will get the HTTP://WWW.EXAMPLE.COM syntax
        """

        
    return render_template('home.html', form = form), print("you are under the home page now, mrbacco ...")

@app.route("/dashboard", methods = ['GET']) # this is the route to the dasboard page for scraping results
def dashboard():
    print("you are under the dashboard page now, well done mrbacco ")
    return render_template('dashboard.html')





@app.route("/users", methods = ['GET'])
def users():
    print("you are under the users page now, well done mrbacco")
    return render_template('users.html')
  


    
############## defining the routes for the different web pages END ##############






####################################################################################################
# running the app and enabling debug mode so that I can update the app.py without the need of manual restart
if __name__ == "__main__":
    app.secret_key="mrbacco1974"
    app.run(debug=True)