from flask import Blueprint,request,render_template,redirect,url_for,flash
from .models import Teacher, Student, Administrator
from werkzeug.security import check_password_hash
from flask_login import login_user,logout_user,login_required


auth = Blueprint('auth', __name__)

@auth.route('/')
@auth.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'GET':
            return render_template('login.html')
        elif request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role')

            if role == 'Teacher':
                curr_user = Teacher.query.filter_by(email=email).first()
            elif role == 'Student':
                curr_user = Student.query.filter_by(email=email).first()
            elif role == 'Admin':
                curr_user = Administrator.query.filter_by(email=email).first()
            else:
                flash(message="Invalid role selected.", category="error")
                return redirect(url_for('auth.login'))

            if curr_user:
                if check_password_hash(curr_user.password, password):
                    login_user(user=curr_user)
                    flash(message='Login Successful', category='success')

                    return redirect(url_for('views.home', role=role))
                else:
                    flash(message="Wrong password, please try again!", category="error")
            else:
                flash(message="User does not exist, please register first!", category='error')

        return redirect(url_for('auth.login'))  # Return a response for other cases

    except Exception as e:
        print(f"Exception Occurred: {str(e)}")
        return render_template('login.html')  # Return a response for exceptions


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(message="Logout Successful!",category='success')
    return render_template('login.html')