from flask import Flask, render_template, request
import pymysql
import datetime



connection = pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='kimi1992',
                             db='library')
print("Database connected...")
connection.query('SET GLOBAL connect_timeout=6000')

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/addmember', methods=['POST', 'GET'])
def new_member():
    return render_template('addmember.html')

@app.route('/new_member',methods=['POST', 'GET'])
def add_new_member():
    lib_ssn = request.form['Lib_SSN']
    mem_ssn = request.form['Mem_SSN']
    mem_name = str(request.form['Mem_Name'])
    campus_address = str(request.form['Mem_Address'])
    mem_phone = request.form['Mem_Phone']

    cur = connection.cursor()
    try:
        command = "insert into members(lib_SSN, SSN, Mem_name, Campus_Address, Phone_No, No_of_Books, Card_Issue_date, Card_Notice_date) values (" + lib_ssn + ", " + mem_ssn + ", '" + mem_name + "','" + campus_address + "', " + mem_phone + ", 0, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 6 MONTH) );"
        print(command)
        cur.execute(command)
        connection.commit()
        return render_template('index.html')
    except:
        return render_template('addmember.html', result="Library staff SSN/Member SSN is wrong")

@app.route('/addbook', methods=['POST', 'GET'])
def new_book():
    return render_template('addbook.html')

@app.route('/add_new_book',methods=['POST', 'GET'])
def add_new_book():
    lib_ssn = request.form['Lib_SSN']
    book_isbn = request.form['book_ISBN']
    title = request.form['Book_Title']
    Author = request.form['Book_Author']
    subject_area = request.form['Subj_Area']
    lang = request.form['lang']
    bind = request.form['bind']
    description = request.form['description']

    try:
        cur = connection.cursor()
        cmd1 = "insert into books values (" + book_isbn + ",'" + title + "', '" + Author + "', '" + subject_area + "', " + lib_ssn + ");"
        cur.execute(cmd1)
        connection.commit()
        cur2 = connection.cursor()
        cmd2 = "insert into available values(" + book_isbn + ", '" + lang + "', '" + bind + "', '" + description + "', 1);"
        print(cmd2)
        cur2.execute(cmd2)
        connection.commit()
        return render_template('index.html')
    except:
        return render_template('addbook.html', result="Wrong details found")

@app.route('/BorrowBook', methods=['POST', 'GET'])
def borrow_book():
    books_cursor = connection.cursor()
    books_cmd = "select b.ISBN, b.Title, b.Author, b.Subject_Area, a.descri, a.lang from available as a, books as b where b.ISBN=a.b_isbn and copies > 0;"
    print(books_cmd)
    books_cursor.execute(books_cmd)
    total = books_cursor.fetchall()
    print(total)
    return render_template('borrowBook.html', total=total)

@app.route('/borrow_this_book',methods=['POST', 'GET'])
def get_this_book():
    lib_ssn = request.form['Lib_SSN']
    book_isbn = request.form['book_ISBN']
    mem_ssn = request.form['mem_SSN']
    mem_cur = connection.cursor()

    cmd1 = "select * from members where SSN=" + mem_ssn +";"
    #print(cmd1)
    mem_cur.execute(cmd1)
    is_mem = mem_cur.fetchall()
    #print(is_mem)
    if (len(is_mem) == 0):
        return "Not a Member"
    else:
        NoofBooks = is_mem[0][4]
        gen_cur = connection.cursor()
        cmd2 = "select * from general_members where Mem_SSN=" + mem_ssn +";"
        gen_cur.execute(cmd2)
        is_gen = gen_cur.fetchall()

        if ((len(is_gen) != 0) and NoofBooks > 4):
            return render_template("borrowBook.html", result="Books borrow limit reached")
        else:
            try:
                if (len(is_gen) != 0):
                    days = 21
                    grace = 7
                else:
                    days = 90
                    grace = 14

                borrow_cur = connection.cursor()
                cmd3 = "insert into borrows values(" + book_isbn + ", " + lib_ssn + ", " + mem_ssn + ", CURDATE(), DATE_ADD(CURDATE(), INTERVAL " + str(days) + " DAY), " + str(grace) + " );"
                print(cmd3)
                borrow_cur.execute(cmd3)

                update_cur = connection.cursor()
                cmd4 = "update available set copies=0 where b_isbn=" + book_isbn + ";"
                update_cur.execute(cmd4)

                NoofBooks  = int(NoofBooks) + 1
                books_cur = connection.cursor()
                cmd5 = "update members set No_of_Books=" +  str(NoofBooks) + ";"
                books_cur.execute(cmd5)
            except:
                return render_template("borrowBook.html", result="Wrong Details provided")

    connection.commit()

    return render_template('index.html')

@app.route('/ReturnBook', methods=['POST', 'GET'])
def return_book():
    return render_template('ReturnBook.html')

@app.route('/return_this_book',methods=['POST', 'GET'])
def return_this_book():
    lib_ssn = request.form['Lib_SSN']
    book_isbn = request.form['book_ISBN']
    mem_ssn = request.form['Mem_SSN']

    #try:
    check_cur = connection.cursor()
    cmd1 = "select bo.b_isbn ,bo.book_issue_date, bo.b_return_date, CURDATE(), b.Title, b.Author FROM borrows as bo, books as b where bo.b_isbn= " + book_isbn + " and b.ISBN=bo.b_isbn;"
    print(cmd1)
    check_cur.execute(cmd1)
    result = check_cur.fetchall()
    print(result[0][3] - result[0][2])
    if (len(result) == 0):
        return render_template("borrowBook.html", result="The book is not borrowed")

    days = str(result[0][3] - result[0][2])
    title = str(result[0][4])
    author = str(result[0][5])
    borred_date = result[0][1]
    cur_date = result[0][3]
    print(days, title, author)
    available_cur = connection.cursor()
    cmd2 = "update available set copies=1 where b_isbn=" + book_isbn + ";"
    available_cur.execute(cmd2)

    delete_cur = connection.cursor()
    cmd3 = "delete from borrows where b_isbn=" + book_isbn + ";"
    delete_cur.execute(cmd3)

    noOfBooks_cur = connection.cursor()
    cmd4 = "select No_of_Books from members where SSN=" + mem_ssn + ";"
    noOfBooks_cur.execute(cmd4)
    count = noOfBooks_cur.fetchall()
    count = str(int(count[0][0]) - 1)
    up_cur = connection.cursor()
    cmd5 = "update members set No_of_Books=" + count + " where SSN=" + mem_ssn + ";"
    up_cur.execute(cmd5)

    new_cur = connection.cursor()
    cmd6 = "INSERT into borrow_history values(" + book_isbn + ", '" + str(borred_date)  + "', '" + str(cur_date) + "', " + mem_ssn + ");"
    print(cmd6)
    new_cur.execute(cmd6)
    connection.commit()


    #except:
    #    return render_template("ReturnBook.html", result="Wrong details provided")

    return render_template("ReturnBook.html", isbn=book_isbn, title=title, author=author, borred_date=borred_date, days=days, result="Receipt", cur_date=cur_date)

@app.route('/RenewMembership', methods=['POST', 'GET'])
def RenewMembership():
    return render_template('RenewMembership.html')

@app.route('/renew_membership',methods=['POST', 'GET'])
def renew_membership():
    lib_ssn = request.form['Lib_SSN']
    mem_ssn = request.form['Mem_SSN']

    try:
        renew_cur = connection.cursor()
        cmd = "update members set Card_Issue_date= CURDATE(), Card_Notice_date= DATE_ADD(CURDATE(), INTERVAL 6 MONTH) where SSN=" + mem_ssn + ";"
        print(cmd)
        renew_cur.execute(cmd)
        connection.commit()
    except:
        return render_template("RenewMembership.html", result="Wrong details provided")


    return render_template('index.html')

@app.route('/Weekly', methods=['POST', 'GET'])
def Weekly():
    return render_template("weekly.html")

@app.route('/get_weekly', methods=['POST', 'GET'])
def get_weekly():
    end_date = str(request.form['Date'])
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    start_date = end_date + datetime.timedelta(days=-7)

    week_con = connection.cursor()
    cmd = "select *, datediff(start_date, end_date) from borrow_history where end_date between '" + str(start_date)  +"' and '"  + str(end_date) + "';"
    print(cmd)
    week_con.execute(cmd)
    out = week_con.fetchall()

    new_cur = connection.cursor()
    cmd1 = "select *, datediff(book_issue_date, CURDATE()) as datediff from borrows;"
    new_cur.execute(cmd1)
    out_new = new_cur.fetchall()

    return render_template("weekly.html", out=out, out_new=out_new)


if __name__ == '__main__':
    app.run()
