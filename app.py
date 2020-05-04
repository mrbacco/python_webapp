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
from passlib.hash import sha512_crypt # password hashing
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
    mycol_u = mydb["users"]
    print("if connected to db, then these are the collections in mydb: ", mydb.list_collection_names()) # used to check if db is connected
except:
    logging.warning("not connected to mongodb")

############## db SETUP END ##############



############## defining the routes for the different web pages START ##############

# definition of a class for the form used in signup, login, and web scraping
class Init(Form): #this is for registering
    email = StringField('Email', [validators.DataRequired(),validators.Email()])
    name = StringField('Name', [validators.DataRequired(),validators.length(min=1, max=50)])
    username = StringField('Username', [validators.DataRequired(),validators.DataRequired(),validators.length(min=5, max=15)])
    password = PasswordField("Password", [validators.DataRequired(), validators.length(min=6, max=14)])

class Scrape(Form): #this is for scraping
    url = StringField('URL', [validators.DataRequired(),validators.URL()])

class Signin(Form): #this is for signing in
    username = StringField('Username', [validators.DataRequired(),validators.DataRequired(),validators.length(min=5, max=15)])
    password = PasswordField("Password", [validators.DataRequired()])

# route for the web scraping home page 
@app.route("/", methods = ['GET', 'POST']) # this is the route to the homepage for scraping
def index():
    form = Scrape(request.form)
    if request.method == 'GET': # make sure the method used is define above
        return render_template('home.html', form = form), logging.warning("you are under the home page now using GET, well done mrbacco ")
    if request.method == 'POST' and form.validate():
        # the following are the data from the init form
        url = form.url.data
        #email = form.email.data
        
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
                #"email" : email,
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

#check if user is logged in 
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash ("please login first to view this page", "danger")
            return redirect(url_for("signin"))
    return wrap

#route for the web scraping results page
@app.route("/dashboard", methods = ['GET'])
@is_logged_in
def dashboard():
    print("you are under the dashboard page now, well done mrbacco ")
    return render_template('dashboard.html')

#route for the signup page
@app.route("/signup", methods = ['GET', "POST"]) 
def signup():
    form = Init(request.form)
    if request.method == 'GET': # make sure the method used is define above
        return render_template('signup.html', form = form), logging.warning("you are under the signup page now using GET, well done mrbacco ")
   
    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email= form.email.data
        password = sha512_crypt.encrypt(str(form.password.data))
    
        myuser=[{
                "name": name,
                "username": username,
                "email": email,
                "password" : password, #this is the hashed password
                "date": readtime,
              }]


        #checking if the username is already in use
        u = mycol_u.find_one({'username' : username})
        if u is not None:
            flash("USERNAME ALREADY IN USE!!, please choose another username!", "danger")
            return render_template('signup.html', form = form), print("reload the signup page due username already present")
        else:
            u = mycol_u.insert_many(myuser), print("inserting this item: ", myuser) # insert user into the mongo db
        
            # send an email to mrbacco@mrbacco.com for testing purposes: PLEASE DISABLE THIS IN PRODUCTION!!!!!       
            msg = Message("NEW MESSAGE: ", sender='mistalj85@gmail.com', recipients=["mrbacco@mrbacco.com"], html = f"<h3> new signup from: </h3> <ul> <li>name: {name}</li> <li>username: {username}</li> <li> email: {email}</li> <li> date and time: {readtime}</li>")
            mail.send(msg)
        
            flash("thanks for registering, you can now login", "success")
            return redirect(url_for('signin')), print ("redirecting to signin page")

        flash("Credential not correct, try again", "danger")  
        return render_template('signup.html', form = form), print("reload the signup page due to failure")

#route for the signin  page
@app.route("/signin", methods = ['GET', "POST"]) 
def signin():
    form = Signin(request.form)
    if request.method == 'GET': # make sure the method used is define above
        return render_template('signin.html', form = form), print("you are under the signin page now, well done mrbacco")
    if request.method == 'POST' and form.validate():
        # the following are the data from the init form
        username = form.username.data
        password_form = form.password.data
        print("these are the email and password inserted", username, password_form)

        user_db = mycol_u.find_one({'username' : username})
        #for key, value in user_db.items():
            #print ("these are the fields in the db ", key, value)

        if user_db is None:
            flash("No USER FOUND!!, please try again or signup!", "danger")
            return render_template('signin.html', form = form), print("user not found, flashed a message on the web page")

        if sha512_crypt.verify(password_form, user_db['password']):
            
            #setting the session on for this user till he/she signs out!!
            session ["logged_in"] = True 
            session ["username"] = username

            flash("You are now logged in", "success")
            return render_template('home.html', form = form), print("Password match: redirecting to scraping page")
        else:
            flash("credential not correct, please try again", "danger")
        
    return render_template('signin.html', form = form)

#route for the signout page
@app.route("/signout", methods = ['GET', "POST"])
@is_logged_in
def signout():
    session.clear()
    flash("You are now logged out, thanks", "success")
    print("user signed out signout")
    return render_template('home.html')

#route for the users page - MAKE IT VISIBLE ONLY TO ADMIN
@app.route("/users", methods = ['GET'])
@is_logged_in
def users():
    print("you are under the users page now")
    return render_template('users.html')
  

############## defining the routes for the different web pages END ##############



############# signup to the webapp START ##############


############# signup to the webapp END ##############




############# signin to the webapp START ##############


############# signin to the webapp END ##############





####################################################################################################
# running the app and enabling debug mode so that I can update the app.py without the need of manual restart
if __name__ == "__main__":
    app.secret_key="mrbacco1974"
    app.run(debug=True)