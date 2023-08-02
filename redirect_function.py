import string
import random
import datetime
import requests

def if_is_url(url_string) :
    try:
        response = requests.get(url_string)
        return True
    except :
        return False

def check(mycursor , input_link) :

    for idx, link in enumerate(mycursor['URL']):
        if input_link == link:
            return 1

    for idx, link in enumerate(mycursor['Shorten_URL']):
        if input_link == "https/bit.ly/{}".format(link):
            return 2

    return 0

def delete_existed_link(mydb , input_link) :
    mycursor1 = mydb.cursor()

    sql1 = "DELETE FROM url WHERE URL = %s"
    val = (input_link,)

    mycursor1.execute(sql1, val)

    mydb.commit()

def insert_data(mydb , expired_date , input_link) :
    try:
        expired_date = datetime.datetime.strptime(expired_date, "%d-%m-%Y")
    except:
        today = datetime.datetime.today()
        expired_date = today + datetime.timedelta(days=10)

    expired_date = datetime.datetime.strftime(expired_date, "%d-%m-%Y")

    created_date = datetime.datetime.now()

    mycursor1 = mydb.cursor()

    sql1 = "INSERT INTO url (URL , Created_date , Expire_date) VALUES (%s , %s , %s)"
    val = (input_link, created_date, expired_date)

    mycursor1.execute(sql1, val)
    mydb.commit()

def create_link(d, input_link):
    letters = string.ascii_letters + string.digits
    s = ""
    s += ''.join(random.choice(letters) for i in range(8))

    while s in d['Shorten_URL']:
        s = ""
        s += ''.join(random.choice(letters) for i in range(8))

    for idx, link in enumerate(d['URL']):
        if link == input_link and (d['Shorten_URL'][idx] == None or len(d['Shorten_URL'][idx]) == 0):
            return s
        elif link == input_link:
            return d['Shorten_URL'][idx]

def delete_shorten_link(mydb , input_link) :
    mycursor1 = mydb.cursor()

    sql1 = "DELETE FROM url WHERE Shorten_URL = %s"
    val = (input_link[13:],)

    mycursor1.execute(sql1, val)

    mydb.commit()