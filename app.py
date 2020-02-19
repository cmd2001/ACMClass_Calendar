from flask import Flask, render_template
import sqlite3 as sql
import calendar

app = Flask(__name__)

@app.route('/hello/<int:score>')
def hello_name(score):
    return render_template('hello.html', marks = (score, score))

def getTask(year, month, day):
    con = sql.connect("database.db")
    cur = con.cursor()

    ls = cur.execute("SELECT id, overview from TASK where year = ? AND month = ? AND day = ?", (year, month, day))

    ret = ''

    for eve in ls:
        ret = ret + '<a href=\"task/' + str(eve[0]) + '\">' + str(eve[1]) + '</a><br>'
    return ret

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
        tasks.append(getTask(year, month, i))
    while len(days) < 35:
        days.append('')
        tasks.append('')
    return render_template('month.html', curMonth = monthNames[month - 1], curYear = year, days = days, tasks = tasks)

@app.route('/task/<int:id>')
def show_Detail(id):
    con = sql.connect("database.db")
    cur = con.cursor()
    ls = cur.execute("SELECT year, month, day, overview, detail from TASK where id = ?", str(id))
    a = []
    for i in ls:
        a = i
    print(a)
    return render_template('task.html', year = a[0], month = a[1], day = a[2], overview = a[3], detail = a[4])


if __name__ == '__main__':
    app.run(debug = True)