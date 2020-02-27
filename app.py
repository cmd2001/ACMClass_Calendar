from flask import Flask, render_template, request, redirect, make_response
from datetime import datetime, timedelta
import sqlite3 as sql
import calendar
from uuid import uuid4
from config import ADMIN_PASSWORD, COOKIE_LIVE_TIME

cookiePool = {}

app = Flask(__name__)


def takeThird(ele):
    return ele[2]

def get_Task(year, month, day):
    con = sql.connect("database.db")
    cur = con.cursor()

    ls = cur.execute("SELECT id, overview, startTime from TASK where year = ? AND month = ? AND day = ?", (year, month, day))

    srt = []

    for eve in ls:
        srt.append(eve)

    srt.sort(key=takeThird)

    ret = ''

    for eve in srt:
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
    ls = cur.execute("SELECT year, month, day, overview, detail, startTime, endTime from TASK where id = ?", str(id))
    a = []
    for i in ls:
        a = i
    return render_template('task.html', year = a[0], month = a[1], day = a[2], overview = a[3], detail = a[4].replace('\n', '<br>'), startTime = a[5], endTime = a[6],
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
    for key, value in cookiePool.items():
        if value > cur:
            nw.append((key, value))
    cookiePool.clear()
    for key, value in nw:
        cookiePool[key] = value


def insertCookiePool(key, value):
    updateCookiePool()
    cookiePool[key] = value

@app.route('/login', methods=("GET", "POST"))
def login():
    if request.method == "GET":
        return render_template('login.html')
    form = request.form.to_dict()
    if form['password'] != ADMIN_PASSWORD:
        return 'Wrong Password' # returning a pure text
    resp = make_response(redirect('/admin'))
    resp.set_cookie('status', 'login')
    userID = str(uuid4())
    retStr = str(datetime.now())
    insertCookiePool(userID, retStr)
    resp.set_cookie('id', userID)
    return resp

@app.route('/admin')
def admin():
    status = request.cookies.get('status')
    if status != 'login':
        return 'Please login first' # returning a pure text
    userID = request.cookies.get('id')
    if not checkCookiePool(userID):
        return 'Login status timed out or invalid' # returning a pure text
    return render_template('admin.html')

def valid(form):
    if not form['year'].isdigit(): # not a number
        return False
    if int(form['year']) < 1000 or int(form['year']) > 9999: # out of range
        return False
    if not form['month'].isdigit():
        return False
    if int(form['month']) < 1 or int(form['month']) > 12:
        return False
    if not form['day'].isdigit():
        return False
    if int(form['day']) < 1 or int(form['day']) > 31:
        return False
    startTime = form['startTime'].split(':')
    if len(startTime) != 2: # more or less ':'
        return False
    if not startTime[0].isdigit() or not startTime[1].isdigit():
        return False
    if int(startTime[0]) < 0 or int(startTime[0]) > 24:
        return False
    if int(startTime[1]) < 0 or int(startTime[1]) > 60:
        return False
    endTime = form['endTime'].split(':')
    if len(endTime) != 2: # more or less ':'
        return False
    if not endTime[0].isdigit() or not endTime[1].isdigit():
        return False
    if int(endTime[0]) < 0 or int(endTime[0]) > 24:
        return False
    if int(endTime[1]) < 0 or int(endTime[1]) > 60:
        return False
    return True

@app.route('/admin/addtask', methods=("GET", "POST"))
def addtask():
    status = request.cookies.get('status')
    if status != 'login':
        return 'Please login first' # returning a pure text
    userID = request.cookies.get('id')
    if not checkCookiePool(userID):
        return 'Login status timed out or invalid' # returning a pure text


    if request.method == "GET":
        return render_template('addtask.html')
    form = request.form.to_dict()
    if not valid(form):
        return 'Illegal Inout' # returning a pure text
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO TASK (id, year, month, day, overview, detail, startTime, endTime) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
                (form['year'], form['month'], form['day'], form['overview'], form['detail'], form['startTime'], form['endTime']))
    con.commit()
    con.close()

    return 'Task Added' # returning a pure text

@app.route('/admin/deltask', methods=("GET", "POST"))
def deltask():
    status = request.cookies.get('status')
    if status != 'login':
        return 'Please login first' # returning a pure text
    userID = request.cookies.get('id')
    if not checkCookiePool(userID):
        return 'Login status timed out or invalid' # returning a pure text

    if request.method == "GET":
        return render_template('deltask.html')
    form = request.form.to_dict()

    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("DELETE FROM TASK WHERE id = ?", form['id'])
    con.commit()
    con.close()

    return 'Task Deleted' # returning a pure text

def convertDigit(x):
    if len(x) < 2:
        x = '0' + x
    return x
def convertTask(x):
    ret = 'BEGIN:VEVENT\n'
    ret = ret + 'DTSTART:' + x[0] + convertDigit(x[1]) + convertDigit(x[2]) + 'T' + convertDigit(x[5].split(':')[0]) + convertDigit(x[5].split(':')[1]) + '00\n'
    ret = ret + 'DTEND:' + x[0] + convertDigit(x[1]) + convertDigit(x[2]) + 'T' + convertDigit(x[6].split(':')[0]) + convertDigit(x[6].split(':')[1]) + '00\n'
    ret = ret + 'SUMMARY:' + x[3] + '\n'
    ret = ret + 'DESCRIPTION:' + x[4].replace('\r', '').replace('\n', '\\n') + '\n'
    ret = ret + 'END:VEVENT\n'
    return ret

@app.route('/calendar.ics')
def getIcs():
    con = sql.connect("database.db")
    cur = con.cursor()
    ls = cur.execute("SELECT year, month, day, overview, detail, startTime, endTime from TASK")

    ret = 'BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:ACMClass Calendar Beta\n'
    for x in ls:
        ret = ret + convertTask(x)
    ret = ret + 'END:VCALENDAR\n'
    return ret

@app.route('/robots.txt')
def getRobots():
    return 'User-Agent: *\nDisallow: /\n'

if __name__ == '__main__':
    app.run(debug = True)