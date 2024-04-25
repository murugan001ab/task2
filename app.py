from flask import Flask, render_template, request, redirect, url_for, jsonify,flash,make_response

import sqlite3
import jwt
from datetime import datetime,timedelta
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'


# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and password == user[2]:
            token = jwt.encode({'username': username, 'exp':datetime.utcnow() + timedelta(minutes=5)}, app.config['SECRET_KEY'])
            return redirect(url_for('home', token=token))
        
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    return render_template('login.html')

# Decorator for verifying JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms="HS256")
    
        except:
            return jsonify({'error': 'Token is invalid'}), 401

        return f(*args, **kwargs)

    return decorated

# Protected route
@app.route('/home')
@token_required
def home():
    token = request.args.get('token')
    decoded_token = jwt.decode(token, app.config['SECRET_KEY'],algorithms='HS256')
    username = decoded_token['username']
    return render_template('base.html',username=username,token=token)

@app.route('/provid',methods=["POST"])
def pro(): 
    if request.method=="POST":

        id=request.form.get("id")
        name=request.form.get("name")
        email=request.form.get("email")
        gen=request.form.get("gender")
        quntity=request.form.get("quntity")
        group=request.form.get("group")
        date=datetime.today()
        date=date.strftime("%d,%m,%Y")
        print("helo")
        try:
            con=sqlite3.connect("users.db")
            cur=con.cursor()
            
            cur.execute("insert into milk values(?,?,?,?,?,?,?)",(int(id),name,email,gen,quntity,group,date))
            print(id)   
            con.commit()
            con.close()
        except Exception as e:
            print("connection error",e)


    return render_template('createpage.html')


         

@app.route('/data')
@token_required
def data():
    token = request.args.get('token')
    decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    username = decoded_token['username']
    print(username)
    con=sqlite3.connect("users.db")
    cur=con.cursor()
    cur.execute("select *from milk where name=?",(username,))
    data=cur.fetchall()
    return render_template("datalist.html" ,data=data)

@app.route('/data',methods=['POST'])
def da():
    if request.method=="POST":
        cheked=[]
        cheked=request.form.getlist("dataAr")
        con=sqlite3.connect("users.db")
        cur=con.cursor()
        for i in cheked:
           cur.execute("delete from milk where date=?",(i,))
        con.commit()
        con.close()
        flash("deleted")
    token = request.args.get('token')
    decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    username = decoded_token['username']
    print(username)
    con=sqlite3.connect("users.db")
    cur=con.cursor()
    cur.execute("select *from milk where name=?",(username,))
    data=cur.fetchall()
    return redirect("{{url_for('data')}}")



    


if __name__ == '__main__':

    app.run(debug=True)
