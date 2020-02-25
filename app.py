from flask import Flask, render_template, request, redirect, make_response
from datetime import  datetime, timedelta
import sqlite3 as sql
import calendar
from config import ADMIN_PASSWORD, COOKIE_LIVE_TIME

cookiePool = set()

app = Flask(__name__)


def get_Task(year, month, day):
    con = sql.connect("database.db")
    cur = con.cursor()

    ls = cur.execute("SELECT id, overview from TASK where year = ? AND month = ? AND day = ?", (year, month, day))

    ret = ''

    for eve in ls:
        ret = ret + '<a href=\"' + '../../task/' + str(eve[0]) + '\">' + str(eve[1]) + '</a><br>'
    return ret

def gen_Prv_Month(year, month):
    month = month - 1
    if month == 0:
        year = year - 1
        month = 12
    return '../' + str(year) + '/' + str(month)


def gen_Nxt_Month(year, month):
    month = month + 1
    if month == 13:
        year = year + 1
        month = 1
    return '../' + str(year) + '/' + str(month)


@app.route('/month/<int:year>/<int:month>')
def show_Month(year, month):
    monthNames = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    firstDay, daySiz = calendar.monthrange(year, month)
    firstDay += 1
    days = []
    tasks = []
    if firstDay != 7:
        for i in range(0, firstDay):
            days.append('')
            tasks.append('')
    for i in range(1, daySiz + 1):
        days.append(str(i))
        tasks.append(get_Task(year, month, i))
    while len(days) < 35:
        days.append('')
        tasks.append('')
    return render_template('month.html', curMonth = monthNames[month - 1], curYear = year, days = days, tasks = tasks,
                           link_prv_month = gen_Prv_Month(year, month), link_nxt_month = gen_Nxt_Month(year, month))

def gen_Link_Month(year, month):
    return '../month/' + str(year) + '/' + str(month)

@app.route('/task/<int:id>')
def show_Detail(id):
    con = sql.connect("database.db")
    cur = con.cursor()
    ls = cur.execute("SELECT year, month, day, overview, detail from TASK where id = ?", str(id))
    a = []
    for i in ls:
        a = i
    print(a)
    return render_template('task.html', year = a[0], month = a[1], day = a[2], overview = a[3], detail = a[4],
                           link_month = gen_Link_Month(a[0], a[1]))

@app.route('/')
def show_Index():
    curYear = datetime.now().year
    curMonth = datetime.now().month
    return render_template('index.html', cur_Link = 'month/' + str(curYear) + '/' + str(curMonth))



@app.route('/result', methods=("GET", "POST"))
def result():
    if(request.method == "GET"):
        return redirect('/')
    form = request.form.to_dict()
    return redirect('/month/' + str(form['Year']) + '/' + form['Month'])

def checkCookiePool(x):
    updateCookiePool()
    return x in cookiePool

def updateCookiePool():
    cur = str(datetime.now() - timedelta(seconds=COOKIE_LIVE_TIME))
    nw = []
    for x in cookiePool:
        if x >= cur:
            nw.append(x)
    cookiePool.clear()
    for x in nw:
        cookiePool.add(x)


def insertCookiePool(x):
    updateCookiePool()
    cookiePool.add(x)

@app.route('/login', methods=("GET", "POST"))
def login():
    if request.method == "GET":
        return render_template('login.html')
    form = request.form.to_dict()
    if form['password'] != ADMIN_PASSWORD:
        return 'Wrong Password' # returning a pure text
    resp = make_response(redirect('/admin'))
    resp.set_cookie('status', 'login')
    retStr = str(datetime.now())
    insertCookiePool(retStr)
    resp.set_cookie('time', retStr)
    return resp

@app.route('/admin')
def admin():
    status = request.cookies.get('status')
    if status != 'login':
        return 'Please login first' # returning a pure text
    loginTime = request.cookies.get('time')
    if not checkCookiePool(loginTime):
        return 'Login status timed out' # returning a pure text
    return render_template('admin.html')

@app.route('/admin/addtask', methods=("GET", "POST"))
def addtask():
    status = request.cookies.get('status')
    if status != 'login':
        return 'Please login first' # returning a pure text
    loginTime = request.cookies.get('time')
    if not checkCookiePool(loginTime):
        return 'Login status timed out' # returning a pure text


    if request.method == "GET":
        return render_template('addtask.html')
    form = request.form.to_dict()
    print(form)
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO TASK (id, year, month, day, overview, detail) VALUES (NULL, ?, ?, ?, ?, ?)", (form['year'], form['month'], form['day'], form['overview'], form['detail']))
    con.commit()
    con.close()

    return 'Task Added' # returning a pure text

@app.route('/admin/deltask', methods=("GET", "POST"))
def deltask():
    status = request.cookies.get('status')
    if status != 'login':
        return 'Please login first' # returning a pure text
    loginTime = request.cookies.get('time')
    if not checkCookiePool(loginTime):
        return 'Login status timed out' # returning a pure text


    if request.method == "GET":
        return render_template('deltask.html')
    form = request.form.to_dict()

    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("DELETE FROM TASK WHERE id = ?", form['id'])
    con.commit()
    con.close()

    return 'Task Deleted' # returning a pure text

if __name__ == '__main__':
    app.run(debug = True)