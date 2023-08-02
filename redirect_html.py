from flask import Flask, redirect, jsonify, render_template , request
from flask_mail import Mail, Message
from flask_restful import Resource, Api
import pandas.io.sql as sql
from mysql.connector import connect
import redirect_function
import datetime
import os
from dotenv import load_dotenv

app = Flask(__name__ , template_folder = 'template')
api = Api(app)

load_dotenv()

app.config['MAIL_SERVER']  = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

LINK_RUT_GON = 2
LINK_DA_TON_TAI = 1
LINK_MOI = 0

db_connect = connect(
    host="localhost",
    user="root",
    password="@Americanstudy123",
    database="url_link"
)
conn = db_connect.cursor(dictionary=True)  # kết nối với cơ sở dữ liệu
class all_data(Resource) :
    def get(self):
        sql1 = "select * from url"
        conn.execute(sql1)
        result = {'data' : [dict(i) for i in conn]}
        return jsonify(result)

@app.route('/form' , methods = ['GET'])
def form():
    return render_template('input.html')

@app.route('/create_link' , methods = ['POST' , 'GET'])
def create_link() :
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST' :
        form_data = request.form
        redirect_function.insert_data(db_connect , form_data['expire_date'] , form_data['url'])
        mycursor = sql.read_sql("select * from url", db_connect)
        res = redirect_function.create_link(mycursor ,  form_data['url'])

        mycursor1 = db_connect.cursor()

        sql1 = "UPDATE url SET Shorten_URL = %s , Viewer_number = if(Viewer_number is null,0,Viewer_number) WHERE URL = %s"
        val = (res, form_data['url'])

        mycursor1.execute(sql1, val)

        db_connect.commit()

        res = "https/bit.ly/" + res
        return render_template('data.html',form_data = res)

@app.route('/data/renew_link' , methods = ['POST' , 'GET'])
def renew_link():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST' :
        form_data = request.form
        if form_data['renew'].lower() == 'yes':
            redirect_function.delete_existed_link(db_connect , form_data['url'])
            return render_template("enter_date.html" , url = form_data['url'])
        else:
            msg = Message('There is an activity in your program.' , sender = 'thaolinha1hb@gmail.com' , recipients = ['nthaolinh1103@gmail.com'])
            msg.body = 'There is person using your program to work with URL link.'
            mail.send(msg)
            return render_template("closing.html")

@app.route("/data/delete_existed_link" , methods = ['POST' , 'GET'])
def delete_existed_link() :
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST' :
        form_data = request.form
        if form_data['delete'].lower() == 'yes' :
            redirect_function.delete_existed_link(db_connect , form_data['url'])
            return render_template("renew_delete.html", url = form_data['url'])
        else :
            return render_template("renew.html" , url = form_data['url'])

        msg = Message('There is an activity in your program.', sender='thaolinha1hb@gmail.com',
                      recipients=['nthaolinh1103@gmail.com'])
        msg.body = 'There is person using your program to work with URL link.'
        mail.send(msg)

        return render_template("closing.html")

@app.route("/data/delete_shorten_link" , methods = ['POST' , 'GET'])
def delete_shorten_link() :
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST' :
        form_data = request.form
        if form_data['delete'].lower() == 'yes' :
            redirect_function.delete_shorten_link(db_connect , form_data['url'])

        msg = Message('There is an activity in your program.', sender='thaolinha1hb@gmail.com',
                      recipients=['nthaolinh1103@gmail.com'])
        msg.body = 'There is person using your program to work with URL link.'
        mail.send(msg)

        return render_template("closing.html")

@app.route('/data/not_url' , methods = ['GET'])
def not_url() :
    return render_template("not_url.html")

@app.route('/data/', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':

        form_data = request.form

        mycursor1 = sql.read_sql("select * from url", db_connect)

        tmp1 = redirect_function.check(mycursor1, form_data['URL'])

        if tmp1 == LINK_RUT_GON:

            mycursor2 = db_connect.cursor()

            sql1 = "SELECT URL, Created_date , Expire_date , Viewer_number from url where Shorten_URL =%s"
            val = (form_data['URL'][13:],)

            mycursor2.execute(sql1, val)

            d = mycursor2.fetchall()

            expired_date = datetime.datetime.strptime(d[0][2], "%m/%d/%Y")
            today = datetime.datetime.today()

            if today <= expired_date:
                d.append("The link is still available.")
            else:
                d.append("The link was expired.")

            return render_template("all_data.html" , form_data = d , url = form_data['URL'])

        tmp = (redirect_function.if_is_url(form_data['URL']))

        if tmp == False :
            return redirect("/data/not_url" , code = 302 )

        mycursor = sql.read_sql("select * from url", db_connect)

        tmp = redirect_function.check(mycursor , form_data['URL'])
        if tmp == LINK_DA_TON_TAI :
            return render_template("existed_link.html" , url = form_data['URL'] )
        elif tmp == LINK_MOI :

            return render_template("enter_date.html" , url = form_data['URL'])

class take_data(Resource):
    def get(self , shortenurl):
        sql1 = "select * from url where Shorten_URL = %s"
        val = (shortenurl,)
        conn.execute(sql1, val)
        result = [dict(i) for i in conn]
        return jsonify(result)

class get_link(Resource):
    def get(self, shortenurl):
        sql1 = "select Expire_date , URL from url where Shorten_URL = %s"
        val = (shortenurl,)
        conn.execute(sql1, val)
        for i in conn.fetchall():
            result = i
        expired_date = datetime.datetime.strptime(result['Expire_date'], "%m/%d/%Y")
        today = datetime.datetime.today()

        if today <= expired_date:
            sql2 = "UPDATE url SET Viewer_number =  Viewer_number + 1 WHERE Shorten_URL = %s"
            val2 = (shortenurl,)
            conn.execute(sql2, val2)
            db_connect.commit()

            return redirect(result['URL'], code=302)
        else:
            return "\tThe link was expired."

api.add_resource(all_data, '/')
api.add_resource(take_data, '/https/bit.ly/<shortenurl>/data')
api.add_resource(get_link, '/https/bit.ly/<shortenurl>')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)