from flask import Blueprint,request,render_template,redirect,url_for,flash
from .models import Student,Class,Attendance,Period,Subject
from . import db
from flask_login import current_user
from datetime import datetime




period_attendance_routes = Blueprint('period_attendance_routes',__name__)

@period_attendance_routes.route('/get_period_attendance_page',methods = ['GET','POST'])
def get_period_attendance_view():
    role = current_user.get_role()
    return render_template('period_attendance_forms.html',role = role)


@period_attendance_routes.route('/post_subject_wise_attendance',methods = ['POST'])
def post_subject_wise_attendance():
   
   student_id = request.form.get('student_id_form1')
   class_id = request.form.get('class_id_form1')
   subject_id = request.form.get('subject_id_form1')
   subject_name = request.form.get('subject_name_form1')

   if student_id:
       return redirect(url_for('period_attendance_routes.get_subject_wise_attendance',
                               student_id = student_id,
                               subject_id = subject_id,
                               class_id =class_id))
   if class_id:
       return redirect(url_for('period_attendance_routes.get_subject_wise_attendance',
                               subject_id = subject_id))


@period_attendance_routes.route('/get_subject_wise_attendance',methods = ['GET'])
def get_subject_wise_attendance():
    student_id = request.args.get('student_id')  
    class_id = request.args.get('class_id')
    
    role = current_user.get_role()
  
    subject_id = request.args.get('subject_id')
    subject_name = request.args.get('subject_name')
    
    if student_id:
        if subject_name:
            subject = Subject.query.filter_by(subject_name=subject_name).first()
            if subject:
                subject_id = subject.subject_id
                
            else:
                flash('Subject not found with the given name', category='error')
                return render_template('period_attendance_forms.html')
        period = Period.query.filter_by(class_id = class_id, subject_id = subject_id).first()
            
        if not period:
            flash('Period is not present with your class_id and subject_id', category='error') 
            return render_template('period_attendance_forms.html')
        
        attendance_count = Attendance.query.filter(Attendance.student_id == student_id, Attendance.class_id == class_id,
                                                Attendance.period_number == period.period_number,
                                                Attendance.attendance_status == 'Present').count()
        
        total_periods = Attendance.query.filter(Attendance.student_id == student_id,
                                                Attendance.class_id == class_id,
                                            Attendance.period_number == period.period_number).count()
        
        if total_periods > 0:
            attendance_percentage = (attendance_count / total_periods) * 100
        else:
            attendance_percentage = 0.0
        
        rounded_percentage = round(attendance_percentage, 2)
        
        return render_template('view_period_attendance.html',
                               subject_id = subject_id,student_id = student_id,
                               class_id = class_id,
                                attendance_count=attendance_count,
                           total_periods=total_periods,
                           attendance_percentage=rounded_percentage,role = role,
                           form = 'form1')


@period_attendance_routes.route('/post_subject_wise_attendance_in_month',methods = ['POST'])
def post_subject_wise_attendance_in_month():
   student_id = request.form.get('student_id_form2')
   class_id = request.form.get('class_id_form2')
   subject_id = request.form.get('subject_id_form2')
   subject_name = request.form.get('subject_name_form2')
   in_month = request.form.get('in_month_form2')


   return redirect(url_for('period_attendance_routes.get_subject_wise_attendance_in_month',class_id = class_id,student_id = student_id,
                           subject_id = subject_id,subject_name = subject_name,in_month = in_month))


@period_attendance_routes.route('/get_subject_wise_attendance_in_month',methods = ['GET'])
def get_subject_wise_attendance_in_month():
    student_id = request.args.get('student_id')
    
    class_id = request.args.get('class_id')
    in_month = request.args.get('in_month')

    
    role = current_user.get_role()
    
    subject_id = request.args.get('subject_id')
    subject_name = request.args.get('subject_name')


    student = Student.query.get(student_id)

    if not student:
                flash('Student is not present given id', category='error') 
                return render_template('period_attendance_forms.html')

    if student:
               if subject_name:
                   subject = Subject.query.filter_by(subject_name = subject_name).first()
                   subject_id = subject.subject_id
                   
               period = Period.query.filter_by(class_id = class_id, subject_id = subject_id).first()
               
               if not period:
                   flash('Period is not present with your class_id and subject_id', category='error') 
                   return render_template('period_attendance_forms.html')
               
               period_number = period.period_number
               parsed_date = datetime.strptime(in_month, '%Y-%m')
               attendance_count = Attendance.query.filter(Attendance.student_id == student_id,
                                                          Attendance.period_number == period_number,
                                                  db.func.year(Attendance.date) == parsed_date.year,
                                                 db.func.month(Attendance.date) == parsed_date.month,
                                                  Attendance.attendance_status == 'Present'
                                                  ).count()
               
               if not attendance_count:
                   flash("Given month is not present in database,please enter valid inputs",category='error')
                   return render_template('period_attendance_forms.html')
               
               total_periods = Attendance.query.filter(Attendance.student_id == student_id, 
                                                       Attendance.period_number == period_number,
                                           db.func.year(Attendance.date) == parsed_date.year,
                                           db.func.month(Attendance.date) == parsed_date.month).count()
               
               attendance_percentage = (attendance_count/total_periods) *100
               rounded_percentage = round(attendance_percentage, 2)

               return render_template('view_period_attendance.html',attendance_percentage = rounded_percentage,
                              attendance_count = attendance_count,
                              class_id = class_id,student_id = student_id,
                              in_month = in_month,
                              total_periods = total_periods,form = 'form2',role = role)


@period_attendance_routes.route('/post_subject_wise_attendance_of_class_in_month',methods = ['POST'])
def post_subject_wise_attendance_of_class_in_month():

   
    class_id = request.form.get('class_id_form3')
    subject_id = request.form.get('subject_id_form3')
    subject_name = request.form.get('subject_name_form3')
    in_month = request.form.get('in_month_form3')

    return redirect(url_for('period_attendance_routes.get_subject_wise_attendance_of_class_in_month',class_id = class_id,
                           subject_id = subject_id,subject_name = subject_name,in_month = in_month))
     

@period_attendance_routes.route('/get_subject_wise_attendance_of_class_in_month',methods = ['GET'])
def get_subject_wise_attendance_of_class_in_month():
    class_id = request.args.get('class_id')
    in_month = request.args.get('in_month')
   
    subject_id = request.args.get('subject_id')
    subject_name = request.args.get('subject_name')

    role = current_user.get_role()

   
    if subject_name:   
        subject = Subject.query.filter_by(subject_name = subject_name).first()
        subject_id = subject.subject_id

    period = Period.query.filter_by(class_id = class_id, subject_id = subject_id).first()
               
    if not period:
        flash('Period is not present with your class_id and subject_id', category='error') 
        return render_template('period_attendance_forms.html')
               
    period_number = period.period_number


    parsed_date = datetime.strptime(in_month, '%Y-%m')
    attendance_count = Attendance.query.filter(Attendance.class_id == class_id,
                                                         Attendance.period_number == period_number,
                                                         db.func.year(Attendance.date) == parsed_date.year,
                                                 db.func.month(Attendance.date) == parsed_date.month,
                                                  Attendance.attendance_status == 'Present' ).count()
    if not attendance_count:
        flash("Given month is not present in database,please enter valid inputs",category='error')
        return render_template('period_attendance_forms.html')
    
    total_periods = Attendance.query.filter(Attendance.class_id == class_id,
                                                       Attendance.period_number == period_number,
                                           db.func.year(Attendance.date) == parsed_date.year,
                                           db.func.month(Attendance.date) == parsed_date.month).count()
    
    attendance_percentage = (attendance_count/total_periods) *100
    rounded_percentage = round(attendance_percentage, 2)

    return render_template('view_period_attendance.html',attendance_percentage = rounded_percentage,
                              attendance_count = attendance_count,class_id = class_id,
                              in_month = in_month,
                              total_periods = total_periods,role = role,form = 'form3')

@period_attendance_routes.route('/post_subject_wise_class_attendance_in_between_dates',methods = ['POST'])
def post_subject_wise_class_attendance_in_between_dates():
    student_id = request.form.get('student_id_form4')
    class_id = request.form.get('class_id_form4')
    subject_id = request.form.get('subject_id_form4')
    subject_name = request.form.get('subject_name_form4')
    from_date = request.form.get('from_date_form4')
    to_date = request.form.get('to_date_form4')


    return redirect(url_for('period_attendance_routes.get_subject_wise_class_attendance_in_between_dates',subject_id = subject_id,
                            subject_name = subject_name,
                            from_date = from_date,
                            to_date = to_date,
                              class_id = class_id))


@period_attendance_routes.route('/get_subject_wise_class_attendance_in_between_dates',methods = ['GET'])
def get_subject_wise_class_attendance_in_between_dates():
    class_id = request.args.get('class_id')
    
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date') 

    subject_id = request.args.get('subject_id')
    subject_name = request.args.get('subject_name')

    role = current_user.get_role()


    if subject_name:   
        subject = Subject.query.filter_by(subject_name = subject_name).first()
        subject_id = subject.subject_id

    parsed_from_date = datetime.strptime(from_date, "%Y-%m-%d")
    parsed_to_date = datetime.strptime(to_date, "%Y-%m-%d")

    period = Period.query.filter_by(class_id = class_id, subject_id = subject_id).first()
               
    if not period:
        flash('Period is not present with your class_id and subject_id', category='error') 
        return render_template('period_attendance_forms.html')
               
    period_number = period.period_number

    class_exists = Class.query.filter_by(id = class_id).first()
    if not class_exists:
            flash("class does not exists with given class id,please enter valid class Id",category='error')
            return render_template('calculate_attendance.html')
             
    if class_exists:
        class_start_date = class_exists.start_date

    if parsed_from_date.date() < class_start_date:
            flash("Given from date is less than class start date,please enter valid date inputs",category='error')
            return render_template('calculate_attendance.html')


        #for handling inavlid from and to date inputs
    if parsed_from_date>parsed_to_date:
            flash("'from date' is gtreater than 'to date',please enter valid inputs",category='error')
            return render_template('calculate_attendance.html')
    
    if parsed_to_date>datetime.now():
            flash("'to date' is greater than 'current date&time',please enter valid inputs",category='error')
            return render_template('calculate_attendance.html')


    attendance_count = Attendance.query.filter(Attendance.class_id == class_id,
                                               Attendance.period_number == period_number,
                                                 Attendance.date.between(parsed_from_date, 
                                                                          parsed_to_date,),
                                              Attendance.attendance_status == 'Present').count()
         
    if not attendance_count:
              flash(" Given 'from date' and 'to date' are not present in database,please enter valid inputs",category='error')
              return render_template('calculate_attendance.html')
    
    total_periods = Attendance.query.filter(Attendance.class_id == class_id,
                                         Attendance.period_number == period_number,
                                                 Attendance.date.between(parsed_from_date, 
                                                                          parsed_to_date)).count()
         
    attendance_percentage = (attendance_count/total_periods) * 100
    rounded_percentage = round(attendance_percentage, 2)

    return render_template('view_period_attendance.html',
                           attendance_percentage = rounded_percentage,subject_id = subject_id,
                              attendance_count = attendance_count,class_id = class_id,
                              to_date = to_date, from_date = from_date, 
                              total_periods = total_periods,role = role,form = 'form4')
    


@period_attendance_routes.route('/post_subject_wise_student_attendance_in_between_dates',methods = ['POST'])
def post_subject_wise_student_attendance_in_between_dates():
    student_id = request.form.get('student_id_form5')
    class_id = request.form.get('class_id_form5')
    subject_id = request.form.get('subject_id_form5')
    subject_name = request.form.get('subject_name_form5')
    from_date = request.form.get('from_date_form5')
    to_date = request.form.get('to_date_form5')


    return redirect(url_for('period_attendance_routes.get_subject_wise_student_attendance_in_between_dates',
                            student_id = student_id,
                            subject_id = subject_id,
                            subject_name = subject_name,
                            from_date = from_date,
                            to_date = to_date,
                              class_id = class_id))

@period_attendance_routes.route('/get_subject_wise_student_attendance_in_between_dates',methods = ['GET'])
def get_subject_wise_student_attendance_in_between_dates():
    class_id = request.args.get('class_id')
    student_id = request.args.get('student_id')
   
    
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    subject_id = request.args.get('subject_id')
    subject_name = request.args.get('subject_name')


    parsed_from_date = datetime.strptime(from_date, "%Y-%m-%d")
    parsed_to_date = datetime.strptime(to_date, "%Y-%m-%d")

    role = current_user.get_role()


    if subject_name:   
        subject = Subject.query.filter_by(subject_name = subject_name).first()
        subject_id = subject.subject_id


    period = Period.query.filter_by(class_id = class_id, subject_id = subject_id).first()
               
    if not period:
        flash('Period is not present with your class_id and subject_id', category='error') 
        return render_template('period_attendance_forms.html')
               
    period_number = period.period_number

    class_exists = Class.query.filter_by(id = class_id).first()
    if not class_exists:
            flash("class does not exists with given class id,please enter valid class Id",category='error')
            return render_template('calculate_attendance.html')
             
    if class_exists:
        class_start_date = class_exists.start_date

    if parsed_from_date.date() < class_start_date:
            flash("Given from date is less than class start date,please enter valid date inputs",category='error')
            return render_template('calculate_attendance.html')


        #for handling inavlid from and to date inputs
    if parsed_from_date>parsed_to_date:
            flash("'from date' is gtreater than 'to date',please enter valid inputs",category='error')
            return render_template('calculate_attendance.html')
    
    if parsed_to_date>datetime.now():
            flash("'to date' is greater than 'current date&time',please enter valid inputs",category='error')
            return render_template('calculate_attendance.html')


    attendance_count = Attendance.query.filter(Attendance.class_id == class_id,
                                               Attendance.student_id == student_id,
                                               Attendance.period_number == period_number,
                                                 Attendance.date.between(parsed_from_date, 
                                                                          parsed_to_date,),
                                              Attendance.attendance_status == 'Present').count()
         
    if not attendance_count:
              flash(" Given 'from date' and 'to date' are not present in database,please enter valid inputs",category='error')
              return render_template('calculate_attendance.html')
    
    total_periods = Attendance.query.filter(Attendance.class_id == class_id,
                                         Attendance.period_number == period_number,
                                          Attendance.student_id == student_id,
                                                 Attendance.date.between(parsed_from_date, 
                                                                          parsed_to_date)).count()
         
    attendance_percentage = (attendance_count/total_periods) * 100
    rounded_percentage = round(attendance_percentage, 2)

    return render_template('view_period_attendance.html',attendance_percentage = rounded_percentage,
                           subject_id = subject_id,student_id = student_id,
                              attendance_count = attendance_count,class_id = class_id,
                              to_date = to_date, from_date = from_date,
                                total_periods = total_periods,role = role,form = 'form5')