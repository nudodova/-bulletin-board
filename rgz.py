from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, render_template, request, redirect, session
import psycopg2
from flask_login import login_required, current_user
from flask import jsonify

rgz = Blueprint('rgz', __name__)


def dbConnect():
    conn = psycopg2.connect(
        host="127.0.0.1",
        port="5432",
        database="doska_obyavleni",
        user="anastasia_udodova",
        password="0123456789")

    return conn

def dbClose(cursor, connection):
    cursor.close()
    connection.close()

@rgz.route('/rgz/')
def main():
    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM userss")

    result = cur.fetchall()

    print(result)

    dbClose(cur, conn)

    return "go to console"

@rgz.route('/rgz/mainpage')
def mainpage():
    username = session.get('username')
    return render_template('mainpage.html', username=username)

@rgz.route('/rgz/home')
def home():
    username = session.get('username')
    return render_template('home.html', username=username)


@rgz.route('/rgz/register', methods=["GET", "POST"])
def registerpage():
    errors=[]

    if request.method == "GET":
        return render_template("register.html", errors=errors)

    login = request.form.get("login")
    password = request.form.get("password")
    name = request.form.get("name")
    avatar = request.form.get("avatar")
    email = request.form.get("email")
    about = request.form.get("about")

    if not (login or password or name or avatar or email):
        errors.append("Пожалуйста, заполните все поля!")
        print(errors)
        return render_template("register.html", errors=errors)

    hashPassword = generate_password_hash(password)

    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT login FROM userss WHERE login = %s;", (login,))

    if cur.fetchone() is not None:
        errors.append("Пользователь с данным логином уже существует!")
        
        conn.close()
        cur.close()

        return render_template("register.html", errors=errors)

    
    cur.execute("INSERT INTO userss (login, password, name, email, about) VALUES (%s, %s, %s, %s, %s);", (login, hashPassword, name, email, about))
    conn.commit()
    conn.close()
    cur.close()

    return redirect("/rgz/login")

@rgz.route('/rgz/login', methods=["GET", "POST"])
def loginpage():
    errors = []

    if request.method == "GET":
        return render_template("login.html", errors=errors)

    login = request.form.get("login")
    password = request.form.get("password")

    if not (login or password):
        errors.append("Пожалуйста, заполните все поля!")
        return render_template("login.html", errors=errors)

    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT id, password FROM userss WHERE login = %s;", (login,))

    results = cur.fetchone()

    if results is None:
        errors.append("Неправильный логин или пароль")
        dbClose(cur, conn)
        return render_template("login.html", errors=errors)

    userId, hashPassword = results

    if check_password_hash(hashPassword, password):
        session['id'] = userId
        session['login'] = login
        dbClose(cur, conn)
        return redirect("/rgz/home")

    else:
        errors.append("Неправильный логин или пароль")
        dbClose(cur, conn)
        return render_template("login.html", errors=errors)


@rgz.route("/rgz/newadvertisement", methods = ["GET", "POST"])
def createArticle():
    errors = []

    userID = session.get('id')
    login = session.get('login')
    if userID is not None:
        if request.method =="GET":
            return render_template("newadvertisement.html", login=login)
        
        if request.method == "POST":
            advertisement_text = request.form.get("advertisement_text")
            title = request.form.get("advertisement_title")

            if len(advertisement_text)==0:
                errors.append("Заполните текст")
                return render_template("newadvertisement.html", errors = errors, login=login)
            
            conn = dbConnect()
            cur = conn.cursor()

            cur.execute("INSERT INTO advertisements (user_id, title, advertisement_text) VALUES (%s, %s, %s) RETURNING id;", (userID, title, advertisement_text))
            
            
            new_articl_id = cur.fetchone()[0]
            conn.commit()

            dbClose(cur, conn)

            return redirect(f"/rgz/advertisements")

    return redirect("/rgz/login")


@rgz.route('/rgz/advertisements')
def list_articles():
    conn = dbConnect()
    cur = conn.cursor()

    cur.execute("SELECT id, title, advertisement_text FROM advertisements;")
    articles_data = cur.fetchall()

    articles = [{'id': row[0], 'title': row[1], 'advertisement_text': row[2]} for row in articles_data]

    dbClose(cur, conn)

    return render_template('advertisements.html', articles=articles)


@rgz.route('/rgz/advertisements/<int:ad_id>/edit', methods=['GET', 'POST'])
def edit_article(ad_id):
    conn = dbConnect()
    cur = conn.cursor()

    if request.method == 'GET':
        cur.execute("SELECT id, title, advertisement_text FROM advertisements WHERE id = %s;", (ad_id,))
        article_data = cur.fetchone()

        dbClose(cur, conn)

        return render_template('edit_advertisement.html', article=article_data)

    elif request.method == 'POST':
        new_title = request.form.get('title')
        new_advertisement_text = request.form.get('advertisement_text')

        cur.execute("UPDATE advertisements SET title = %s, advertisement_text = %s WHERE id = %s;",
                    (new_title, new_advertisement_text, ad_id))
        conn.commit()

        dbClose(cur, conn)

        return redirect("/rgz/advertisements")


@rgz.route('/rgz/advertisements/<int:ad_id>', methods=['GET', 'POST'])
def delete_article(ad_id):
    if request.method == 'GET':
        
        conn = dbConnect()
        cur = conn.cursor()

        cur.execute("SELECT id, title, advertisement_text FROM advertisements WHERE id = %s;", (ad_id,))
        article_data = cur.fetchone()

        dbClose(cur, conn)

        return render_template('delete_confirmation.html', article=article_data)

    elif request.method == 'POST':
      
        conn = dbConnect()
        cur = conn.cursor()

        cur.execute("DELETE FROM advertisements WHERE id = %s;", (ad_id,))
        conn.commit()

        dbClose(cur, conn)

        return redirect("/rgz/advertisements")


@rgz.route('/rgz/logout', methods=["GET"])
def logout():
    session.clear()
    return redirect("/rgz/mainpage")

