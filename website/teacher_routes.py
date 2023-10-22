from flask import Blueprint,request,render_template,redirect,url_for,flash
from .models import Student,Class,Attendance,Assignment,Assessment,Question,AnswerChoice,AssessmentResult,Period
from . import db, mail, app
from flask_login import login_required,current_user
from datetime import date,datetime,timedelta
import re
from flask_mail import Message


teacher_routes = Blueprint('teacher_routes',__name__)

@teacher_routes.route('/homepage_teacher')
def homepage_teacher():
   teacher_id = current_user.id
   periods = Period.query.filter_by(teacher_id = teacher_id).all()
   return render_template('homepage_teacher.html', periods = periods)


@teacher_routes.route('/attendance',methods = ['POST'])
@login_required
def take_attendance():
   class_id  = request.form.get('class_id')
   return redirect(url_for('teacher_routes.attendance_list',class_id = class_id))

@teacher_routes.route('/attendance_list',methods = ['GET'])
@login_required
def attendance_list():
   class_id = request.args.get('class_id')
   period_number = request.args.get('period_number')


   students = Student.query.filter_by(class_id = class_id).all()
   
   is_period = Period.query.filter(Period.class_id == Period.class_id, Period.period_number == Period.period_number).first()
   if not is_period:
       flash("Period is not present with that period number", category='error')
       return redirect(url_for('teacher_routes.homepage_teacher'))


   today_date = date.today()

   yesterday_date = today_date-timedelta(days=1)
   before_yesterday_date = today_date-timedelta(days=2)
   two_days_ago_date = today_date-timedelta(days=3)
   
   
   attendance_already_submitted = Attendance.query.filter(Attendance.date == today_date, Attendance.class_id == class_id, Attendance.period_number == period_number).count()
   if attendance_already_submitted:
      flash("Attendance is Already Submitted",category='error')
      return redirect(url_for('teacher_routes.homepage_teacher'))

   yesterday_attendance_report = Attendance.query.filter(Attendance.date == yesterday_date, Attendance.class_id == class_id, Attendance.period_number == period_number).all()

   before_yesterday_attendance_report = Attendance.query.filter(Attendance.date == before_yesterday_date, Attendance.class_id == class_id, Attendance.period_number == period_number).all()

   two_days_ago_attendance_report = Attendance.query.filter(Attendance.date == two_days_ago_date, Attendance.class_id == class_id, Attendance.period_number == period_number).all()

   if students:
      return render_template('attendance_list.html',yesterday_attendance_report = yesterday_attendance_report,
                             before_yesterday_attendance_report = before_yesterday_attendance_report,
                             two_days_ago_attendance_report = two_days_ago_attendance_report,
                            students = students, class_id = class_id, date =today_date, period_number = period_number)
   else:
      flash(message=f'no class found with that class id {class_id} in attendance register.',category='error')
      return redirect(url_for('teacher_routes.homepage_teacher'))
   
   
@teacher_routes.route('/submit_attendance', methods = ['POST'])
@login_required
def submit_attendance():
   class_id = request.form.get('class_id')
   period_number = request.form.get('period_number')


   today_date = date.today()
   
   for key, value in request.form.items():
      if key.startswith('attendance_status'):
         student_id = key.split('_')[2]
         attendance_status = value

         attendance = Attendance(student_id = student_id, class_id = class_id, date = today_date, 
                                 attendance_status = attendance_status,
                                 period_number = period_number)

         db.session.add(attendance)
         db.session.commit()
   flash("Attendance Submitted!",category='success')
   return redirect(url_for('teacher_routes.homepage_teacher'))


@teacher_routes.route('/add_assignment', methods=['GET', 'POST'])
@login_required
def add_assignment():
    if request.method == 'GET':
        return render_template('add_assignment.html')
    else:
        name = request.form.get('name')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        class_id = request.form.get('class_id')
        class_with_id = Class.query.filter_by(id=class_id).first()

        try:
            # Check if assignment name contains only alphanumeric characters and backslashes
            if not re.match(r'^[a-zA-Z0-9\s\\]+$', name):
               flash("Assignment name should only contain letters, numbers, spaces, and backslashes.", category='error')
               return redirect(url_for('teacher_routes.add_assignment'))

            if not class_with_id:
                flash("No class is found with the given id, please enter a valid class id.", category='error')
                return redirect(url_for('teacher_routes.add_assignment'))

            new_assignment = Assignment(name=name, description=description, due_date=due_date, class_id=class_id)

            db.session.add(new_assignment)
            db.session.commit()
            flash("Assignment added successfully.", category='success')
            return redirect(url_for('teacher_routes.add_assignment'))

        except ValueError:
            flash("Invalid date format. Please enter the date as YYYY-MM-DD.", category='error')
            return redirect(url_for('teacher_routes.add_assignment'))
        

def get_student_report(student_id,in_month):
   parsed_date = datetime.strptime(in_month, '%Y-%m')
   attendance_count = Attendance.query.filter(Attendance.student_id == student_id,
                                                  db.func.year(Attendance.date) == parsed_date.year,
                                                 db.func.month(Attendance.date) == parsed_date.month,
                                                  Attendance.attendance_status == 'Present').count()
   if not attendance_count:
              flash(" Given month is not present in database,please enter valid inputs",category='error')
              return render_template('send_reports.html')
         
   total_days = Attendance.query.filter(Attendance.student_id == student_id, 
                                           db.func.year(Attendance.date) == parsed_date.year,
                                           db.func.month(Attendance.date) == parsed_date.month).count()
   attendance_percentage = (attendance_count/total_days) * 100
   rounded_percentage = round(attendance_percentage, 2)
         
   return rounded_percentage,attendance_count,total_days


@teacher_routes.route('/send_reports', methods = ['GET', 'POST'])
def send_report():
   if request.method == 'GET':
      return render_template('send_reports.html')
   else:
      class_id = request.form.get('class_id')
      in_month = request.form.get('in_month')

      class_exists = Class.query.get(class_id)

      try:
         if not class_exists:
             flash('Class doent exists with given class id, please enter valid class id.',category='error')
             return redirect(url_for('teacher_routes.send_report'))
         
         students = Student.query.filter_by(class_id = class_id).all()
         for student in students:
            student_id = student.id
            parent_email = student.parent_email
             
            rounded_percentage,attendance_count,total_days = get_student_report(student_id,in_month)
            absent_days = total_days - attendance_count
            message = Message('Monthly Attendance Report',
                          recipients=[parent_email],
                          sender= app.config['MAIL_DEFAULT_SENDER'])
            message.body = f"""Dear Parent,
             This is an attendance report for your son, {student.full_name}, for the month of {in_month}:
             
             - Total days: {total_days}
             - Attended days: {attendance_count}
             - Absent days: {absent_days} days
             - Attendance percentage: {rounded_percentage}%
             
             If you have any questions or concerns, please don't hesitate to reach out.

             Best regards,
             Mother Lap English Medium School,
             Thimmanayunipeta
             contact: +919494341027 """
            
            mail.send(message)
            flash('Reports Successfully sent', category='success')
         return redirect(url_for('teacher_routes.send_report'))
      except ValueError:
            flash("Invalid date format. Please enter the date format as shown in date filed.", category='error')
            return redirect(url_for('teacher_routes.send_report'))
      
@teacher_routes.route('/create_assessment', methods=['GET', 'POST'])
def create_assessment():
    if request.method == 'GET':
        return render_template('create_assessment.html')
    else:
        try:
            assessment_name = request.form.get('assessment_name')
            teacher_id = request.form.get('teacher_id')
            class_id = request.form.get('class_id')

            new_assessment = Assessment(assessment_name=assessment_name, teacher_id=teacher_id, class_id=class_id, date_created=date.today())

            db.session.add(new_assessment)
            db.session.commit()

            assessment = Assessment.query.filter_by(assessment_name = assessment_name).first()

            flash(f"Assessment Added, Id is {assessment.assessment_id}, Add Questions here.", category='success')
            return redirect(url_for('teacher_routes.add_question'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", category='error')
            return redirect(url_for('teacher_routes.create_assessment'))


@teacher_routes.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'GET':
        return render_template('add_question.html')
    else:
        try:
            assessment_id = request.form.get('assessment_id')
            question_text = request.form.get('question_text')
            question_id = request.form.get('question_id')
            choice_text = request.form.get('choice_text')
            is_correct_str = request.form.get('is_correct')  # Get the string value

            # Convert the string to a boolean (case-insensitive check for 'true')
            if is_correct_str:
                is_correct = is_correct_str.lower() == 'true'

            if question_text:
                new_question = Question(assessment_id=assessment_id, question_text=question_text, date_created=date.today())
                db.session.add(new_question)
                db.session.commit()

                question = Question.query.filter_by(question_text = question_text).first()
                
                flash(f"Question Added,question id is{question.question_id}, belongs to assessment with id {question.assessment_id}", category='success')
                return redirect(url_for('teacher_routes.add_question'))

            if choice_text:
                new_choice = AnswerChoice(question_id=question_id, choice_text=choice_text, is_correct=is_correct)
                db.session.add(new_choice)
                db.session.commit()

                choice = AnswerChoice.query.filter_by(choice_text = choice_text).first()

                question = Question.query.filter_by(question_id = choice.question_id).first()

                flash(f"choice id is {choice.choice_id}, Added for question with id {choice.question_id}, belongs to assessment with id {question.assessment_id}", category='success')

                return redirect(url_for('teacher_routes.add_question'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", category='error')
            return redirect(url_for('teacher_routes.add_question'))
        

def get_assessment(assessment_id, class_id):
    assessment = Assessment.query.filter_by(assessment_id=assessment_id, class_id=class_id).first()
    
    return assessment

def get_assessment_result(assessment_id, student_id):
    assessment_result = AssessmentResult.query.filter_by(assessment_id=assessment_id, student_id=student_id).first()

    return assessment_result


@teacher_routes.route('/send_assessment_reports', methods = ['GET', 'POST'])
def send_assessment_reports():
   if request.method == 'GET':
      return render_template('send_assessment_reports.html')
   else:
      class_id = request.form.get('class_id')
      assessment_id = request.form.get('assessment_id')

      class_exists = Class.query.get(class_id)

      try:
         if not class_exists:
             flash('Class doent exists with given class id, please enter valid class id.',category='error')
             return redirect(url_for('teacher_routes.send_assessment_reports'))
         
         students = Student.query.filter_by(class_id = class_id).all()
         assessment = get_assessment(assessment_id,class_id)

         if not assessment:
             flash('Assessment doent exists with given id, please enter valid assessment id.',category='error')
             return redirect(url_for('teacher_routes.send_assessment_reports'))
         
         for student in students:
            student_id = student.id
            parent_email = student.parent_email
             
            assessment_result = get_assessment_result(assessment_id,student_id)
            
            message = Message('Assessment Report',
                          recipients=[parent_email],
                          sender= app.config['MAIL_DEFAULT_SENDER'])
            
            message.body = f"""Dear Parent,
             This is an assessment report for your son, {student.full_name}, for the {assessment.assessment_name} assessment:
             
             - Assessment Id: {assessment_result.assessment_id}
             - Obtained Marks: {assessment_result.obtained_marks} marks
             - Marks percentage: {assessment_result.percentage}%
             
             If you have any questions or concerns, please don't hesitate to reach out.

             Best regards,
             Mother Lap English Medium School,
             Thimmanayunipeta
             contact: +919494341027 """
            
            mail.send(message)
            flash('Reports Successfully sent', category='success')
         return redirect(url_for('teacher_routes.send_assessment_reports'))
      except ValueError:
            flash("Invalid input. Please enter valid input.", category='error')
            return redirect(url_for('teacher_routes.send_assessment_report'))