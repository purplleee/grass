from flask import Flask, render_template, request, url_for, flash, redirect
from forms import CourseForm
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = '1fd34bf367245d1c60c08a5325a2dc72235390ee0a685cf9'

# Function to create a new MySQL connection
def get_db_connection():
    mysql_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'comment'
    }
    return mysql.connector.connect(**mysql_config)

@app.route('/', methods=('GET', 'POST'))
def index():
    form = CourseForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            dictionary=True
            cursor.execute('''INSERT INTO courses (title, description, price, available, level) 
                              VALUES (%s, %s, %s, %s, %s)''',
                           (form.title.data, form.description.data, form.price.data, 
                            form.available.data, form.level.data))
            conn.commit()
            flash('Course created successfully!', 'success')
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash('Failed to create course.', 'error')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('courses'))
    return render_template('index.html', form=form)

@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!', 'error')
        elif not content:
            flash('Content is required!', 'error')
        else:
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO info_table (title, content) VALUES (%s, %s)''', (title, content))
                conn.commit()
                flash('Message created successfully!', 'success')
            except mysql.connector.Error as err:
                print(f"Error: {err}")
                flash('Failed to create message.', 'error')
            finally:
                cursor.close()
                conn.close()
            return redirect(url_for('index'))
    return render_template('create.html')




@app.route('/courses/')
def courses():
    conn = get_db_connection()
    courses_list = []
    try:
        cursor = conn.cursor(dictionary=True)  # Ensure cursor returns dictionaries
        cursor.execute("SELECT * FROM courses")
        courses_list = cursor.fetchall()
        app.logger.info(f"Fetched courses: {courses_list}")  # Log the fetched data
    except mysql.connector.Error as err:
        app.logger.error(f"Failed to fetch courses: {err}")
        flash(f"Error fetching courses: {err}", 'error')
    finally:
        cursor.close()
        conn.close()
    return render_template('courses.html', courses_list=courses_list)
