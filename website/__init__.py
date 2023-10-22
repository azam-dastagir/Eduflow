from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)
db = SQLAlchemy()
login_manager = LoginManager()

mail = Mail()

def create_app():
    app.secret_key = 'Azam'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:8106328334@localhost/StudentManagementAppDB'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

     #Configure flask-Mail for Gmail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'sdgiri0662@gmail.com'
    app.config['MAIL_PASSWORD'] = 'cclwfpwvrpmstzng'
    app.config['MAIL_DEFAULT_SENDER'] = 'sdgiri0662@gmail.com'



    db.__init__(app)
    mail.__init__(app)

    with app.app_context():
        db.create_all()


    from .auth import auth
    from .views import views
    from .admin_routes import admin_routes
    from .teacher_routes import teacher_routes
    from .student_routes import student_routes
    from .period_attendance_routes import period_attendance_routes


    from .models import Teacher, Student, Administrator
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id_with_role):

        #id_with_role = "teacher-1"
        print(id_with_role)
        role, user_id = id_with_role.split("-")

        
        user = None

        if role == 'teacher':
            user = Teacher.query.filter_by(id=int(user_id)).first()
        elif role == 'student':
            user = Student.query.filter_by(id=int(user_id)).first()
        elif role == 'admin':
            user = Administrator.query.filter_by(id=int(user_id)).first()

        return user

    app.register_blueprint(auth, url_prefix = '/')
    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(teacher_routes, url_prefix = '/')
    app.register_blueprint(student_routes, url_prefix = '/')
    app.register_blueprint(admin_routes, url_prefix = '/')
    app.register_blueprint(period_attendance_routes, url_prefix = '/')


    return app