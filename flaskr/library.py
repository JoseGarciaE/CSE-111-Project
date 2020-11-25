from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from random import randint

bp = Blueprint('library', __name__)

def getUser():
    db = get_db()
    user = 'student'
    if db.execute('SELECT l_userid FROM Librarian WHERE l_userid = ?', (g.user["u_userid"],)).fetchone() is not None:
        user = 'librarian'
    return user

def getUniversity():
    db = get_db()
    return db.execute('SELECT * FROM University WHERE un_id = ?',(g.user["u_universityid"],)).fetchone()

def getAllBooks():
    db = get_db()
    return db.execute(
    'SELECT * FROM Books, Author, Stockroom, University WHERE s_universityid = un_id AND b_isbn = s_isbn AND b_authorid = a_authorid AND s_universityid = ?',(g.user["u_universityid"],)
    ).fetchall()
def getFilteredBooks(filter, input):
    db = get_db()
    input = "%" + input + "%"
    if filter == "title":
        temp = 'b_title LIKE ?'
    elif filter == 'author':
        temp = 'a_authorname LIKE ?'
    elif filter == 'year':
        temp = 'b_publishedyear LIKE ?'
    else:
        temp = "b_isbn LIKE ?"

    query = "SELECT * FROM Books, Author, Stockroom, University WHERE s_universityid = un_id AND b_isbn = s_isbn AND b_authorid = a_authorid AND s_universityid = ? AND " + temp

    return db.execute(query,([g.user["u_universityid"], input])).fetchall()

def getLibraryUsers():
    db = get_db()
    return db.execute('SELECT * FROM User, University WHERE u_universityid = un_id AND un_id = ?',(g.user["u_universityid"],)).fetchall()
def getFilteredUsers(filter, input):
    db = get_db()
    input = "%" + input + "%"
    if filter == "name":
        temp = 'u_name LIKE ?'
    else:
        temp = 'u_email LIKE ?'
    
    query = "SELECT * FROM User, University WHERE u_universityid = un_id AND un_id = ? AND " + temp

    return db.execute(query,([g.user["u_universityid"], input])).fetchall()
def insertBooks(title, author, year, isbn, copies):
    db = get_db()
    cur = db.cursor()
    checkAuthor = cur.execute('SELECT a_authorid FROM Author WHERE a_authorname = ?', (author,)).fetchone()

    id = randint(0,100000)
    while cur.execute('SELECT * FROM Books WHERE b_bookid = ?', (id,)).fetchone() is not None:
        id = randint(0,100000)

    if checkAuthor is not None:
        db.execute(
            'INSERT INTO Books (b_bookid, b_isbn, b_authorid, b_publishedyear, b_title) VALUES (?, ?, ?, ?, ?)',
                (id,isbn,checkAuthor["a_authorid"],year,title)
        )
        db.execute(
            'INSERT INTO StockRoom (s_universityid,s_isbn,s_bookcount) VALUES (?,?,?)',
                (g.user["u_universityid"], isbn, copies)
        )   

@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'GET':
        return render_template('library/index.html', user=getUser(), university=getUniversity(), books=getAllBooks())

    if request.method == 'POST':
        button = request.form["button"]
        if button == "refresh books" or button == "return to books":
            return render_template('library/index.html', user=getUser(), university=getUniversity(), books=getAllBooks())
        if button == "filter books":
            return render_template('library/index.html', user=getUser(), university=getUniversity(), books=getFilteredBooks(request.form["filter"],request.form['input']))
        if button == "insert books":
            insertBooks(request.form['title'],request.form['author'],request.form['year'],request.form['isbn'],request.form['copies'])
            return render_template('library/index.html', user=getUser(), university=getUniversity(), books=getAllBooks())

        if button == "refresh users" or button == "search users":
            return render_template('library/index.html', user=getUser(), university=getUniversity(), libraryUsers=getLibraryUsers())
        if button == "filter users":
            return render_template('library/index.html', user=getUser(), university=getUniversity(), libraryUsers=getFilteredUsers(request.form["filter"],request.form['input']))
            