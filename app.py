import datetime
import os
from flask import Flask, jsonify, render_template, redirect, request, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, SelectField, StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired, Email
from dotenv import load_dotenv
from flask_cors import CORS

from internal_connector import RestConnector

#Load environment
load_dotenv()
secret_key = os.getenv('app.secret_key')
channel_id = "sambathreasmey"

app = Flask(__name__)
app.secret_key = secret_key
CORS(app)

class RegisterForm(FlaskForm):
    full_name = StringField("ឈ្មោះពេញ",validators=[DataRequired()])
    user_name = StringField("ឈ្មោះអ្នកប្រើប្រាស់",validators=[DataRequired()])
    email_address = StringField("អ៊ីមែល",validators=[DataRequired(), Email()])
    password = PasswordField("ពាក្យសម្ងាត់",validators=[DataRequired()])
    submit = SubmitField("បង្កើតគណនី")

class SavingDepositForm(FlaskForm):
    amount = StringField("ចំនួនទឹកប្រាក់", validators=[DataRequired()])
    currencyType = SelectField('ប្រភេទសាច់ប្រាក់', choices=[('USD', 'USD'), ('USD', 'KHR')])
    date = DateField('កាលបរិច្ឆេទ', format='%Y-%m-%d', default=datetime.date.today, validators=[DataRequired()])
    desc = StringField("កំណត់ចំណាំ")
    isMoreDeposit = BooleanField("បន្ថែមលើប្រតិបត្តិចាស់ក្នុងថ្ងៃ")
    submit = SubmitField("បញ្ចូល")

class LoanForm(FlaskForm):
    amount = StringField("ទំហំសាច់ប្រាក់", validators=[DataRequired()])
    currencyType = SelectField('ប្រភេទសាច់ប្រាក់', choices=[('USD', 'USD'), ('USD', 'KHR')])
    date = DateField('កាលបរិច្ឆេទ', format='%Y-%m-%d', default=datetime.date.today, validators=[DataRequired()])
    desc = StringField("មូលហេតុ")
    submit = SubmitField("បញ្ចូល")

class LoanRepayForm(FlaskForm):
    amount = StringField("ទំហំសាច់ប្រាក់សង", validators=[DataRequired()])
    currencyType = SelectField('ប្រភេទសាច់ប្រាក់', choices=[('USD', 'USD'), ('USD', 'KHR')])
    date = DateField('កាលបរិច្ឆេទ', format='%Y-%m-%d', default=datetime.date.today, validators=[DataRequired()])
    desc = StringField("កំណត់ចំណាំ")
    submit = SubmitField("បញ្ចូល")

class LoginForm(FlaskForm):
    username = StringField("ឈ្មោះអ្នកប្រើប្រាស់",validators=[DataRequired()])
    password = PasswordField("ពាក្យសម្ងាត់",validators=[DataRequired()])
    submit = SubmitField("ចូលគណនី")

@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']

        req = {
            "channel_id": channel_id
        }
        res = RestConnector.internal_app_api('partner', 'retrive_user', req, "POST")
        if res:
            if res.status_code == 200:
                data = res.json()
                if data:
                    users = data['data']
                    user_detail = None
                    for user in users:
                        if user['user_name'] == user_id:
                            user_detail = user
                
                    req = {
                        "channel_id": channel_id
                    }
                    #get transactions detail
                    res = RestConnector.internal_app_api('saving', 'transaction_detail', req, "POST")
                    if res.status_code == 200:
                        data = res.json()
                        if data:
                            txn_details = data['data']
                    #get dashboard
                    res_dashboard = RestConnector.internal_app_api('saving', 'dashboard', req, "POST")
                    if res_dashboard.status_code == 200:
                        data = res_dashboard.json()
                        if data:
                            dashboard = data['dashboard']
                    return render_template('index.html', total_user=len(users), txn_details=txn_details, dashboard=dashboard)
        flash("ប្រព័ន្ធមានបញ្ហារអាក់រអួល សូមព្យាយាមពេលក្រោយ")
        return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route('/saving_deport', methods=['GET','POST'])
def saving_deport():
    if 'user_id' in session:
        form = SavingDepositForm()
        if form.validate_on_submit():
            if session['user_detail']['email_address'] not in ['engsoknai471@gmail.com', 'reasmeysambath@gmail.com']:
                flash("អ្នកពុំមានសិទ្ធិក្នុងការបញ្ចូលទេ!", 'danger')
                return redirect(url_for('saving_deport'))
            amount = form.amount.data
            currencyType = form.currencyType.data
            date = form.date.data
            desc = form.desc.data
            isMoreDeposit = form.isMoreDeposit.data
            req = {
                "transaction_date": date.strftime('%Y-%m-%d'),
                "amount": amount,
                "transaction_desc": desc,
                "user_id": session['user_id'],
                "currency_type": currencyType,
                "transaction_type": "saving_deposit_more" if isMoreDeposit else "saving_deposit",
                "channel_id": channel_id
            }
            resp = RestConnector.internal_app_api('saving', 'deposit', req, "POST")
            if resp:
                if resp.status_code == 200:
                    data = resp.json()
                    if data and data['status'] == 0:
                        flash("ប្រតិបត្តិការទទួលបានជោគជ័យ", 'success')
                        return redirect(url_for('saving_deport'))
                    else:
                        flash(data['message'], 'danger')
                        return redirect(url_for('saving_deport'))
            flash("ប្រព័ន្ធមានបញ្ហារអាក់រអួល សូមព្យាយាមពេលក្រោយ", 'danger')
            return redirect(url_for('login'))
        return render_template('saving_deport.html', form=form)
    return redirect(url_for('login'))

@app.route('/loan', methods=['GET','POST'])
def loan():
    if 'user_id' in session:
        form = LoanForm()
        if form.validate_on_submit():
            if session['user_detail']['email_address'] not in ['engsoknai471@gmail.com', 'reasmeysambath@gmail.com']:
                flash("អ្នកពុំមានសិទ្ធិក្នុងការបញ្ចូលទេ!", 'danger')
                return redirect(url_for('saving_deport'))
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
                "transaction_type": "loan",
                "channel_id": channel_id
            }
            resp = RestConnector.internal_app_api('saving', 'deposit', req, "POST")
            if resp:
                if resp.status_code == 200:
                    data = resp.json()
                    if data and data['status'] == 0:
                        flash("ប្រតិបត្តិការទទួលបានជោគជ័យ", 'success')
                        return redirect(url_for('loan'))
                    else:
                        flash(data['message'], 'danger')
                        return redirect(url_for('loan'))
            flash("ប្រព័ន្ធមានបញ្ហារអាក់រអួល សូមព្យាយាមពេលក្រោយ", 'danger')
            return redirect(url_for('login'))
        return render_template('loan.html', form=form)
    return redirect(url_for('login'))

@app.route('/loan_repay', methods=['GET','POST'])
def loan_repay():
    if 'user_id' in session:
        form = LoanRepayForm()
        if form.validate_on_submit():
            if session['user_detail']['email_address'] not in ['engsoknai471@gmail.com', 'reasmeysambath@gmail.com']:
                flash("អ្នកពុំមានសិទ្ធិក្នុងការបញ្ចូលទេ!", 'danger')
                return redirect(url_for('saving_deport'))
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
                "transaction_type": "loan_repay",
                "channel_id": channel_id
            }
            resp = RestConnector.internal_app_api('saving', 'deposit', req, "POST")
            if resp:
                if resp.status_code == 200:
                    data = resp.json()
                    if data and data['status'] == 0:
                        flash("ប្រតិបត្តិការទទួលបានជោគជ័យ", 'success')
                        return redirect(url_for('loan_repay'))
                    else:
                        flash(data['message'], 'danger')
                        return redirect(url_for('loan_repay'))
            flash("ប្រព័ន្ធមានបញ្ហារអាក់រអួល សូមព្យាយាមពេលក្រោយ", 'danger')
            return redirect(url_for('login'))
        return render_template('loan_repay.html', form=form)
    return redirect(url_for('login'))

@app.route('/delete_transaction_by_id/<string:transaction_id>', methods=['DELETE'])
def delete_transaction_by_id(transaction_id):
    if 'user_id' in session:
        if session['user_detail']['email_address'] not in ['engsoknai471@gmail.com', 'reasmeysambath@gmail.com']:
            flash("អ្នកពុំមានសិទ្ធិក្នុងការបញ្ចូលទេ!", 'danger')
            return redirect(url_for('saving_deport'))
        req = {
            "transaction_id": transaction_id,
            "channel_id": channel_id
        }
        resp = RestConnector.internal_app_api('saving', 'delete_transaction_by_id', req, "DELETE")
        if resp:
            if resp.status_code == 200:
                return resp.json()
        flash("ប្រព័ន្ធមានបញ្ហារអាក់រអួល សូមព្យាយាមពេលក្រោយ", 'danger')
        return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route('/update_transaction_by_id/<string:transaction_id>', methods=['PUT'])
def update_transaction_by_id(transaction_id):
    if 'user_id' in session:
        if session['user_detail']['email_address'] not in ['engsoknai471@gmail.com', 'reasmeysambath@gmail.com']:
            flash("អ្នកពុំមានសិទ្ធិក្នុងការបញ្ចូលទេ!", 'danger')
            return redirect(url_for('saving_deport'))
        req = {
            "transaction_id": transaction_id,
            "transaction_date": request.json.get("transaction_date"),
            "amount": request.json.get("amount"),
            "transaction_desc": request.json.get("transaction_desc"),
            "currency_type": request.json.get("currency_type"),
            "transaction_type": request.json.get("transaction_type"),
            "channel_id": channel_id
        }
        resp = RestConnector.internal_app_api('saving', 'update_transaction_by_id', req, "PUT")
        if resp:
            if resp.status_code == 200:
                return resp.json()
        flash("ប្រព័ន្ធមានបញ្ហារអាក់រអួល សូមព្យាយាមពេលក្រោយ", 'danger')
        return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route('/repayment_loan_by_transaction_id/<string:transaction_id>', methods=['POST'])
def repayment_loan_by_transaction_id(transaction_id):
    if 'user_id' in session:
        if session['user_detail']['email_address'] not in ['engsoknai471@gmail.com', 'reasmeysambath@gmail.com']:
            flash("អ្នកពុំមានសិទ្ធិក្នុងការបញ្ចូលទេ!", 'danger')
            return redirect(url_for('saving_deport'))
        
        current_date = datetime.date.today()
        req = {
            "transaction_id": transaction_id,
            "repay_date": current_date.strftime('%Y-%m-%d'),
            "repay_amount": request.json.get("repay_amount"),
            "repay_desc": request.json.get("repay_desc"),
            "channel_id": channel_id
        }
        print(req)
        resp = RestConnector.internal_app_api('saving', 'repay_loan', req, "POST")
        if resp:
            if resp.status_code == 200:
                return resp.json()
        flash("ប្រព័ន្ធមានបញ្ហារអាក់រអួល សូមព្យាយាមពេលក្រោយ", 'danger')
        return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route('/report')
def report():
    if 'user_id' in session:
        #check report type
        report_type = request.args.get('transaction_type', '')  # Default to '' if not provided
        is_general = True
        if report_type:
            is_general = False

        req = {
                "channel_id": channel_id,
                "report_type": report_type
            }
        res = RestConnector.internal_app_api('saving', 'transaction_detail', req, "POST")
        if res:
            if res.status_code == 200:
                data = res.json()
                if data:
                    txn_details = data['data']  # Fetch all users from the database
                    return render_template('report.html', txn_details=txn_details, is_general=is_general)
        flash("ប្រព័ន្ធមានបញ្ហារអាក់រអួល សូមព្យាយាមពេលក្រោយ", 'danger')
        return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        full_name = form.full_name.data
        user_name = form.user_name.data
        email_address = form.email_address.data
        password = form.password.data
        req = {
        "channel_id": channel_id,
        "full_name": full_name,
        "user_name": user_name,
        "password": password,
        "email_address": email_address,
        "attempt": 1,
        "role": "full access",
        "status": 1
        }
        res = RestConnector.internal_app_api('partner', 'add_user', req, "POST")
        if res:
            if res.status_code == 200:
                data = res.json()
                if data and data['status'] == 0:
                    return redirect(url_for('login'))
                else:
                    flash(data['message'], 'danger')
                    return redirect(url_for('register'))
        flash("ប្រព័ន្ធមានបញ្ហារអាក់រអួល សូមព្យាយាមពេលក្រោយ", 'danger')
        return redirect(url_for('login'))

    return render_template('register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        req = {
            "channel_id": channel_id,
            "user_name": username,
            "password": password
        }
        res = RestConnector.internal_app_api('partner', 'user_login', req, "POST")
        if res:
            if res.status_code == 200:
                data = res.json()
                if data and data['status'] == 0:
                    session['user_id'] = username
                    session['user_detail'] = data['data']
                    return redirect(url_for('index'))
                else: 
                    flash("ការចូលបានបរាជ័យ។ សូមពិនិត្យមើលឈ្មោះអ្នកប្រើប្រាស់ និងពាក្យសម្ងាត់របស់អ្នក។", 'danger')
                    return redirect(url_for('login'))
        flash("ប្រព័ន្ធមានបញ្ហារអាក់រអួល សូមព្យាយាមពេលក្រោយ", 'danger')
        return redirect(url_for('login'))

    return render_template('login.html',form=form)

@app.route('/onload')
def onload():
    req = {
        "channel_id": channel_id
    }
    notification = None
    resNotification = RestConnector.internal_app_api('saving', 'notification', req, "POST")
    if resNotification:
        if resNotification.status_code == 200:
            data = resNotification.json()
            if data:
                notification = data
    res = {
        "user_detail": session['user_detail'],
        "user_name": session['user_id'],
        "notification": notification
    }
    return res

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# external api
@app.route('/api/user_login', methods=['POST'])
def user_login():
    req = {
        "channel_id": channel_id,
        "user_name": request.get_json().get('user_name'),
        "password": request.get_json().get('password')
    }
    res = RestConnector.internal_app_api('partner', 'user_login', req, "POST")
    if res:
        if res.status_code == 200:
            data = res.json()
            if data and data['status'] == 0:
                return jsonify(data)
            else:
                return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=8080)