from django.shortcuts import render,redirect
from django.db import connection
import re
from django.http import HttpResponse
# Create your views here.

logged_in = False
ID = -1

def is_valid(l):
    for i in l:
        if i == '':
            return False
    return True

def is_valid_card(credit_id,password,method):
    cursor = connection.cursor()
    sql = "SELECT * FROM CARD"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()

    for r in result:
        if credit_id == r[2] and password == r[3] and method.lower() == r[1].lower():
            return True
    return False

def push_into_db(l,u_id):

    #generate subscription id
    cursor = connection.cursor()
    sql_ID = "SELECT NVL(MAX(SUBSCRIPTION_ID),0) FROM SUBSCRIPTION"
    cursor.execute(sql_ID)
    result = cursor.fetchall()
    for i in result:
        sub_ID = i[0]
    cursor.close()
    sub_ID = sub_ID+1

    #generate bill id
    cursor = connection.cursor()
    sql_ID = "SELECT NVL(MAX(BILL_ID),0) FROM BILLING_HISTORY"
    cursor.execute(sql_ID)
    result = cursor.fetchall()
    for i in result:
        bill_ID = i[0]
    cursor.close()
    bill_ID = bill_ID+1

    #current date
    cursor = connection.cursor()
    curr_date_sql = "SELECT TO_CHAR(SYSDATE, 'YYYY-MM-DD') FROM dual"
    curr_date_list = cursor.execute(curr_date_sql)
    for i in curr_date_list:
        curr_date = str(i[0])
    cursor.close()

    #for yearly
    cursor = connection.cursor()
    curr_date_sql = "SELECT ADD_MONTHS(TO_CHAR(SYSDATE, 'YYYY-MM-DD'),12) FROM dual"
    curr_date_list = cursor.execute(curr_date_sql)
    for i in curr_date_list:
        yearly = str(i[0])
    cursor.close()

    #for monthly
    cursor = connection.cursor()
    curr_date_sql = "SELECT ADD_MONTHS(TO_CHAR(SYSDATE, 'YYYY-MM-DD'),1) FROM dual"
    curr_date_list = cursor.execute(curr_date_sql)
    for i in curr_date_list:
        monthly = str(i[0])
    cursor.close()

    #update user table
    cursor = connection.cursor()
    sql = "UPDATE USERS SET SUBSCRIPTION_PLAN = %s, FAVOURITE_GENRE = %s WHERE USER_ID = %s"
    cursor.execute(sql, [l[2], l[4], u_id])
    connection.commit()
    print("Printing l(2): "+l[2])
    sub_period = ""
    Amount = ""

    sub_status = "Active"
    bill_des = "Paid"

    if l[2] == "yearly":
        sub_period = yearly
        Amount = "70$"
    elif l[2] == "single":
        Amount = "0.99$"
    else:
        sub_period = monthly
        Amount = "6.25$"

    #insert into billing history
    cursor = connection.cursor()
    sql_card = "SELECT * FROM CARD"
    cursor.execute(sql_card)
    result = cursor.fetchall()
    for r in result:
        if l[0] == r[2] and l[1] == r[3]:
            card_id = r[0]
    cursor.close()
    print(bill_ID)
    print(curr_date)
    print(bill_des)
    print(sub_period)
    print(Amount)
    print(card_id)

    cursor = connection.cursor()
    sql = "INSERT INTO BILLING_HISTORY (BILL_ID, BILL_DATE, BILL_DESCRIPTION, SERVICE_PERIOD, AMOUNT_PAID, CARD_ID) VALUES(%s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, [bill_ID,curr_date,bill_des,sub_period,Amount,card_id])
    connection.commit()
    cursor.close()
    #insert into Subscription table
    cursor = connection.cursor()
    sql = "INSERT INTO SUBSCRIPTION (SUBSCRIPTION_ID,SUBSCRIPTION_PERIOD, SUBSCRIPTION_STATUS, USER_IDSUB, BILL_IDSUB) VALUES(%s, %s, %s, %s, %s)"
    cursor.execute(sql, [sub_ID,sub_period,sub_status,u_id,bill_ID])
    connection.commit()
    cursor.close()

def home_notLoggedIn(request):
    if request.session.get('is_logged_in',False) == True:
        #return HttpResponse('This is User_ID' + request.session.get('user_ID',-1))
        id = request.session.get('user_ID', -1)
        cursor = connection.cursor()
        sql = "SELECT * FROM USERS WHERE USER_ID = %s"
        cursor.execute(sql, id)
        result = cursor.fetchall()
        cursor.close()
        for r in result:
            first_name = r[2]
        cursor = connection.cursor()
        sql = "SELECT * FROM SHOW s, DIRECTOR d WHERE s.DIRECTOR_ID = d.PERSON_ID"
        cursor.execute(sql)
        result_show = cursor.fetchall()
        cursor.close()
        show_list = []
        for r in result_show:
            temp_director = str(r[15])+" "+str(r[16])
            show_title = r[2]
            show_genre = r[1]
            show_imdb = r[5]
            show_image = r[13]
            director_name = temp_director
            director_link = r[18]
            single_row = {"director_name":director_name,"director_link":director_link,"show_title": show_title, "show_genre": show_genre, "show_imdb": show_imdb,
                          "show_image": show_image}
            show_list.append(single_row)


        return render(request, "home/homepage.html", {'shows': show_list})

    else:
        return redirect("http://127.0.0.1:8000/user/login")

#not used anymore, might use in future
def home_LoggedIn(request,user_ID):
    #Home page specific to user
    print(user_ID)

    if 'is_logged_in' in request.session:
        if user_ID == request.session.get('user_ID',-1) and request.session.get('is_logged_in', False) == True:
            #return HttpResponse('This is User_ID' + str(user_ID))
            return render(request,"home/homepage.html")
        else:
            print("not logged in")
            return redirect("http://127.0.0.1:8000/user/login/")

    else:
        print("not logged in")
        return redirect("http://127.0.0.1:8000/user/login/")


def search(request):

    search_item = request.GET.get('search')
    print(search_item)
    cursor = connection.cursor()
    sql = "SELECT * FROM SHOW s, DIRECTOR d, SERIES ss WHERE s.DIRECTOR_ID = d.PERSON_ID AND s.SERIES_ID = ss.SERIES_ID"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()

    error_msg = "No Result Found!"
    show_list=[]

    for r in result:
        temp_director = str(r[15])+" "+str(r[16])
        temp_show = r[2]
        temp_genre = r[1]
        temp_series_title = r[26]
        temp_lang = r[8]
        if search_item.lower() == temp_lang.lower() or search_item.lower() == temp_director.lower() or search_item.lower() == temp_show.lower() or search_item.lower() == temp_genre.lower() or search_item.lower() == temp_series_title.lower():
            show_title = r[2]
            show_genre = r[1]
            show_des = r[3]
            show_age = r[4]
            show_lang = r[8]
            show_image = r[13]
            show_imdb = r[5]
            #show nothing... just for testing
            director_name = temp_director
            director_link = r[18]
            single_row = {"director_name":director_name,"director_link":director_link,"show_imdb":show_imdb,"show_title":show_title,"show_genre":show_genre,"show_des":show_des,"show_age":show_age,"show_lang":show_lang,"show_image":show_image}
            show_list.append(single_row)
            error_msg = ""
    show_all = {
        "show_name":search_item,
        "shows":show_list,
        "error_msg":error_msg
    }
    return render(request,'home\homepage.html',{'shows' : show_list , 'error_msg' : error_msg})

def log_out(request):
    if request.session.get('is_logged_in',False) == True:
        try:
            del request.session['user_ID']
            del request.session['is_logged_in']
        except KeyError:
            pass
        print("logged out successfully")

    return redirect("http://127.0.0.1:8000/user/login")

def search_by_year(request):
    if request.method == "POST":
        From_year = int(request.POST.get("start"))
        To_year = int(request.POST.get("end"))
    cursor = connection.cursor()
    sql = "SELECT * FROM SHOW s, DIRECTOR d, SERIES ss WHERE s.DIRECTOR_ID = d.PERSON_ID and s.SERIES_ID = ss.SERIES_ID"
    cursor.execute(sql)
    result_show = cursor.fetchall()
    cursor.close()

    error_msg = "No Result Found!"
    show_list=[]

    for r in result_show:
        year = r[23]
        if year >= From_year and year <= To_year:
            show_title = r[2]
            show_genre = r[1]
            show_des = r[3]
            show_age = r[4]
            show_lang = r[8]
            show_image = r[13]
            show_imdb = r[5]
            director_name = str(r[15])+" "+str(r[16])
            director_link = r[18]
            single_row = {"director_name":director_name,"director_link":director_link,"show_imdb":show_imdb,"show_title":show_title,"show_genre":show_genre,"show_des":show_des,"show_age":show_age,"show_lang":show_lang,"show_image":show_image}
            show_list.append(single_row)
            error_msg = ""
    return render(request,'home\homepage.html',{'shows' : show_list , 'error_msg' : error_msg})

def Action(request):
    return render(request,'home\homepage.html')
def Thriller(request):
    return render(request,'home\homepage.html')
def political(request):
    return render(request,'home\homepage.html')
def crime(request):
    return render(request,'home\homepage.html')
def historical(request):
    return render(request,'home\homepage.html')


def subscribe(response):
    error_msg = ""
    u_id = -1
    if response.session.get('is_logged_in',False) == True:
        u_id = response.session.get('user_ID', -1)
    print(u_id)
    form_values = {'credit_id': "",
                   'password': "",
                   'period': "",
                   'method': "",
                   'favgen': "",
    }

    if response.method == "POST":

        if response.POST.get("Subscribe"):
            credit_id = response.POST.get("credit_id")
            password = response.POST.get("password")
            period = ""
            if response.POST.get("period"):
                period = response.POST.get("period")
            method = ""
            if response.POST.get("method"):
                method = response.POST.get("method")
            favgen = response.POST.get("favgen")

            l = []
            l.append(credit_id)
            l.append(password)
            l.append(period)
            l.append(method)
            l.append(favgen)

            print(l)

            form_values = {'credit_id' : credit_id,
                           'password' : password,
                           'period' : period,
                           'method' : method,
                           'favgen' : favgen,
                           }
            if is_valid(l) == False:
                print("No Field can be left empty")
                error_msg = "No Field can be left empty"

            else:
                if is_valid_card(credit_id,password,method) == False:
                    print("Not a valid card")
                    error_msg = "Not a valid card"
                else:
                    push_into_db(l,u_id)
                    #redirect to login page
                    #return redirect("http://127.0.0.1:8000/user/login/")
    return render(response,'home\subscribe.html',{"error_msg":error_msg , "form_values": form_values})











