from flask import Flask, render_template,request,session,redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
import sqlite3, random, string
from functools import wraps





app = Flask(__name__)
app.secret_key = 'shixymanflowx'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db =SQLAlchemy(app)
app.app_context().push()
# to fix error working outside of application context
#add app.app_context().push()
#Run in terminal
#   python3
#   from app import app
#   from app import db
#   db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

# Create custom error pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

# create route and class fot todo
class Todo(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)
    
@app.route('/todo')
def todo():
    #show all todos
    todo_list = Todo.query.all()
    return render_template('todo.html',todo_list =todo_list)

@app.route('/add',methods= ["POST"])
def add():
    #add new todo
    title = request.form.get("title")
    new_todo =Todo(title=title,complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("todo"))


@app.route('/update/<int:todo_id>')
def update(todo_id):
    #update new todo
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("todo"))

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    #delete new todo
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("todo"))

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/monster')
def monster():
    return render_template('monster.html')




@app.route('/blog', methods=['GET', 'POST'])
def blog():
    # Connect to db
    db = sqlite3.connect('posts.db')
    cursor = db.cursor()

    if request.method == 'POST':
        # Get search query from request form
        search_query = request.form.get('q')

        if search_query:
            # Search for posts containing the query
            cursor.execute("SELECT * FROM posts WHERE title LIKE ? OR post LIKE ?",
                           ('%' + search_query + '%', '%' + search_query + '%'))
        else:
            # Get all posts from db
            cursor.execute('SELECT * FROM posts')
        
    elif request.method == 'GET':
        # Get search query from request args
        search_query = request.args.get('q')

        if search_query:
            # Search for posts containing the query
            cursor.execute("SELECT * FROM posts WHERE title LIKE ? OR post LIKE ?",
                           ('%' + search_query + '%', '%' + search_query + '%'))
        else:
            # Get all posts from db
            cursor.execute('SELECT * FROM posts')

    data = cursor.fetchall()

    # Close db connection
    db.close()

    if not data and search_query:
        message = 'No results found for "{}"'.format(search_query)
    else:
        message = ''

    return render_template('blog.html', posts=data, search_query=search_query, message=message)


@app.route('/post/<_id>')
def post(_id):
    # Check if the user is logged in
    # if not session.get('logged_in'):
    #     return redirect('/login')
    # Connect to db
    db = sqlite3.connect('posts.db')  
    cursor = db.cursor()
    
    # Get data from db
    cursor.execute('SELECT * FROM posts WHERE id=%s' % _id)
    post = cursor.fetchone()
    
    # Close db connection
    db.close()
    return render_template('post.html', post=post)

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/editing')
def editing():
    # Check if the user is logged in
    if not session.get('logged_in'):
        return redirect('/login')
    # Get request args
    title = request.args.get('title')
    post = request.args.get('post')
    _id = request.args.get('_id')

    return render_template('editing.html', title=title, post=post, _id=_id)


@app.route('/inserting')
def inserting():
    # Check if the user is logged in
    if not session.get('logged_in'):
        return redirect('/login')
    # Connect to db
    db = sqlite3.connect('posts.db')  
    cursor = db.cursor()
    
    # Get request args
    title = request.args.get('title')
    post = request.args.get('post')
    
    # Insert data into db
    cursor.execute('INSERT INTO posts(title, post) VALUES("%s", "%s")' % (title, post.replace('"', "'")))
    db.commit()
    
    # Close db connection
    db.close()
    return redirect('/blog')

@app.route('/updating/<_id>')
def updating(_id):
    # Check if the user is logged in
    if not session.get('logged_in'):
        return redirect('/login')
    # Connect to db
    db = sqlite3.connect('posts.db')  
    cursor = db.cursor()
    
    # Get request args
    title = request.args.get('title')
    post = request.args.get('post')
    
    # Update data in db
    cursor.execute('UPDATE posts SET title="%s", post="%s" WHERE id=%s' % (title, post.replace('"', "'"), _id))
    db.commit()
    
    # Close db connection
    db.close()
    return redirect('/admin')

@app.route('/deleting/<_id>')
def deleting(_id):
    # Check if the user is logged in
    if not session.get('logged_in'):
        return redirect('/login')
    # Connect to db
    db = sqlite3.connect('posts.db')  
    cursor = db.cursor()
    
    # Update data in db
    cursor.execute('DELETE FROM posts WHERE id=%s' % _id)
    db.commit()
    
    # Close db connection
    db.close()
    return redirect('/admin')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('admin')
#         password = request.form.get('shixyman')

#         # Add your authentication logic here
#         # Check if the username and password are valid
#         # You can use a database or any other authentication mechanism

#         # If authentication is successful, set a session variable to mark the user as logged in
#         session['logged_in'] = True
        
#         return redirect('/admin')

#     return render_template('login.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Add your authentication logic here
        # Check if the username and password are valid
        if username == 'admin' and password == 'shixyman':
            # If the username and password are valid, set a session variable to mark the user as logged in
            session['logged_in'] = True
            return redirect('/admin')
        else:
            # If the username and password are invalid, display an error message
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/admin')
def admin():
    # Check if the user is logged in
    if not session.get('logged_in'):
        return redirect('/login')

    # Connect to db and fetch posts
    with sqlite3.connect('posts.db') as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM posts')
        data = cursor.fetchall()

    return render_template('admin.html', posts=data)

@app.route('/logout')
def logout():
    # Clear the session and log out the user
    session.clear()
    return redirect('/login')


@app.route('/generate_password', methods=['GET', 'POST'])
def generate_password():
    upperLetter = request.form.get('upper_letter')
    numbers = request.form.get('numbers')
    punctuation = request.form.get('punctuation')
    lenPasswrd = request.form.get('length')
    
    if lenPasswrd is None:
        return render_template('genpwd.html', error='Please enter a password length.')
        
    lenPasswrd = int(lenPasswrd)

    total = string.ascii_lowercase
    if upperLetter is None or upperLetter.lower() == "yes":
        total += string.ascii_uppercase
    if numbers is None or numbers.lower() == "yes":
        total += string.digits
    if punctuation is None or punctuation.lower() == "yes":
        total += string.punctuation

    password = "".join(random.sample(total, lenPasswrd))
    return render_template('genpwd.html', password=password)

@app.route('/dice')
def dice():
    return render_template("dice.html")

@app.route('/passwordJS')
def passwordJS():
    return render_template("passwordJS.html")
    
@app.route('/landing')
def landing():
    return redirect("https://usri-rshid.github.io/landing_page/")

@app.route('/dayNight')
def dayNight():
    return redirect("https://usri-rshid.github.io/day_light/")

@app.route('/portfolio0')
def portfolio0():
    return redirect("https://usri-rshid.github.io/portfolio/")

@app.route('/quotesApi')
def quotesApi():
    return redirect("https://usri-rshid.github.io/quotes_api/")

if __name__ == "__main__":
    db.create_all()
    # to add todo list for testing html
    #new_todo = Todo(title="todo 1",complete = False)
    #db.session.add(new_todo)
    #db.session.commit()
    
    app.run(debug=True)