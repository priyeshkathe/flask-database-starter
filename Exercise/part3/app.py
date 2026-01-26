# EXERCISE:
# 1. Add a `Teacher` model with a relationship to Course 
# (have one Course can be taught by many Teachers and one Teacher can only teach only one Course)
# In other words, create new Teacher model exactly like Student with all others things same 
# (relationship between the two, frontend page for teacher list, add new teacher, backend routes for add new teacher, edit teacher, delete teacher)
# Additional exercise - display list of students with course name and teacher name (taken from the course name) and vice versa

# 2. Try different query methods: `filter()`, `order_by()`, `limit()`

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your-secret-key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

db = SQLAlchemy(app)  


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    students = db.relationship('Student', backref='course', lazy=True)
    teachers = db.relationship('Teacher', backref='course', lazy=True)


    def __repr__(self):
        return f'<Course {self.name}>'



class Student(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) 
    
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f'<Teacher {self.name}>'



@app.route('/')
def index():
    students = Student.query.all()  
    return render_template('index.html', students=students)


@app.route('/courses')
def courses():
    all_courses = Course.query.all()  
    return render_template('courses.html', courses=all_courses)


@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course_id = request.form['course_id']

        new_student = Student(name=name, email=email, course_id=course_id)  
        db.session.add(new_student)  
        db.session.commit() 

        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))

    courses = Course.query.all()  
    return render_template('add.html', courses=courses)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    
    student = Student.query.get_or_404(id)  
    if request.method == 'POST':
        student.name = request.form['name']  
        student.email = request.form['email']
        student.course_id = request.form['course_id']

        db.session.commit()  
        flash('Student updated!', 'success')
        return redirect(url_for('index'))

    courses = Course.query.all()
    return render_template('edit.html', student=student, courses=courses)


@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)  
    db.session.commit()

    flash('Student deleted!', 'danger')
    return redirect(url_for('index'))


@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')  

        new_course = Course(name=name, description=description)
        db.session.add(new_course)
        db.session.commit()

        flash('Course added!', 'success')
        return redirect(url_for('courses'))

    return render_template('add_course.html')

@app.route('/teachers')
def teachers():
    teachers = Teacher.query.all()
    return render_template('teachers.html', teachers=teachers)


@app.route('/add-teacher', methods=['GET', 'POST'])
def add_teacher():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course_id = request.form['course_id']

        teacher = Teacher(name=name, email=email, course_id=course_id)
        db.session.add(teacher)
        db.session.commit()

        flash('Teacher added successfully!', 'success')
        return redirect(url_for('teachers'))

    courses = Course.query.all()
    return render_template('add_teacher.html', courses=courses)


@app.route('/edit-teacher/<int:id>', methods=['GET', 'POST'])
def edit_teacher(id):
    teacher = Teacher.query.get_or_404(id)

    if request.method == 'POST':
        teacher.name = request.form['name']
        teacher.email = request.form['email']
        teacher.course_id = request.form['course_id']

        db.session.commit()
        flash('Teacher updated!', 'success')
        return redirect(url_for('teachers'))

    courses = Course.query.all()
    return render_template('edit_teacher.html', teacher=teacher, courses=courses)


@app.route('/delete-teacher/<int:id>')
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()

    flash('Teacher deleted!', 'danger')
    return redirect(url_for('teachers'))

@app.route('/students/sort/name')
def students_sort_name():
    students = Student.query.order_by(Student.name.asc()).all()
    return render_template('index.html', students=students)

@app.route('/students/latest')
def latest_students():
    students = Student.query.order_by(Student.id.desc()).limit(5).all()
    return render_template('index.html', students=students)

@app.route('/students/course/<course_name>')
def students_by_course(course_name):
    students = Student.query.filter(
        Student.course.has(name=course_name)
    ).all()
    return render_template('index.html', students=students)

@app.route('/teachers/sort/name')
def teachers_sort_name():
    teachers = Teacher.query.order_by(Teacher.name.asc()).all()
    return render_template('teachers.html', teachers=teachers)

@app.route('/teachers/latest')
def latest_teachers():
    teachers = Teacher.query.order_by(Teacher.id.desc()).limit(3).all()
    return render_template('teachers.html', teachers=teachers)

@app.route('/teachers/course/<course_name>')
def teachers_by_course(course_name):
    teachers = Teacher.query.filter(
        Teacher.course.has(name=course_name)
    ).all()
    return render_template('teachers.html', teachers=teachers)




def init_db():
    """Create tables and add sample courses if empty"""
    with app.app_context():
        db.create_all()  

       
        if Course.query.count() == 0:
            sample_courses = [
                Course(name='Python Basics', description='Learn Python programming fundamentals'),
                Course(name='Web Development', description='HTML, CSS, JavaScript and Flask'),
                Course(name='Data Science', description='Data analysis with Python'),
            ]
            db.session.add_all(sample_courses)  
            db.session.commit()
            print('Sample courses added!')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
