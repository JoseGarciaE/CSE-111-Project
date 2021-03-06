import click
import sqlite3
import sys
import os
import random
import datetime
import string
from sqlite3 import Error
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

#Function to initiate application
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

#Function to initiate database
def init_db():
    db = get_db()

    initializeDatabase()
    # with current_app.open_resource('schema.sql') as f:
    #     db.executescript(f.read().decode('utf8'))

#Function to get database
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

#Function to close database
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

#Function to connect database
@click.command('init-db')
@with_appcontext
def init_db_command():
    #Clear the existing data and create new table
    sys.path.append('/flaskr/')
    
    init_db()
    click.echo('Initialized the database.')

############################################
########## POPULATE TABLES #################
############################################

users_file = "./book_data/users.txt"
checked_file = "./book_data/inputChecked.txt"
reserved_file = "./book_data/inputReserved.txt"

def openConnection(_dbFile):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """

    conn = None
    try:
        conn = sqlite3.connect(_dbFile)
    except Error as e:
        print(e)


    return conn

def closeConnection(_conn, _dbFile):

    try:
        _conn.close()
    except Error as e:
        print(e)


def createTables(_conn):

    try:
        sql = """CREATE TABLE RawBooks (
                    b_goodreadsid DECIMAL(13, 0), 
                    b_isbn VARCHAR(13) PRIMARY KEY, 
                    b_authornames VARCHAR(40) NOT NULL, 
                    b_publishedyear DECIMAL(4,0) NOT NULL,
                    b_title VARCHAR(50) NOT NULL, 
                    b_image_url TEXT,
                    b_small_image_url TEXT
                )"""
        _conn.execute(sql)

        sql = """CREATE TABLE Books (
                    b_bookid DECIMAL(13, 0), 
                    b_isbn VARCHAR(13) PRIMARY KEY, 
                    b_authorid INTEGER NOT NULL,
                    b_publishedyear DECIMAL(4,0) NOT NULL,
                    b_title VARCHAR(50) NOT NULL,
                    b_image_url TEXT,
                    b_small_image_url TEXT
                )"""
        _conn.execute(sql)

        sql = """CREATE TABLE RawBookTags (
                    bt_goodreadsid DECIMAL(13, 0), 
                    bt_tagid DECIMAL(10, 0),
                    bt_tagcount DECIMAL(10, 0))"""
        _conn.execute(sql)

        sql = """CREATE TABLE BookTags (
                    bt_bookid DECIMAL(13, 0), 
                    bt_tagid DECIMAL(10, 0))"""
        _conn.execute(sql)

        sql = """CREATE TABLE RawTags (
                    t_tagid DECIMAL(10, 0) PRIMARY KEY,
                    t_description VARCHAR(30, 0))"""
        _conn.execute(sql)

        sql = """CREATE TABLE Tags (
                    t_tagid DECIMAL(2, 0) PRIMARY KEY,
                    t_description VARCHAR(30, 0))"""
        _conn.execute(sql)

        sql = """CREATE TABLE University (
                    un_id DECIMAL(2, 0) PRIMARY KEY,
                    un_name VARCHAR(30, 0),
                    un_address VARCHAR(30, 0))"""
        _conn.execute(sql)

        sql = """CREATE TABLE StockRoom (
                    s_universityid DECIMAL(2, 0),
                    s_isbn VARCHAR(13),
                    s_bookcount DECIMAL(2, 0))"""
        _conn.execute(sql)

        sql = """CREATE TABLE User (
                    u_userid INTEGER PRIMARY KEY AUTOINCREMENT,
                    u_name TEXT NOT NULL,
                    u_email TEXT NOT NULL,
                    u_password TEXT NOT NULL,
                    u_universityid TEXT NOT NULL)"""
        _conn.execute(sql)

        sql = """CREATE TABLE Librarian (
                    l_userid INTEGER PRIMARY KEY,
                    l_salary DECIMAL(4,0))"""
        _conn.execute(sql)

        sql = """CREATE TABLE LibraryUser (
                    lu_userid INTEGER PRIMARY KEY,
                    lu_major TEXT NOT NULL)"""
        _conn.execute(sql)

        sql = """CREATE TABLE CheckedBooks (
                    cb_isbn VARCHAR(13),
                    cb_userid INTEGER,
                    cb_checkeddate DATE,
                    cb_experiationdate DATE)"""
        _conn.execute(sql)

        sql = """CREATE TABLE ReservedBooks (
                    r_isbn VARCHAR(13),
                    r_foruserid INTEGER,
                    r_reservatindate DATE,
                    r_reason TEXT)"""
        _conn.execute(sql)

        sql = """CREATE TABLE Author (
                    a_authorid INTEGER PRIMARY KEY AUTOINCREMENT,
                    a_authorname VARCHAR(40) NOT NULL)"""
        _conn.execute(sql)

        _conn.commit()
        
    except Error as e:
        _conn.rollback()
        print(e)


def dropTables(_conn):

    try:
        sql = "DROP TABLE IF EXISTS Books"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS RawBooks"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS RawBookTags"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS RawTags"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS BookTags"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS Tags"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS University"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS StockRoom"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS User"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS Librarian"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS LibraryUser"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS CheckedBooks"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS ReservedBooks"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS Author"
        _conn.execute(sql)


        _conn.commit()
    except Error as e:
        _conn.rollback()
        print(e)


def bulkLoadData():
    try:
        cmd = r"sqlite3 ./instance/data.sqlite < ./book_data/bulk_loading.sql"
        os.system(cmd)
    except Error as e:
        print("Error bulkloading data")

def populateUniversity(_conn):
    try:
        products = [
            (1, "UC Merced", "5200 Lake Rd, Merced, CA 95343"),
            (2, "UC Riverside", "900 University Ave, Riverside, CA 92521"),
            (3, "UC San Diego", "9500 Gilman Dr, La Jolla, CA 92093"),
            (4, "UC Santa Barbara", "Santa Barbara, CA 93106"),
            (5, "UC Davis", "1 Shields Ave, Davis, CA 95616")
        ]

        sql = "INSERT INTO University VALUES(?, ?, ?)"
        _conn.executemany(sql, products)

        _conn.commit()
    except Error as e:
        _conn.rollback()
        print(e)

def populateTags(_conn):
    try:
        products = [
            (1, "nonfiction"),
            (2, "action"),
            (3, "romance"),
            (4, "humor"),
            (5, "comedy"),
            (6, "murder"),
            (7, "mystery"),
            (8, "best-books"),
            (9, "novel"),
            (10, "fantasy")
        ]

        sql = "INSERT INTO Tags VALUES(?, ?)"
        _conn.executemany(sql, products)

        _conn.commit()
    except Error as e:
        _conn.rollback()
        print(e)

def cleanBooksTable(_conn):

    try: 
        sql = """
                delete 
                from RawBooks
                where not length(b_title) > 0 or 
                    not b_title glob '*[A-Za-z]*' or 
                    not length(cast(b_publishedyear as text)) > 0 or
                    not length(b_isbn) > 0
            """
        
        _conn.execute(sql)

        _conn.commit()

    except Error as e: 
        _conn.rollback()
        print(e)

def cleanRawTagsTable(_conn, _genres):

    try: 
        sqlDeleteInvalidRows = """
            delete 
            from RawTags
            where not length(t_description) > 0 or 
                not t_description glob '*[A-Za-z]*'
        """

        sqlUpdateGenres = """
            update RawTags
            set t_description = "{}"
            where t_description like "%{}%"
        """

        sqlRemoveLeftOver = """
            delete
            from RawTags 
            where t_description not in (
                select t_description 
                from RawTags 
                where t_description = "nonfiction" or 
                    t_description = "action" or 
                    t_description = "romance" or 
                    t_description = "humor" or 
                    t_description = "comedy" or
                    t_description = "murder" or  
                    t_description = "mystery" or 
                    t_description = "best-books" or
                    t_description = "novel" or
                    t_description = "fantasy"
            )
        """

        _conn.execute(sqlDeleteInvalidRows)
        _conn.commit()

        for genre in _genres:
            tempSql = sqlUpdateGenres.format(genre, genre)
            _conn.execute(tempSql)

        _conn.commit()

        _conn.execute(sqlRemoveLeftOver)
        _conn.commit()

    except Error as e: 
        _conn.rollback()
        print(e)


def cleanTagsData(_conn):

    genres = [
        "nonfiction",
        "action",
        "romance",
        "humor",
        "comedy",
        "murder",
        "mystery",
        "best-books",
        "novel",
        "fantasy"
    ]

    try: 
        
        cleanBooksTable(_conn)
        cleanRawTagsTable(_conn, genres)

    except Error as e: 
        _conn.rollback()
        print(e)

def populateBookTagsTable(_conn):

    genres = [
        "nonfiction",
        "action",
        "romance",
        "humor",
        "comedy",
        "murder",
        "mystery",
        "best-books",
        "novel",
        "fantasy"
    ]

    try: 
        sqlCopy = """ 
            insert into BookTags
            select bt_goodreadsid, bt_tagid
            from RawBookTags
            where bt_tagid in 
                (
                    select t_tagid
                    from RawTags
                )
            order by bt_goodreadsid
        """

        sqlUpdateTagIDs = """
            update BookTags
            set bt_tagid = ?
            where bt_tagid in 
            (
                select t_tagid
                from RawTags
                where t_description = ?
            )
        """

        sqlRemoveDuplicates = """
            delete from BookTags
            where rowid not in (
                select min(rowid)
                from BookTags 
                group by bt_tagid, bt_bookid
            )
        """

        _conn.execute(sqlCopy)

        _conn.commit()
        
        counter = 1

        for genre in genres:
            args = [counter, genre]
            _conn.execute(sqlUpdateTagIDs, args)
            counter += 1

        _conn.commit()
        
        _conn.execute(sqlRemoveDuplicates)
        _conn.commit()

    except Error as e: 
        _conn.rollback()
        print(e)


def dropExtraTables(_conn):
    try: 
        sql = "DROP TABLE IF EXISTS RawBookTags"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS RawTags"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS RawBooks"
        _conn.execute(sql)

        _conn.commit()

    except Error as e: 
        _conn.rollback()
        print(e)


def insertStockRoomEntries(_conn, _entries, _u_id):

    try:   
        
        entriesToInsert = []

        for entry in _entries:
            isbn = entry[0]
            randomNum = random.randrange(1, 11)

            newEntry = [_u_id, isbn, randomNum]
            entriesToInsert.append(newEntry)

        sql = "INSERT INTO StockRoom VALUES(?, ?, ?)"
        _conn.executemany(sql, entriesToInsert)
        _conn.commit()

    except Error as e:
        _conn.rollback()
        print(e)


def populateStockRooms(_conn):

    try:
        sql = """
            select b_isbn
            from RawBooks
            where substr(b_authornames, 1, 1) >= ? and
                substr(b_authornames, 1, 1) <= ?
        """
        ranges = [
            ('A', 'D'),
            ('E', 'J'),
            ('K', 'L'),
            ('M', 'R'),
            ('S', 'Z')
        ]

        cur = _conn.cursor()

        for i in range(0, 5):
            args = [ranges[i][0], ranges[i][1]] 
            cur.execute(sql, args)

            temp = cur.fetchall()
            insertStockRoomEntries(_conn, temp, i + 1)


    except Error as e: 
        _conn.rollback()
        print(e)

def populateAuthorTable(_conn):

    try:
        sql = """
            insert into Author (a_authorname)
            select distinct b_authornames
            from RawBooks
        """

        _conn.execute(sql)

        _conn.commit()
    except Error as e: 
        _conn.rollback()
        print(e)

def populateBooksTable(_conn):

    try:

        sql = """
            alter table RawBooks
            add column b_authorid INTEGER
        """

        _conn.execute(sql)

        sql = """
            update RawBooks 
            set b_authorid = 
            (select a_authorid from Author where b_authornames = a_authorname)
        """

        _conn.execute(sql)

        sql = """
            insert into Books
            select R.b_goodreadsid, R.b_isbn, R.b_authorid, R.b_publishedyear, R.b_title, R.b_image_url, R.b_small_image_url
            from RawBooks R
        """

        _conn.execute(sql)

        _conn.commit()
    except Error as e: 
        _conn.rollback()
        print(e)


def getUserIDFromEmail(_conn, u_email):

    try:
        sql = "SELECT u_userid FROM User WHERE u_email = ?"

        cur = _conn.cursor()

        cur.execute(sql, [u_email])

        user_id = cur.fetchone()

        return user_id[0]

    except Error as e:
        _conn.rollback()
        print(e)

def insertLibraryUsers(_conn, user_emails):
    """
    Reference: https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
    Use: For random majors for sample data
    """

    try:
        libraryUsers = []

        for user_email in user_emails:
            randomMajor = ''.join(random.choice(string.printable) for _ in range(10))
            user_id = getUserIDFromEmail(_conn, user_email)
            
            newEntry = [user_id, randomMajor]

            libraryUsers.append(newEntry)

        sql = "INSERT INTO LibraryUser VALUES(?, ?)"

        _conn.executemany(sql, libraryUsers)
        _conn.commit()

    except Error as e:
        _conn.rollback()
        print(e)


def insertLibrarians(_conn, user_emails):

    try:
        librarians = []

        for user_email in user_emails:
            randomSalary = random.randrange(30000, 80000, 2500)
            user_id = getUserIDFromEmail(_conn, user_email)
            
            newEntry = [user_id, randomSalary]

            librarians.append(newEntry)

        sql = "INSERT INTO Librarian VALUES(?, ?)"

        _conn.executemany(sql, librarians)
        _conn.commit()

    except Error as e:
        _conn.rollback()
        print(e)


def populateSampleUsers(_conn):

    raw_users = getLinesFromFile(users_file)

    sampleUsers = []
    sampleLibraryUsers = []
    sampleLibrarians = []

    for i, user in enumerate(raw_users):
        raw_user = user.split()
        
        newEntryUser = (raw_user[0], raw_user[1], generate_password_hash(raw_user[2]), raw_user[3])
    
        sampleUsers.append(newEntryUser)

        if i >= len(raw_users) - 5:
            sampleLibrarians.append(raw_user[1])
            continue
        
        sampleLibraryUsers.append(raw_user[1])


    try:
        sql = """INSERT INTO User(u_name, u_email, u_password, u_universityid) VALUES(?, ?, ?, ?)"""
        _conn.executemany(sql, sampleUsers)

        _conn.commit()

        insertLibrarians(_conn, sampleLibrarians)
        insertLibraryUsers(_conn, sampleLibraryUsers)

    except Error as e:
        _conn.rollback()
        print(e)

def populateTables(_conn):

    try: 
        bulkLoadData()

        # Manually populated
        populateUniversity(_conn)
        populateTags(_conn)

        # Remap IDs and remove unnecessary tuples
        cleanTagsData(_conn)

        # Populate new table from raw data
        populateBookTagsTable(_conn)

        # Separate author from large table
        populateAuthorTable(_conn)

        # Clean and insert book data
        populateBooksTable(_conn)

        # Populate stock rooms using available data
        populateStockRooms(_conn)

        # Insert sample users
        populateSampleUsers(_conn)

        # Drop original tables
        dropExtraTables(_conn)

    except Error as e: 
        print(e)


def getLinesFromFile(_file):
    """ Returns the contents of a file as a list."""

    with open(_file, "r") as f:
        raw_input = f.readlines()

    input = []
    for raw_line in raw_input:
        line = raw_line.rstrip()
        if line:
            input.append(line.rstrip())
    
    return input


def insertCheckedEntry(_conn, entry):

    try:
        sql = "INSERT INTO CheckedBooks VALUES(?, ?, ?, ?)"

        _conn.execute(sql, entry)
        _conn.commit()
    except Error as e:
        _conn.rollback()
        print(e)

def insertReservedEntry(_conn, entry):

    try:
        sql = "INSERT INTO ReservedBooks VALUES(?, ?, ?, ?)"

        _conn.execute(sql, entry)
        _conn.commit()
    except Error as e:
        _conn.rollback()
        print(e)

def checkoutSampleBooks(_conn):

    try: 
        sqlGetBook = """
            select b_isbn, s_bookcount
            from Books, StockRoom, University
            where b_isbn = s_isbn and 
                s_universityid = un_id and 
                un_id = ? and 
                b_isbn = ?
        """

        sqlUpdateStockRoomCount = """
            update StockRoom
            set s_bookcount = (
                select s_bookcount - 1
                from StockRoom, Books, University
                where b_isbn = s_isbn and 
                    s_universityid = un_id and 
                    s_universityid = ? and 
                    s_isbn = ?)
            where s_isbn = ? and 
                s_universityid = ?
        """

        cur = _conn.cursor()

        simulatedInput = getLinesFromFile(checked_file)


        for line in simulatedInput:
            words = line.split()
            
            un_id = int(words[0])
            user_id = int(words[1])
            isbn = words[2]

            args = [un_id, isbn]

            cur.execute(sqlGetBook, args)
            bookEntry = cur.fetchall()

            if bookEntry:
                count = bookEntry[0][1]

                if count >= 1:

                    checkedDate = datetime.datetime.today()
                    #tempDate
                    expirationDate = checkedDate + datetime.timedelta(days=30)

                    checkedDate = checkedDate.strftime('%Y-%m-%d')
                    expirationDate = expirationDate.strftime('%Y-%m-%d')
                    newEntry = [
                        isbn,
                        user_id,
                        checkedDate,
                        expirationDate
                    ]
                    insertCheckedEntry(_conn, newEntry)

            args = [un_id, isbn, un_id, isbn]
            _conn.execute(sqlUpdateStockRoomCount, args)

            _conn.commit()

    except Error as e:
        _conn.rollback()
        print(e)


def reserveSampleBooks(_conn):
    
    reason_location = "NOT IN SCHOOL"
    reason_copies = "NO MORE COPIES"

    try: 
        sqlGetBook = """
            select b_isbn, s_bookcount
            from Books, StockRoom, University
            where b_isbn = s_isbn and 
                s_universityid = un_id and 
                un_id = ? and 
                b_isbn = ?
        """

        cur = _conn.cursor()

        simulatedInput = getLinesFromFile(reserved_file)


        for line in simulatedInput:
            words = line.split()
            
            un_id = int(words[0])
            user_id = int(words[1])
            isbn = words[2]

            args = [un_id, isbn]

            cur.execute(sqlGetBook, args)
            bookEntry = cur.fetchall()

            reservedDate = datetime.datetime.today().strftime('%Y-%m-%d')

            newEntry = []

            if len(bookEntry) != 0:
                count = bookEntry[0][1]

                if count == 0:

                    newEntry = [
                        isbn,
                        user_id,
                        reservedDate,
                        reason_copies
                    ]
            else:
                newEntry = [
                        isbn,
                        user_id,
                        reservedDate,
                        reason_location
                    ]    
                
            insertReservedEntry(_conn, newEntry)
            _conn.commit()

    except Error as e:
        _conn.rollback()
        print(e)


def initializeDatabase():
    database = r"./instance/data.sqlite"

    # print(os.getcwd())
    
    # create a database connection
    conn = openConnection(database)
    with conn:
        dropTables(conn)
        createTables(conn)
        populateTables(conn)


        checkoutSampleBooks(conn)
        reserveSampleBooks(conn)


    closeConnection(conn, database)

