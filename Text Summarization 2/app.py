from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import re
import pandas as pd, numpy as np
import pickle
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

import joblib
from textsummarizer import *
  
app = Flask(__name__)

app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secret key of your choice
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'users.db')
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User model
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


# Create the User table if it doesn't exist
with app.app_context():
    db.create_all()


@app.route('/')
def home():
	return render_template('home.html')
  
@app.route('/summarize',methods=['POST'])
def summarize():
    
    if request.method == 'POST':
        
        text = request.form['originalText']
        if not request.form['numOfLines']:
            numOfLines = 3
        else:
            numOfLines = int(request.form['numOfLines'])
            
        summary, original_length = generate_summary(text,numOfLines)
        
        return render_template('result.html',
                               text_summary=summary,
                               lines_original = original_length,
                               lines_summary = numOfLines,
                               user = current_user)


# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password match
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            flash('Login successful!', 'success')
            return render_template('predict.html', user = current_user)
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect('/login')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect('/')
  

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            #flash('Username already exists. Please choose a different username.', 'danger')
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect('/register')

        # Create a new user
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. You can now login.', 'success')
        return redirect('/login')

    return render_template('register.html')
    

# summary save in pdf --------------------------

from flask import Flask, render_template, request, make_response
from fpdf import FPDF



# Existing routes and functions...

# @app.route('/download_summary', methods=['POST'])
# def download_summary():
#     if request.method == 'POST':
#         summary_text = request.form['summary_text']
        
#         # Generate PDF file
#         pdf = FPDF()
#         pdf.add_page()
#         pdf.set_font("Arial", size=12)
#         pdf.cell(0, 10, txt=summary_text, ln=True)

#         # Prepare the response
#         response = make_response(pdf.output(dest='S').encode('latin-1'))
#         response.headers.set('Content-Disposition', 'attachment', filename='summary.pdf')
#         response.headers.set('Content-Type', 'application/pdf')

#         return response




@app.route('/download_summary', methods=['POST'])
def download_summary():
    if request.method == 'POST':
        summary_text = request.form['summary_text']

        # Generate PDF file
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Split the summary text into lines
        lines = summary_text.split('\n')

        # Write each line to the PDF with line breaks
        for line in lines:
            pdf.multi_cell(0, 10, txt=line, align='L')
        
        # Prepare the response
        response = make_response(pdf.output(dest='S').encode('latin-1'))
        response.headers.set('Content-Disposition', 'attachment', filename='summary.pdf')
        response.headers.set('Content-Type', 'application/pdf')

        return response



if __name__ == "__main__":
    app.run()