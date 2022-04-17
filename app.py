#app.py
from email import message
import psycopg2 #pip install psycopg2 
import psycopg2.extras
from flask import Flask, render_template, url_for, redirect, request,session,flash

app = Flask(__name__)

app.secret_key = "learn_basics_secret_key"

# database credential goes here
DB_HOST = "localhost"
DB_NAME = "test"
DB_USER = "postgres"
DB_PASS = "pass@123"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
# a list of user session data
userData=[]

@app.route('/',methods=['GET','POST'])
def main():
    try:
        # if previous login detected redirect to dashboard
        if (session['id']):
            global userData
            userData=[session['id'],session['username'],session['email']]
            return render_template('dashboard.html',user=userData)
    except:
        return render_template('memberLogin.html')

# to authenticate user
@app.route('/login',methods=['GET','POST'])
def login():
    try:
        if request.method==('post' or 'get'):
            # session.pop('id',none)
            return 'illegal request'
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        user= request.form['username']
        password = request.form['password']
        cur.execute("SELECT * FROM user_login where username = %s",[user])
        userExist = cur.fetchone()
        print(userExist)
        if userExist:
            if password == userExist['password']:    
                session['id']=userExist['emp_id']
                session['username']=userExist['username']
                session['email']=userExist['email_id']
                userData=[session['id'],session['username'],session['email']]
                return render_template('dashboard.html',user=userData)
            else:
                # if the username is correct but not the password
                flash('Forgot Password?')
                return render_template('memberLogin.html')
        else:
            # if none is correct
            flash('Invalid Credentials')
            return render_template('memberLogin.html')
    except: return render_template('redirect.html')

# just a testing route (optional)
@app.route('/home',methods=['GET','POST'])
def dashboard():
    try:
        if session['username']:
            return render_template('dashboard.html',user=userData)
    except: return render_template('redirect.html')

# this logs out the user and destroys the session if any
@app.route('/logout',methods=['GET','POST'])
def logout():
    session.pop('id',None)
    session.pop('username',None)
    session.pop('email',None)
    return render_template('memberLogin.html')

# to authenticate user using email and username for password reset process
@app.route('/forgotPassword',methods=['GET','POST'])
def forgotPassword():
    try:
        if request.method==('post' or 'get'):
            return 'illegal request'
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        user= request.form['username']
        email = request.form['email']
        cur.execute("SELECT * FROM user_login where username = %s",[user])
        userExist = cur.fetchone()
        print(userExist)
        if userExist:
            if email == userExist['email_id']:
                # if user exists create a session and allow them to reset password
                print(user,email)
                session['id']=userExist['emp_id']
                session['username']=userExist['username']
                session['email']=userExist['email_id']
                return render_template('createPass.html')
            else:
                logout()
                flash('Details do not match any record!')
                return render_template('memberLogin.html')
        else:
            flash('Details do not match any record!')
            return render_template('memberLogin.html')
    except: 
        # flash('Details do not match any record!')
        return render_template('forgotPass.html')

# to create new password for the user
# the reason why this is an entirely differnt route because in future we can 
# allow users to change password from their dashboard also, if they want. By 
# just adding a simple action to this route
@app.route('/createPassword',methods=['GET','POST'])
def createPassword():
    try:
        if request.method==('post' or 'get'):
            return 'illegal request'
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        password1= request.form['new-password']
        confirmPassword1 = request.form['re-new-password']
        # if passwords do not match flash an alert
        if password1!=confirmPassword1:
            print('pass do not match')
            flash('Passwords do not match!')
            return render_template('createPass.html')
        # if the length check is not passed flash an alert
        if len(password1)<6:
            flash('The minimum length of password should be of 6 characters')
            return render_template('createPass.html')
        # if all the requirements met allow the user to update their password
        if password1==confirmPassword1:
            print('pass matches')
            cur.execute('Update user_login set password = %s where username =%s and emp_id = %s',[confirmPassword1,session['username'],session['id']])
            conn.commit()
            flash('Password Changed Successfully!')
            logout()
            return render_template('memberLogin.html')
    except: 
        print('fatal')
        logout()
        return render_template('memberLogin.html')

if __name__ == "__main__":
    app.run(debug=True)