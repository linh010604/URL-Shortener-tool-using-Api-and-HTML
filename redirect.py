from flask import Flask, redirect, jsonify, request
from flask_mail import Mail , Message
from flask_restful import Resource, Api
import pandas.io.sql as sql
from mysql.connector import connect
import redirect_function
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__ )
api = Api(app)

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

def create_link(URL) :
        mycursor = sql.read_sql("select * from url", db_connect)
        res = redirect_function.create_link(mycursor , URL)

        mycursor1 = db_connect.cursor()

        sql1 = "UPDATE url SET Shorten_URL = %s , Viewer_number = if(Viewer_number is null,0,Viewer_number) WHERE URL = %s"
        val = (res, URL)

        mycursor1.execute(sql1, val)

        db_connect.commit()

        res = "https/bit.ly/" + res
        return "The shorten link for {}: {}".format(URL , res)

def delete_existed_link(URL) :
    redirect_function.delete_existed_link(db_connect , URL)

def delete_shorten_link(URL) :
    redirect_function.delete_shorten_link(db_connect , URL)

class all_data(Resource) :
    def get(self):
        sql1 = "select * from url"
        conn.execute(sql1)
        result = {'data' : [dict(i) for i in conn]}
        return jsonify(result)

@app.route('/data/', methods = ['POST'])
def data():
    form_data = request.json

    database = sql.read_sql("select * from url", db_connect)

    LOAI_LINK = redirect_function.check(database, form_data['url'])

    if LOAI_LINK == LINK_RUT_GON:

        mycursor2 = db_connect.cursor(dictionary=True)

        sql1 = "select URL, Created_date , Expire_date , Viewer_number from url where Shorten_URL =%s"
        val = (form_data['url'][13:],)

        mycursor2.execute(sql1, val)

        d = mycursor2.fetchall()

        expired_date = datetime.datetime.strptime(d[0]['Expire_date'], "%d-%m-%Y")
        today = datetime.datetime.today()

        if today <= expired_date:
            d[0]['Overtime'] = "The link is still available."
        else:
            d[0]['Overtime'] = "The link was expired."

        if form_data.get('delete',"").lower() == 'yes' :
            delete_shorten_link(form_data['url'][13:])
            d.append("This link has been deleted")

        msg = Message('There is an activity in your program.', sender='thaolinha1hb@gmail.com', recipients=['nthaolinh1103@gmail.com'])
        msg.body = 'There is person using your program to work with URL link.'
        mail.send(msg)

        return d

    if redirect_function.if_is_url(form_data['url']) == False:
        msg = Message('There is an activity in your program.', sender='thaolinha1hb@gmail.com', recipients=['nthaolinh1103@gmail.com'])
        msg.body = 'There is person using your program to work with URL link.'
        mail.send(msg)
        return "This link is not in url form. PLease enter valid link."

    if LOAI_LINK == LINK_DA_TON_TAI :
        mycursor2 = db_connect.cursor(dictionary=True)

        sql1 = "SELECT URL, Shorten_URL , Created_date , Expire_date , Viewer_number from url where URL =%s"
        val = (form_data['url'],)

        mycursor2.execute(sql1, val)

        d = mycursor2.fetchall()

        expired_date = datetime.datetime.strptime(d[0]['Expire_date'], "%d-%m-%Y")
        today = datetime.datetime.today()

        if today <= expired_date:
            d[0]['Overtime'] = "The link is still available."
        else:
            d[0]['Overtime'] = "The link was expired."

        if form_data.get('delete',"").lower() == 'yes':
            delete_existed_link(form_data['url'])
            d.append("This link has been deleted")

        d[0]['Shorten_URL'] = 'https/bit.ly/' + d[0]['Shorten_URL']

        msg = Message('There is an activity in your program.', sender='thaolinha1hb@gmail.com', recipients=['nthaolinh1103@gmail.com'])
        msg.body = 'There is person using your program to work with URL link.'
        mail.send(msg)

        return d

    elif LOAI_LINK == LINK_MOI :
        redirect_function.insert_data(db_connect, form_data.get('expire_date'), form_data['url'])
        result = create_link(form_data['url'])

        msg = Message('There is an activity in your program.', sender='thaolinha1hb@gmail.com', recipients=['nthaolinh1103@gmail.com'])
        msg.body = '{}'.format(result)
        mail.send(msg)

        return result

class take_data(Resource):
    def get(self , shortenurl):
        sql1 = "select * from url where Shorten_URL = %s"
        val = (shortenurl,)
        conn.execute(sql1, val)
        result = [dict(i) for i in conn]
        result[0]['Shorten_URL'] = 'https/bit.ly/' + result[0]['Shorten_URL']
        return jsonify(result)

class get_link(Resource):
    def get(self, shortenurl):
        sql1 = "select Expire_date , URL from url where Shorten_URL = %s"
        val = (shortenurl,)
        conn.execute(sql1, val)
        for i in conn.fetchall():
            result = i
        expired_date = datetime.datetime.strptime(result['Expire_date'], "%d-%m-%Y")
        today = datetime.datetime.today()

        if today <= expired_date:
            sql2 = "UPDATE url SET Viewer_number =  Viewer_number + 1 WHERE Shorten_URL = %s"
            val2 = (shortenurl,)
            conn.execute(sql2, val2)
            db_connect.commit()

            return redirect(result['URL'], code=302)
        else:
            return "\tThe link was expired on {}.".format(expired_date)

api.add_resource(all_data, '/')
api.add_resource(take_data, '/https/bit.ly/<shortenurl>/data')
api.add_resource(get_link, '/https/bit.ly/<shortenurl>')
if __name__ == '__main__':
    app.run(host='localhost', port=5000)