from mysql.connector import connect
import pandas.io.sql as sql
import string
import random
import datetime
import validators

def if_is_url(url_string) :

    return validators.url(url_string) == True

def enter_link() :
    while 1 :
        input_link = input("Enter link:")
        if if_is_url(input_link) :
            return input_link

def check(mydb , mycursor , input_link) :
    ok = 0
    shortenurl = ""
    request = ""
    for idx, link in enumerate(mycursor['URL']):
        if input_link == link:
            ok = 1
            shortenurl = mycursor['Shorten_URL'][idx]
            break

    for idx, link in enumerate(mycursor['Shorten_URL']):
        if input_link == "https/bit.ly/{}".format(link):
            ok = 2
            break

    if ok == 1 :
        print("\tThis link is already exist.")
        print("\tThe Shorten URL: https/bit.ly/{}".format(shortenurl))

        request = input("Do you want to delete the link (Yes/No)?")

        if request.lower() == "yes":
            mycursor1 = mydb.cursor()

            sql1 = "DELETE FROM url WHERE URL = %s"
            val = (input_link,)

            mycursor1.execute(sql1, val)

            mydb.commit()
            if (mycursor1.rowcount == 1):
                print("The URL has been deleted")

        request = input("Do you want to renew the link (Yes/No)?")
        if request.lower() == 'yes' :
            mycursor1 = mydb.cursor()

            sql1 = "DELETE FROM url WHERE URL = %s"
            val = (input_link,)

            mycursor1.execute(sql1, val)

            mydb.commit()

            ok = 0

    if ok == 0:
        expired_date = input("Enter expire date (mm/dd/yyyy) or left blank:")
        try :
            expired_date = datetime.datetime.strptime(expired_date , "%m/%d/%Y")
        except :
            today = datetime.datetime.today()
            expired_date = today + datetime.timedelta(days=10)
            
        expired_date = datetime.datetime.strftime(expired_date , "%m/%d/%Y")
            
        created_date = datetime.datetime.now()

        mycursor1 = mydb.cursor()

        sql1 = "INSERT INTO url (URL , Created_date , Expire_date) VALUES (%s , %s , %s)"
        val = (input_link, created_date , expired_date)

        mycursor1.execute(sql1, val)
        mydb.commit()
        return True
    elif ok == 1 :
        return True
    else :
        return False

def create_URL(d , input_link) :
    letters = string.ascii_letters + string.digits
    s = ""
    s += ''.join(random.choice(letters) for i in range(8))

    while s in d['Shorten_URL'] :
        s = ""
        s += ''.join(random.choice(letters) for i in range(8))

    for idx , link in enumerate (d['URL']) :
        if link == input_link and (d['Shorten_URL'][idx] == None or len(d['Shorten_URL'][idx]) == 0):
            return s
        elif link == input_link :
            return d['Shorten_URL'][idx]
    
def print_data(a_list) :
    print("\n\tThe number of access to the shorten URL link : {}".format(a_list[0][3]))

    expired_date = datetime.datetime.strptime(a_list[0][2] , "%m/%d/%Y")
    today = datetime.datetime.today()

    if today <= expired_date :
        print("\tThe link is still available.")
    else:
        print("\tThe link was expired.")
        
    print("\tExpired time : {}".format(a_list[0][2]))
    
    print("\tAn original URL : {}".format(a_list[0][0]))
    
    print("\tCreated date : {}".format(a_list[0][1]))

def main(input_link) :

    mydb = connect(
        host = "localhost" ,
        user = "root" ,
        password = "@Americanstudy123" ,
        database = "url_link"
    )

    while 1 :
        input_link = enter_link()

        mycursor = sql.read_sql("select * from url" , mydb)

        ok = check(mydb , mycursor , input_link)

        if ok :

            mycursor = sql.read_sql("select * from url" , mydb)

            s = create_URL(mycursor , input_link)

            mycursor1 = mydb.cursor()

            sql1 = "UPDATE url SET Shorten_URL = %s , Viewer_number = if(Viewer_number is null,0,Viewer_number) WHERE URL = %s"
            val = (s, input_link)

            mycursor1.execute(sql1, val)

            mydb.commit()

            print("Shorten URL: https/bit.ly/{}".format(s))

            return s
        else :

            mycursor1 = mydb.cursor()

            sql1 = "SELECT URL, Created_date , Expire_date , Viewer_number from url where SHorten_URL =%s"
            val = (input_link[13:],)

            mycursor1.execute(sql1, val)

            print_data(mycursor1.fetchall())

            request = input("Do you want to delete the link (Yes/No)?")

            if request.lower() == "yes" :
                mycursor1 = mydb.cursor()

                sql1 = "DELETE FROM url WHERE Shorten_URL = %s"
                val = (input_link[13:],)

                mycursor1.execute(sql1, val)

                mydb.commit()
                if (mycursor1.rowcount == 1) :
                    print("The shorten URL has been deleted")

        ask = input("Do you want to continue (Yes/No)?")
        if ask.lower() != 'yes' :
            break

    print("Thank you for using =>")

if __name__ == "__main__" :
    main()