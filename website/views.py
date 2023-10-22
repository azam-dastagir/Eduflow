from flask import Blueprint,request,render_template,jsonify,redirect,url_for,flash
from .models import Student,Class,Attendance,Assignment,Teacher,Period,Subject
from . import db
from flask_login import login_required,current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
import re


views = Blueprint('views', __name__)

@views.route('/home', methods = ['GET'])
def home():
   role = request.args.get('role')
   if role == 'Teacher':
      return redirect(url_for('teacher_routes.homepage_teacher'))
   if role == 'Student':
      return render_template('homepage_student.html')
   if role == 'Admin':
      return render_template('homepage_admin.html')

@views.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'GET':
        id_with_role = current_user.get_id()
        role, id = id_with_role.split('-')
        return render_template('add_student.html', role = role)
    
    else:
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        class_id = request.form.get('class_id')
        parent_email = request.form.get('parent_email')
        
        class_with_id = Class.query.filter_by(id=class_id).first()

        id_with_role = current_user.get_id()
        role, id = id_with_role.split('-')

        try:
            # Check student name length and validity
            if len(full_name) < 3:
                flash("Student name must be at least 3 characters long.", category='error')
                return redirect(url_for('views.add_student', role = role))
            if not re.match(r'^[a-zA-Z ]+$', full_name):
                flash("Student name should only contain letters and spaces.", category='error')
                return redirect(url_for('views.add_student', role = role))

            # Check password length
            if len(password) < 6:
                flash("Password must be at least 6 characters long.", category='error')
                return redirect(url_for('views.add_student', role = role))

            if not class_with_id:
                flash("No class is found with the given id, please enter a valid class id.", category='error')
                return redirect(url_for('views.add_student', role = role))

            new_student = Student(full_name=full_name, email=email, password=generate_password_hash(password),
                                  class_id=class_id, parent_email = parent_email)
            
            db.session.add(new_student)
            db.session.commit()
            flash("Student added successfully.", category='success')
            return redirect(url_for('views.add_student', role = role))
        
        except Exception as e:
            flash(f"An error occurred while adding the student: {str(e)}", category='error')
            return redirect(url_for('views.add_student', role = role))


@views.route('/calculate_attendance',methods = ['GET'])
@login_required
def calculate_attendance():
   if request.method == 'GET':
      id_with_role = current_user.get_id()
      role, id = id_with_role.split("-")
      return render_template('calculate_attendance.html', role = role)

@views.route('/get_per_day_attendance',methods = ['POST'])
@login_required
def get_per_day_attendance():
      class_id = request.form.get('class_id_form3')
      exact_date = request.form.get('exact_date_form3')

      return redirect(url_for('views.view_attendance', class_id = class_id, exact_date = exact_date))
                      

@views.route('/get_monthly_attendance', methods = ['POST'])
@login_required
def get_monthly_attendance():
      student_id = request.form.get('student_id_form2')
      class_id = request.form.get('class_id_form4')
      in_month = request.form.get('in_month_form4')

      if student_id:
         in_month = request.form.get('in_month_form2')
         return redirect(url_for('views.view_attendance',in_month = in_month,student_id = student_id))

      if class_id:
         
         return redirect(url_for('views.view_attendance',in_month = in_month,class_id = class_id))


@views.route('/get_attendance_in_between_dates', methods = ['POST'])
@login_required
def get_attendance_in_between_dates():
      student_id = request.form.get('student_id_form1')
      class_id = request.form.get('class_id_form1')
      from_date = request.form.get('from_date_form1')
      to_date = request.form.get('to_date_form1')
      
      
      if student_id and from_date:
         return redirect(url_for('views.view_attendance',from_date = from_date,to_date = to_date,
                                 student_id = student_id))
      
      elif class_id and from_date:
         return redirect(url_for('views.view_attendance',from_date = from_date,to_date = to_date, class_id = class_id))


@views.route('/view_attendance',methods = ['GET'])
@login_required
def view_attendance():
   class_id = request.args.get('class_id')
   exact_date = request.args.get('exact_date')

   student_id = request.args.get('student_id')
   class_id = request.args.get('class_id')
   in_month = request.args.get('in_month')

   from_date = request.args.get('from_date')
   to_date = request.args.get('to_date')

   id_with_role = current_user.get_id()
   role, id = id_with_role.split('-')

   try:
      if class_id:
         class_exits = Class.query.filter_by(id = class_id).first()

         if not class_exits:
            flash('Class does not exist, Please enter a valid class id.')
            return render_template('calculate_attendance.html',role = role)
      
      elif student_id:
         student_exists = Student.query.filter_by(id = student_id).first()
         if not student_exists:
            flash('student does not exist, Please enter a valid student id.')
            return render_template('calculate_attendance.html',role = role)
         
      if class_id and exact_date:

         parsed_date = datetime.strptime(exact_date, "%Y-%m-%d")
         attendance_count = Attendance.query.filter_by(class_id = class_id, date = parsed_date, attendance_status = 'Present').count()

         if not attendance_count:
              flash("Given date is not present in database, please enter valid inputs",category='error')
              return render_template('calculate_attendance.html',role = role)
         
         total_students_in_class = Student.query.filter_by(class_id = class_id).count()
         class_attendance_percentage = (attendance_count/total_students_in_class)*100
         num_of_students_absent = int(total_students_in_class) - int(attendance_count)
         rounded_percentage = round(class_attendance_percentage, 2)


         return render_template('view_attendance.html',class_attendance_percentage = rounded_percentage,
                              total_students_in_class = total_students_in_class,
                              attendance_count = attendance_count,class_id = class_id,
                               num_of_students_absent = num_of_students_absent,role = role)
      
      elif student_id and in_month:
         parsed_date = datetime.strptime(in_month, '%Y-%m')
         attendance_count = Attendance.query.filter(Attendance.student_id == student_id,
                                                  db.func.year(Attendance.date) == parsed_date.year,
                                                 db.func.month(Attendance.date) == parsed_date.month,
                                                  Attendance.attendance_status == 'Present'
                                                  ).count()
         if not attendance_count:
              flash(" Given month is not present in database,please enter valid inputs",category='error')
              return render_template('calculate_attendance.html',role = role)
         
         total_days = Attendance.query.filter(Attendance.student_id == student_id, 
                                           db.func.year(Attendance.date) == parsed_date.year,
                                           db.func.month(Attendance.date) == parsed_date.month).count()
         attendance_percentage = (attendance_count/total_days) * 100
         rounded_percentage = round(attendance_percentage, 2)
         
         return render_template('view_attendance.html',attendance_percentage = rounded_percentage,
                              attendance_count = attendance_count,class_id = class_id,student_id = student_id,
                              in_month = in_month,total_days = total_days, role = role)
      
      elif class_id and in_month:
         parsed_date = datetime.strptime(in_month, '%Y-%m')
         attendance_count = Attendance.query.filter(Attendance.class_id == class_id, db.func.year(Attendance.date) == parsed_date.year,
                                                 db.func.month(Attendance.date) == parsed_date.month,
                                                  Attendance.attendance_status == 'Present' ).count()
         
         if not attendance_count:
              flash("Given month is not present in database,please enter valid inputs",category='error')
              return render_template('calculate_attendance.html',role = role)
         
         total_days = Attendance.query.filter(Attendance.class_id == class_id, 
                                              db.func.year(Attendance.date) == parsed_date.year,
                                           db.func.month(Attendance.date) == parsed_date.month).count()
         attendance_percentage = (attendance_count/total_days) *100
         rounded_percentage = round(attendance_percentage, 2)

         return render_template('view_attendance.html',attendance_percentage = rounded_percentage,
                              attendance_count = attendance_count,class_id = class_id,
                              in_month = in_month,total_days = total_days, role = role)
      
      elif class_id and from_date:
         parsed_from_date = datetime.strptime(from_date, "%Y-%m-%d")
         parsed_to_date = datetime.strptime(to_date, "%Y-%m-%d")

         class_exists = Class.query.filter_by(id = class_id).first()
         if not class_exists:
             flash("class does not exists with given class id,please enter valid class Id",category='error')
             return render_template('calculate_attendance.html',role = role)
             
         if class_exists:
            class_start_date = class_exists.start_date
         if parsed_from_date < class_start_date:
             flash("Given from date is less than class start date,please enter valid date inputs",category='error')
             return render_template('calculate_attendance.html',role = role)


         #for handling inavlid from and to date inputs
         if parsed_from_date>parsed_to_date:
            flash("'from date' is gtreater than 'to date',please enter valid inputs",category='error')
            return render_template('calculate_attendance.html',role = role)
         
         if parsed_to_date>datetime.now():
            flash("'to date' is greater than 'current date&time',please enter valid inputs",category='error')
            return render_template('calculate_attendance.html',role = role)


         attendance_count = Attendance.query.filter(Attendance.class_id == class_id, 
                                                 Attendance.date.between(parsed_from_date, 
                                                                          parsed_to_date,),
                                              Attendance.attendance_status == 'Present').count()
         
         if not attendance_count:
              flash(" Given 'from date' and 'to date' are not present in database,please enter valid inputs",category='error')
              return render_template('calculate_attendance.html',role = role)
         
         total_days = Attendance.query.filter(Attendance.class_id == class_id, 
                                                 Attendance.date.between(parsed_from_date, 
                                                                          parsed_to_date)).count()
         
         attendance_percentage = (attendance_count/total_days) * 100
         rounded_percentage = round(attendance_percentage, 2)

         return render_template('view_attendance.html',attendance_percentage = rounded_percentage,
                              attendance_count = attendance_count,class_id = class_id,
                              to_date = to_date, from_date = from_date, role = role)
      
      elif student_id and from_date:
         parsed_from_date = datetime.strptime(from_date, "%Y-%m-%d")
         parsed_to_date = datetime.strptime(to_date, "%Y-%m-%d")

         student_exists = Student.query.filter_by(id = student_id).first()
         if not student_exists:
             flash("student does not exists with given student id,please enter valid student Id",category='error')
             return render_template('calculate_attendance.html',role = role)
             
         if student_exists:
            class_id = student_exists.class_id
            class_exists = Class.query.filter_by(id = class_id).first()

            if not class_exists:
                flash("student class doesnt exist,error in student data,please enter valid date inputs",category='error')
                return render_template('calculate_attendance.html',role = role)
            if class_exists:
               class_start_date = class_exists.start_date
               if parsed_from_date.date() < class_start_date:
                   flash("Given from date is less than class start date,please enter valid date inputs",category='error')
                   return render_template('calculate_attendance.html',role = role)


         #for handling inavlid from and to date inputs
         if parsed_from_date>parsed_to_date:
            flash("'from date' is gtreater than 'to date',please enter valid inputs",category='error')
            return render_template('calculate_attendance.html',role = role)
         
         if parsed_to_date>datetime.now():
            flash("'to date' is greater than 'current date&time',please enter valid inputs",category='error')
            return render_template('calculate_attendance.html',role = role)


         attendance_count = Attendance.query.filter(Attendance.student_id == student_id, 
                                                 Attendance.date.between(parsed_from_date, 
                                                                          parsed_to_date,),
                                              Attendance.attendance_status == 'Present').count()
         if not attendance_count:
              flash(" Given 'from date' and 'to date' are not present in database,please enter valid inputs",category='error')
              return render_template('calculate_attendance.html',role = role)
             
         total_days = Attendance.query.filter(Attendance.student_id == student_id, 
                                                 Attendance.date.between(parsed_from_date, 
                                                                          parsed_to_date)).count()
         
         attendance_percentage = (attendance_count/total_days) * 100
         rounded_percentage = round(attendance_percentage, 2)

         return render_template('view_attendance.html',attendance_percentage = rounded_percentage,
                              attendance_count = attendance_count,class_id = class_id,student_id = student_id,
                              to_date = to_date, from_date = from_date,total_days = total_days,role = role)

   except ValueError as e:
      flash("Invalid Date format, please enter in the format shown in place holder.", category='error')
      return render_template('calculate_attendance.html',role = role)

 


