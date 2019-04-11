from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL      # import the function that will return an instance of a connection
from flask_bcrypt import Bcrypt
app = Flask(__name__)
import re

app.secret_key = 'keep it secret, keep it safe'

bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

#Homepage route
@app.route('/')
def index():
    if 'id' in session:
        return redirect('/wall')
    else:
        return render_template('index.html')

#New user route
@app.route('/register', methods = ["POST"])
def submit():
    is_valid = True
    if len(request.form["new_first"]) < 2:
        is_valid = False
        flash("Please enter a first name")
        print("Please enter a first name")
    if len(request.form["new_last"]) < 2:
        is_valid = False
        flash("Please enter a last name")
        print("Please enter a last name")
    if not EMAIL_REGEX.match(request.form["new_email"]):
        is_valid = False
        flash("Email is not Valid")
        print("Email is not Valid")

    if len(request.form["new_password"]) < 8:
        is_valid = False
        flash("Password must be at least 8 characters long.")
        print("Password must be at least 8 characters long.")
    elif request.form["new_password"] != request.form["con_password"]:
        is_valid = False
        flash("Passwords don't match")
        print("Passwords Don't Match")
    else:
        pw_hash = bcrypt.generate_password_hash(request.form["new_password"])
        print(pw_hash)

    if not is_valid:
        return redirect('/')
    else:
        data = {
            "fn": request.form["new_first"],
            "ln": request.form["new_last"],
            "em": request.form["new_email"],
            "pw": pw_hash
        }
        print("Data collected")
        #Register user query
        mysql = connectToMySQL('private_data')
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES(%(fn)s, %(ln)s, %(em)s, %(pw)s, NOW(), NOW());"
        flash(f"You've been successfully registered")
        new_account = mysql.query_db(query, data)
        mysql = connectToMySQL('private_data')
        print("You've been successfully registered")

        #Name and ID query
        mysql = connectToMySQL('private_data')
        query = "SELECT * FROM users WHERE email = %(em)s"
        data = {
            "em": request.form["new_email"]
        }
        result = mysql.query_db(query, data)
        session['name'] = result[0]['first_name'] + ' ' + result[0]['last_name']
        session['id'] = result[0]['id']
        return redirect('/wall')

#Login route
@app.route('/login', methods = ['POST'])
def login():
    mysql = connectToMySQL('private_data')
    query = "SELECT * FROM users WHERE email = %(em)s"
    data = {
        "em": request.form["user_email"]
    }
    result = mysql.query_db(query, data)
    if len(result) > 0:
        if bcrypt.check_password_hash(result[0]['password'], request.form['user_password']):
            session['name'] = result[0]['first_name'] + ' ' + result[0]['last_name']
            session['id'] = result[0]['id']
            flash(f"You've been successfully been logged in")
            print("You've been successfully been logged in")
            return redirect('/wall')
    flash("You could not be logged in")
    return redirect('/')

@app.route('/wall')
def success():
    if 'id' not in session:
        flash("Noone is currently logged in")
        print("Noone is currently logged in")
        return redirect('/')
    else:
        #Message board query
        data = {
            "id": session["id"]
        }
        mysql = connectToMySQL('private_data')
        messages = mysql.query_db('SELECT messages.id, messages.from_id, users.first_name, messages.to_id, user2.first_name, user2.last_name, messages.message, messages.created_at FROM messages JOIN users ON users.id = messages.from_id JOIN users AS user2 ON user2.id = messages.to_id WHERE messages.to_id = %(id)s;', data)

        #Message count
        mysql = connectToMySQL('private_data')
        count = mysql.query_db('SELECT COUNT(messages.to_id) FROM messages JOIN users ON users.id = messages.from_id JOIN users AS user2 ON user2.id = messages.to_id WHERE messages.to_id = %(id)s', data)

        #General query except for user in session
        mysql = connectToMySQL('private_data')
        other_users = mysql.query_db('SELECT * FROM users WHERE id != %(id)s;', data)
        return render_template('success.html', my_messages = messages, to_send = other_users, messages_num = len(messages), messages_sent = count[0]['COUNT(messages.to_id)'])

@app.route('/send', methods = ['POST'])
def send_message():
    mysql = connectToMySQL('private_data')
    query = "INSERT INTO messages (from_id, to_id, message) VALUES (%(from)s, %(to)s, %(mess)s);"
    data = {
        "to": request.form["reciever"],
        "mess": request.form["message"],
        "from": session['id']
    }
    new_message = mysql.query_db(query, data)
    flash("message has been sent")
    print(new_message)
    return redirect('/wall')

@app.route('/<sessionid>/<messageid>/delete')
def delete(sessionid, messageid):
    userid = sessionid
    num = messageid
    if not session:
        flash("You can't do that")
        return redirect('/')
    if userid != session['id']:
        flash("You can't do that")
        return redirect('/')
    else:
        mysql = connectToMySQL('private_data')
        query = "DELETE FROM messages WHERE id = %(id)s"
        data = {
            "id": num
        }
        delete_message = mysql.query_db(query, data)
        flash("message has been deleted")
        print(f"{delete_message} has been deleted")
        return redirect('/wall')

@app.route('/logout')
def logout():
    session.clear()
    flash("You've been successfully logged out")
    print("You've been successfully logged out")
    return redirect('/')

if __name__ =='__main__':
    app.run(debug=True)