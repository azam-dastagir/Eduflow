from . import db
from flask_login import UserMixin



class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete='CASCADE'))
    parent_email = db.Column(db.String(150), nullable = False)
    roll_number = db.Column(db.Integer)


    def get_id(self):
        return f"student-{self.id}"
    
    def get_role(self):
        return "student"
    
    def to_dict(self):
        student_as_dict = {
            'Full Name':self.full_name,
            'email':self.email,
            'class_id':self.class_id
        }
        return student_as_dict

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete='CASCADE'))
    date = db.Column(db.Date, nullable=False)  
    attendance_status = db.Column(db.String(10))
    period_number = db.Column(db.Integer)

    # Indexes for relevant columns
    __table_args__ = (
        db.Index('idx_student_id_date', 'student_id', 'date'),
        db.Index('idx_class_id_date', 'class_id', 'date')
    )

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), nullable = False)
    description = db.Column(db.Text, nullable = False)
    due_date = db.Column(db.DateTime, nullable = False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete = 'CASCADE'))

class Administrator(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique = True)
    password = db.Column(db.String(300))

    def get_id(self):
        return f"admin-{self.id}"
    
    def get_role(self):
        return "admin"


class Assessment(db.Model):
    assessment_id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, nullable=False)
    class_id = db.Column(db.Integer, nullable=False)
    assessment_name = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.Date, nullable=False)

    # One-to-Many relationship with Question
    questions = db.relationship('Question', backref='assessment', lazy=True)

class Question(db.Model):
    question_id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.assessment_id'), nullable=False)  # Update the ForeignKey
    question_text = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.Date, nullable=False)

    # One-to-Many relationship with AnswerChoice
    answer_choices = db.relationship('AnswerChoice', backref='question', lazy=True)

class AnswerChoice(db.Model):

    __tablename__ = 'answerchoice' 
    
    choice_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.question_id'), nullable=False)  # Update the ForeignKey
    choice_text = db.Column(db.String(255), nullable=False, unique = True)
    is_correct = db.Column(db.Boolean, nullable=False)

class AssessmentResult(db.Model):
    result_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.assessment_id'), nullable=False)
    obtained_marks = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)



class Period(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    period_number = db.Column(db.Integer, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    

    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    subject = db.relationship('Subject', backref='periods', lazy=True)
    teacher = db.relationship('Teacher', backref='periods', lazy=True)
    period_class = db.relationship('Class', backref ='periods', lazy=True)


teacher_class_association = db.Table(
    'teacher_class_association',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id')),
    db.Column('class_id', db.Integer, db.ForeignKey('class.id'))
)

teacher_subject_association = db.Table(
    'teacher_subject_association',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id')),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.subject_id'))
)

class Teacher(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    subjects_taught = db.relationship('Subject', backref='teacher', lazy=True)
    classes_taught = db.relationship('Class', backref='class_teacher', lazy=True)

    classes_taught = db.relationship('Class', secondary=teacher_class_association, back_populates='teachers')

    subjects_taught = db.relationship('Subject', secondary=teacher_subject_association, back_populates='teachers')

    def get_id(self):
        return f"teacher-{self.id}"
    
    def get_role(self):
        return "teacher"

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    start_date = db.Column(db.Date, nullable = False)
    end_date = db.Column(db.Date, nullable = False)

    teachers = db.relationship('Teacher', secondary=teacher_class_association, back_populates='classes_taught')

class Subject(db.Model):
    subject_id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(255), nullable=False, unique=True)

    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))

    teachers = db.relationship('Teacher', secondary=teacher_subject_association, back_populates='subjects_taught')


