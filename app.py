import datetime
import os
from flask import Flask, render_template, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired, Email
from dotenv import load_dotenv

from internal_connector import RestConnector

#Load environment
load_dotenv()
secret_key = os.getenv('app.secret_key')

app = Flask(__name__)
app.secret_key = secret_key

class RegisterForm(FlaskForm):
    user_name = StringField("Name",validators=[DataRequired()])
    email_address = StringField("Email",validators=[DataRequired(), Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Create Account")

class SavingDepositForm(FlaskForm):
    amount = StringField("ចំនួនទឹកប្រាក់", validators=[DataRequired()])
    currencyType = SelectField('ប្រភេទសាច់ប្រាក់', choices=[('USD', 'USD'), ('USD', 'KHR')])
    date = DateField('កាលបរិច្ឆេទ', format='%Y-%m-%d', default=datetime.date.today, validators=[DataRequired()])
    desc = StringField("កំណត់ចំណាំ")
    submit = SubmitField("បញ្ចូល")

class LoginForm(FlaskForm):
    username = StringField("Username",validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Login")

@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']

        req = {
            "channel_id": "sambathreasmey"
        }
        res = RestConnector.internal_app_api('partner', 'retrive_user', req, "POST")
        if res.status_code == 200:
            data = res.json()
        if data:
            users = data['data']
            user_detail = None
            for user in users:
                if user['user_name'] == user_id:
                    user_detail = user
        
            req = {
                "channel_id": "sambathreasmey"
            }
            res = RestConnector.internal_app_api('saving', 'transaction_detail', req, "POST")
            if res.status_code == 200:
                data = res.json()
            if data:
                txn_details = data['data']
            return render_template('index.html', total_user=len(users), txn_details=txn_details)
    return redirect(url_for('login'))

@app.route('/saving_deport', methods=['GET','POST'])
def saving_deport():
    if 'user_id' in session:
        form = SavingDepositForm()
        if form.validate_on_submit():
            amount = form.amount.data
            currencyType = form.currencyType.data
            date = form.date.data
            desc = form.desc.data
            req = {
                "transaction_date": date.strftime('%Y-%m-%d'),
                "amount": amount,
                "transaction_desc": desc,
                "user_id": session['user_id'],
                "currency_type": currencyType,
                "transaction_type": "normal",
                "channel_id": "sambathreasmey"
            }
            resp = RestConnector.internal_app_api('saving', 'deposit', req, "POST")
            if resp.status_code == 200:
                data = resp.json()
            if data and data['status'] == 0:
                return redirect(url_for('saving_deport'))
            else:
                flash(data['message'])
                return redirect(url_for('saving_deport'))
        return render_template('saving_deport.html', form=form)
    return redirect(url_for('login'))

@app.route('/delete_transaction_by_id/<string:transaction_id>', methods=['DELETE'])
def delete_transaction_by_id(transaction_id):
    if 'user_id' in session:
        req = {
            "transaction_id": transaction_id,
            "channel_id": "sambathreasmey"
        }
        resp = RestConnector.internal_app_api('saving', 'delete_transaction_by_id', req, "DELETE")
        return resp.json()
    return redirect(url_for('login'))

@app.route('/report')
def report():
    if 'user_id' in session:
        req = {
                "channel_id": "sambathreasmey"
            }
        res = RestConnector.internal_app_api('saving', 'transaction_detail', req, "POST")
        if res.status_code == 200:
            data = res.json()
        if data:
            txn_details = data['data']  # Fetch all users from the database
            return render_template('report.html', txn_details=txn_details)
    return redirect(url_for('login'))

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_name = form.user_name.data
        email_address = form.email_address.data
        password = form.password.data
        req = {
        "channel_id": "sambathreasmey",
        "user_name": user_name,
        "password": password,
        "email_address": email_address,
        "attempt": 1,
        "role": "full access",
        "status": 1
        }
        res = RestConnector.internal_app_api('partner', 'add_user', req, "POST")
        if res.status_code == 200:
            data = res.json()
        if data and data['status'] == 0:
            return redirect(url_for('login'))
        else:
            flash(data['message'])
            return redirect(url_for('register'))

    return render_template('register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        req = {
            "channel_id": "sambathreasmey",
            "user_name": username,
            "password": password
        }
        res = RestConnector.internal_app_api('partner', 'user_login', req, "POST")
        if res:
            if res.status_code == 200:
                data = res.json()
                if data and data['status'] == 0:
                    session['user_id'] = username
                    return redirect(url_for('index'))
                else: 
                    flash("Login failed. Please check your username and password")
                    return redirect(url_for('login'))
        flash("ប្រព័ន្ធមានបញ្ហារអាក់រអួល សូមព្យាយាមពេលក្រោយ")
        return redirect(url_for('login'))

    return render_template('login.html',form=form)

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']

        req = {
            "channel_id": "sambathreasmey",
            "user_name": user_id
        }
        res = RestConnector.internal_app_api('partner', 'get_user_details', req, "POST")
        if res.status_code == 200:
            data = res.json()
        if data:
            return render_template('dashboard.html',user=data['data'][0])
            
    return redirect(url_for('login'))

@app.route('/user_list')
def user_list():
    req = {
            "channel_id": "sambathreasmey"
        }
    res = RestConnector.internal_app_api('partner', 'retrive_user', req, "POST")
    if res.status_code == 200:
        data = res.json()
    if data:
        users = data['data']  # Fetch all users from the database
        return render_template('user_list.html', users=users)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True, port=8080)