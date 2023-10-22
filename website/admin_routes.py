from flask import Blueprint,request,render_template,redirect,url_for,flash
from .models import Class,Teacher,Subject,Period
from . import db
from flask_login import login_required
from werkzeug.security import generate_password_hash
from datetime import date
import re  



admin_routes = Blueprint('admin_routes', __name__)


@admin_routes.route('/homepage_admin')
def homepage_admin():
   return render_template('homepage_admin.html')

@admin_routes.route('/view_teachers',methods = ['GET'])
@login_required
def view_teachers():
    teachers = Teacher.query.all()
    periods = Period.query.all()
    subjects = Subject.query.all()
    return render_template('teachers_list.html', teachers = teachers, 
                           date = date.today(), periods = periods,
                           subjects = subjects)


@admin_routes.route('/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    if request.method == 'GET':
        return render_template('add_teacher.html')
    else:
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        cnfm_password = request.form.get('cnfm_password')

        try:
            # Check teacher name validity
            if not re.match(r'^[a-zA-Z ]+$', name):
                flash("Teacher name should only contain letters and spaces.", category='error')
                return redirect(url_for('admin_routes.add_teacher'))

            # Check password length
            if len(password) < 6:
                flash("Password must be at least 6 characters long.", category='error')
                return redirect(url_for('admin_routes.add_teacher'))

            if password == cnfm_password:
                new_teacher = Teacher(name=name, email=email, password=generate_password_hash(password))
                db.session.add(new_teacher)
                db.session.commit()
                flash("Teacher added successfully.", category='success')
                return redirect(url_for('admin_routes.add_teacher'))
            else:
                flash("Passwords do not match!", category='error')
                return redirect(url_for('admin_routes.add_teacher'))
        except Exception as e:
            flash(f"An error occurred while adding the teacher: {str(e)}", category='error')
            return redirect(url_for('admin_routes.add_teacher'))

@admin_routes.route('/assign_subjects', methods = ['GET', 'POST'])
@login_required
def assign_subjects():
   if request.method == 'GET':
      id = request.args.get('teacher_id')
      teacher_periods = Period.query.filter_by(teacher_id = id).all()
      teacher_subjects = []
      for period in teacher_periods:
          
          subject = Subject.query.filter_by(subject_id = period.subject_id).first()
          teacher_subjects.append(subject)

      teacher = Teacher.query.filter_by(id = id).first()

      return render_template('assign_subjects.html',teacher = teacher,teacher_periods = teacher_periods,teacher_subjects = teacher_subjects)
   
   else:
      id = request.form.get('teacher_id')
      subject_id = request.form.get('subject_id')
      class_id = request.form.get('class_id')
      period_number = request.form.get('period_number')



      teacher = Teacher.query.filter_by(id = id).first()

      if not teacher:
        flash( "Teacher not found!",category='error')
        return redirect(url_for('admin_routes.assign_subjects'))

      if subject_id:
        if not re.match(r'^[0-9]+$', subject_id):
            flash('subject id must be a number.', category='error')
            return redirect(url_for('admin_routes.assign_subjects',teacher_id = teacher.id))
            
        new_subject = Subject.query.filter_by(subject_id= subject_id).first()
         
        if not new_subject:

            flash('subject does not exist with given subject id',category='error')
            return redirect(url_for('admin_routes.assign_subjects',teacher_id = teacher.id))
         
    
        if not re.match(r'^[0-9]+$', class_id):
            flash('teacher id must be a number.', category='error')
            return redirect(url_for('admin_routes.assign_subjects',teacher_id = teacher.id))
               
        new_class = Class.query.filter_by(id = class_id).first()

        if not new_class:
            flash('class not found with given class id.', category='error')
            return redirect(url_for('admin_routes.assign_subjects',teacher_id = teacher.id))
        
        period = Period.query.filter_by(class_id = class_id,
                                        period_number = period_number).first()
        
        period.teacher_id = id
        period.subject_id = subject_id
        db.session.commit()
        flash(f'teacher and subject are added to class with id {class_id}, period {period_number}', category='error')
        return redirect(url_for('admin_routes.assign_subjects',teacher_id = teacher.id))



@admin_routes.route('/add_class',methods = ['GET','POST'])
@login_required
def add_class():
   if request.method == 'GET':
    return render_template('add_class.html')
   else:
    id = request.form.get('id')
    name = request.form.get('name')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    teacher_id = request.form.get('teacher_id')

    is_class = Class.query.filter_by(id = id).first()

    if is_class:
        flash('class with id is already present',category='error')
        return redirect(url_for('admin_routes.add_class'))
    
    if int(id) <=0:
        flash('Please enter a valid Id',category='error')
        return redirect(url_for('admin_routes.add_class'))
      
    if len(name) < 3:
        flash('name should contain more 3 characters',category='error')
        return redirect(url_for('admin_routes.add_class'))
         
    new_class = Class(id = id, name = name,teacher_id = teacher_id, start_date = start_date, end_date = end_date)
    db.session.add(new_class)
    db.session.commit()
    flash("Class Added!", category='success')
    return redirect(url_for('admin_routes.add_class'))
   

@admin_routes.route('/remove_subject', methods=['GET', 'POST'])
@login_required
def remove_subject():
    if request.method == 'GET':
      id = request.args.get('teacher_id')
      teacher_periods = Period.query.filter_by(teacher_id = id).all()
      teacher_subjects = []
      for period in teacher_periods:
          
          subject = Subject.query.filter_by(subject_id = period.subject_id).first()
          teacher_subjects.append(subject)

      teacher = Teacher.query.filter_by(id = id).first()

      return render_template('remove_subject.html',teacher = teacher,teacher_periods = teacher_periods,teacher_subjects = teacher_subjects)
    else:
        teacher_id = request.form.get('teacher_id')
        subject_id = request.form.get('subject_id')
        class_id = request.form.get('class_id')
        period_number = request.form.get('period_number')

        
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            flash('Teacher not found.', 'error')
            return redirect(url_for('admin_routes.remove_subject', teacher_id = teacher_id))
        
        
        subject = Subject.query.get(subject_id)
        if not subject:
            flash('subject not found.', 'error')
            return redirect(url_for('admin_routes.remove_subject', teacher_id=teacher_id))
        

        is_class = Class.query.get(class_id)

        if not is_class:
            flash('class not found.', category='error')
            return redirect(url_for('admin_routes.remove_subject', teacher_id=teacher_id))
        
        
        period = Period.query.filter_by(teacher_id=teacher_id, 
                                subject_id=subject_id,
                                class_id=class_id,
                                period_number=period_number).first()
        
        if not period:
            flash('Invalid inputs , please enter valid inputs', category='error')
            return redirect(url_for('admin_routes.remove_subject', teacher_id=teacher_id))

        if period:
            period.subject_id = None
            period.teacher_id = None
            db.session.commit()


        flash('Subject removed from the teacher.',category= 'success')
        return redirect(url_for('admin_routes.remove_subject', teacher_id= teacher_id))
            

@admin_routes.route('/add_subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    if request.method == 'GET':
        return render_template('add_subject.html')
    else:
        
        subject_name = request.form.get('subject_name')

        if len(subject_name)<4:
            flash("subject name sholud have atleast 5 characters")
            return redirect(url_for('admin_routes.add_subject'))

        # Check for exceptions and provide a default value for subject_name
        try:
            new_subject = Subject( subject_name=subject_name)
            db.session.add(new_subject)
            db.session.commit()
            flash(f"Subject Added", category='success')
        except Exception as e:
            # Handle exceptions here (e.g., unique constraint violation)
            db.session.rollback()
            flash("An error occurred. Please check your input.", category='error')

        return redirect(url_for('admin_routes.add_subject'))
    
@admin_routes.route('/add_period', methods=['GET', 'POST'])
@login_required
def add_period():
    if request.method == 'GET':
        return render_template('add_period.html')
    else:
        class_id = request.form.get('class_id')
        period_number = request.form.get('period_number')
        subject_id = request.form.get('subject_id')
        teacher_id = request.form.get('teacher_id')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        if int(period_number) <= 0:
            flash('Please enter a valid period number', category='error')
            return redirect(url_for('admin_routes.add_period'))

        is_class = Class.query.filter_by(id=class_id).first()

        if not is_class:
            flash('Class not found with the given class id.', category='error')
            return redirect(url_for('admin_routes.add_period'))

        is_period = Period.query.filter(Period.period_number == period_number,Period.class_id == class_id).first()

        if is_period:
            flash('Period is already present.', category='error')
            return redirect(url_for('admin_routes.add_period'))

        is_subject = Subject.query.get(subject_id)

        if not is_subject:
            flash('Subject with the given id is not present.', category='error')
            return redirect(url_for('admin_routes.add_period'))

        is_teacher = Teacher.query.get(teacher_id)

        if not is_teacher:
            flash('Teacher with the given id is not present.', category='error')
            return redirect(url_for('admin_routes.add_period'))

        existing_period = Period.query.filter(
            Period.class_id == class_id,
            Period.start_time < end_time,
            Period.end_time > start_time
            ).first()
        if existing_period:
            flash('Time conflict with an existing period.', category='error')
            return redirect(url_for('admin_routes.add_period'))

        new_period = Period(
            class_id=class_id,
            period_number=period_number,
            subject_id=subject_id,
            teacher_id=teacher_id,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(new_period)
        db.session.commit()
        flash("Period Added!", category='success')
        return redirect(url_for('admin_routes.add_period'))