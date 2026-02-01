
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'  # Database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable warning

db = SQLAlchemy(app)  # Initialize SQLAlchemy with app


# =============================================================================
# MODELS (Python Classes = Database Tables)
# =============================================================================

class Course(db.Model):  # Course table
    id = db.Column(db.Integer, primary_key=True)  # Auto-increment ID
    name = db.Column(db.String(100), nullable=False)  # Course name
    description = db.Column(db.Text)  # Optional description

    # Relationship: One Course has Many Students
    students = db.relationship('Student', backref='course', lazy=True)

    def __repr__(self):  # How to display this object
        return f'<Course {self.name}>'


class Student(db.Model):  # Student table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # unique=True means no duplicates

    # Foreign Key: Links student to a course
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'


# =============================================================================
# ROUTES - Using ORM instead of raw SQL
# =============================================================================

@app.route('/')
def index():
    # OLD WAY (raw SQL): conn.execute('SELECT * FROM students').fetchall()
    # NEW WAY (ORM):
    students = Student.query.all()  # Get all students
    return render_template('index.html', students=students)


@app.route('/courses')
def courses():
    all_courses = Course.query.all()  # Get all courses
    return render_template('courses.html', courses=all_courses)


@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course_id = request.form['course_id']

        # OLD WAY: conn.execute('INSERT INTO students...')
        # NEW WAY:
        new_student = Student(name=name, email=email, course_id=course_id)  # Create object
        db.session.add(new_student)  # Add to session
        db.session.commit()  # Save to database

        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))

    courses = Course.query.all()  # Get courses for dropdown
    return render_template('add.html', courses=courses)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    # OLD WAY: conn.execute('SELECT * FROM students WHERE id = ?', (id,))
    # NEW WAY:
    student = Student.query.get_or_404(id)  # Get by ID or show 404 error

    if request.method == 'POST':
        student.name = request.form['name']  # Just update the object
        student.email = request.form['email']
        student.course_id = request.form['course_id']

        db.session.commit()  # Save changes
        flash('Student updated!', 'success')
        return redirect(url_for('index'))

    courses = Course.query.all()
    return render_template('edit.html', student=student, courses=courses)


@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)  # Delete the object
    db.session.commit()

    flash('Student deleted!', 'danger')
    return redirect(url_for('index'))


@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')  # Optional field

        new_course = Course(name=name, description=description)
        db.session.add(new_course)
        db.session.commit()

        flash('Course added!', 'success')
        return redirect(url_for('courses'))

    return render_template('add_course.html')


# =============================================================================
# CREATE TABLES AND ADD SAMPLE DATA
# =============================================================================

def init_db():
    """Create tables and add sample courses if empty"""
    with app.app_context():
        db.create_all()  # Create all tables based on models

        # Add sample courses if none exist
        if Course.query.count() == 0:
            sample_courses = [
                Course(name='Python Basics', description='Learn Python programming fundamentals'),
                Course(name='Web Development', description='HTML, CSS, JavaScript and Flask'),
                Course(name='Data Science', description='Data analysis with Python'),
            ]
            db.session.add_all(sample_courses)  # Add multiple at once
            db.session.commit()
            print('Sample courses added!')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
