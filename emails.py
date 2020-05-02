########################################################
# Project: basic web application for scraping          #
# Author: mrbacco                                      #
# email: mrbacco@mrbacco.com                           #
# Date: Q4/2019 - Q1/2020                              #
# SendEmail file in python using flask email           #
########################################################

from flask_mail import Mail, Message

import smtplib
from email.mime.text import MIMEText


def send_mail(name, telefono, email, messaggio):
    port = 2525
    smtp_server = 'smtp.mailtrap.io'
    login = ''
    password = ''
    message = f"<h3>Nuovo contatto</h3><ul><li>Nome: {name}</li><li>email: {email}</li><li>telefono: {telefono}</li><li>messaggio: {messaggio}</li></ul>"

    sender_email = {email}
    receiver_email = 'abaccolini@gmail.com'
    msg = MIMEText(message, 'html')
    msg['Subject'] = 'Contatto'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Send email
    with smtplib.SMTP(smtp_server, port) as server:
        server.login(login, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())