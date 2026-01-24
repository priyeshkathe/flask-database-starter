# =============================================================================
# EXERCISE:
# =============================================================================
#
# Try modifying `add_sample_student()` to add different students with
# different names!
#
# =============================================================================

from flask import Flask, render_template
import sqlite3  

app = Flask(__name__)

DATABASE = 'students.db' 

def get_db_connection():
    conn = sqlite3.connect(DATABASE)  
    conn.row_factory = sqlite3.Row  
    return conn


def init_db():
    """Create the table if it doesn't exist"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL
        )
    ''')  
    conn.commit()  
    conn.close() 



@app.route('/')
def index():
    conn = get_db_connection()  
    students = conn.execute('SELECT * FROM students').fetchall()  
    conn.close()  
    return render_template('index.html', students=students)


@app.route('/add')
def add_sample_student():
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO students (name, email, course) VALUES (?, ?, ?)',
        ('Priyesh kathe', 'priyeshkathe@gmail.com', 'Java')
    )
    conn.commit()  
    conn.close()
    return 'Student added! <a href="/">Go back to home</a>'


if __name__ == '__main__':
    init_db()  
    app.run(debug=True)




