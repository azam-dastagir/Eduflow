from flask import Blueprint,request,render_template,redirect,url_for,flash
from .models import Assignment,Assessment,Question,AnswerChoice,AssessmentResult
from . import db
from flask_login import login_required,current_user


student_routes = Blueprint('student_routes',__name__)


@student_routes.route('/homepage_student')
def homepage_student():
   return render_template('homepage_student.html')

@student_routes.route('/calculate_student_attendance')
def calculate_student_attendance():
   return render_template('calculate_student_attendance.html')


@student_routes.route('/view_assignments',methods = ['GET','POST'])
@login_required
def view_assignments():
   if request.method == 'GET':
      class_id = current_user.class_id
      assignments = Assignment.query.filter_by(class_id = class_id).all()
      return render_template('view_assignments.html', current_student = current_user, assignments = assignments)


@student_routes.route('/view_assessments',methods = ['GET','POST'])
@login_required
def view_assessments():
   if request.method == 'GET':
      class_id = current_user.class_id
      assessments = Assessment.query.filter_by(class_id = class_id).all()
      return render_template('view_assessments.html', current_student = current_user, assessments = assessments)


@student_routes.route('/take_assessment', methods=['GET', 'POST'])
@login_required
def take_assessment():
    assessment_id = request.args.get('assessment_id')

    # Check if the assessment_id is valid
    assessment = Assessment.query.filter_by(assessment_id = assessment_id).first()
    if assessment is None:
        flash('Invalid assessment ID', category='error')
        return redirect(url_for('student_routes.view_assessments'))  # Redirect to an error page

    # Fetch questions and related choices for the assessment
    questions = Question.query.filter_by(assessment_id=assessment_id).all()

    return render_template('take_assessment.html', current_student=current_user, questions=questions, assessment=assessment)


@student_routes.route('/submit_assessment', methods=['POST'])
@login_required
def submit_assessment():
    if request.method == 'POST':

        assessment_id = request.form.get('assessment_id')
        student_id = current_user.id
        
        marks_obtained = 0
        total_marks = 0
        
        # Iterate over the submitted form data to process the user's choices
        for question_id, choice_id in request.form.items():
            if question_id.startswith('question_'):
                question_id = question_id.split('_')[-1]  # Extract the question_id
                choice = AnswerChoice.query.get(choice_id)
                if choice:
                    # Check if the choice is correct and increment marks
                    if choice.is_correct:
                        marks_obtained += 1
                    total_marks += 1
        
        # Calculate the percentage
        if total_marks > 0:
            percentage = (marks_obtained / total_marks) * 100
        else:
            percentage = 0  
       
        result = AssessmentResult(student_id=student_id, assessment_id=assessment_id, obtained_marks=marks_obtained, percentage=percentage)
        db.session.add(result)
        db.session.commit()
        
        return redirect(url_for('student_routes.show_result', result_id=result.result_id))


@student_routes.route('/show_result')
@login_required
def show_result():
   result_id = request.args.get('result_id')
   result = AssessmentResult.query.get(result_id)
   if not result:
      return "Result not found"

   return render_template('show_result.html', result=result)