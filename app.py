from flask import request,render_template,url_for,redirect,Flask,session,make_response,flash,get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_restful import Api,Resource
from datetime import datetime,timedelta
import re

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

app.secret_key='anyrandomsecretkey'

db=SQLAlchemy(app)

api=Api(app)

class Doctor(db.Model):
    __tablename__='doctor'
    doc_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name=db.Column(db.String(100),nullable=False)
    speciality=db.Column(db.String(100),nullable=False)
    phone=db.Column(db.String(10),nullable=False,unique=True)
    email=db.Column(db.String(100),nullable=False,unique=True)
    experience=db.Column(db.Integer)
    comments=db.Column(db.Text)
    availability=db.relationship('AvailabilityDoctor',backref='doctor',cascade='all,delete-orphan')
    password=db.Column(db.String(50),nullable=False)
    dept_id=db.Column(db.Integer,db.ForeignKey('department.dept_id'))
    appointments=db.relationship('Appointments',backref='doctor',cascade='all,delete-orphan')
    blacklist=db.relationship('DoctorBlacklist',backref='doctor',cascade='all,delete-orphan',lazy=True)

class Admin(db.Model):
    __tablename__="admin"
    admin_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    password=db.Column(db.String(50),unique=True,nullable=False)
    admin_name=db.Column(db.String(10),nullable=False)
    email_id=db.Column(db.String(100),nullable=False,unique=True)

class Patient(db.Model):
    __tablename__='patient'
    patient_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name=db.Column(db.String(100),nullable=False)
    age=db.Column(db.Integer,nullable=False)
    gender=db.Column(db.String(10),nullable=False)
    phone=db.Column(db.String(10),nullable=False,unique=True)
    email=db.Column(db.String(100),nullable=False,unique=True)
    dob=db.Column(db.Date)
    height=db.Column(db.Float)
    weight=db.Column(db.Float)
    address=db.Column(db.Text)
    city=db.Column(db.String(50))
    state=db.Column(db.String(50))
    password=db.Column(db.String(50),nullable=False)
    appointment=db.relationship('Appointments',backref='patient',cascade='all,delete-orphan',lazy=True)
    blacklist=db.relationship('PatientBlacklist',backref='patient',cascade='all,delete-orphan',lazy=True)

class Department(db.Model):
    __tablename__='department'
    dept_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    dept_Name=db.Column(db.String(100),nullable=False,unique=True)
    description=db.Column(db.Text)
    doctors=db.relationship('Doctor',backref='department')

class Appointments(db.Model):
    __tablename__='appointments'
    appt_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    description=db.Column(db.Text)
    time=db.Column(db.Time,nullable=False)
    date=db.Column(db.Date,nullable=False)
    status=db.Column(db.String(20),nullable=False)
    doctor_id=db.Column(db.Integer,db.ForeignKey('doctor.doc_id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False)
    patient_id=db.Column(db.Integer,db.ForeignKey('patient.patient_id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False)
    patient_history=db.relationship('Treatment',backref='appointments',uselist=False)

class AvailabilityDoctor(db.Model):
    __tablename__='doctor_availability'
    av_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    doc_id=db.Column(db.Integer,db.ForeignKey('doctor.doc_id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False)
    day=db.Column(db.String(10),nullable=False)
    start_time=db.Column(db.Time,nullable=False)
    end_time=db.Column(db.Time,nullable=False)

class Treatment(db.Model):
    __tablename__="Patient_Diagnosis_History"
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    appt_id=db.Column(db.Integer,db.ForeignKey('appointments.appt_id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False)
    bp=db.Column(db.Float)
    d_bp=db.Column(db.Float)
    heartrate=db.Column(db.Float)
    medicine=db.Column(db.Text)
    diagnosis=db.Column(db.Text)
    prescription=db.Column(db.Text)
    visit_type=db.Column(db.String(50),nullable=False)
    test_done=db.Column(db.String(50),nullable=False)

class DoctorBlacklist(db.Model):
    __tablename__="doctor_blacklist"
    black_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    doctor_id=db.Column(db.Integer,db.ForeignKey('doctor.doc_id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False)

class PatientBlacklist(db.Model):
    __tablename__="patient_blacklist"
    black_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    patient_id=db.Column(db.Integer,db.ForeignKey('patient.patient_id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False)

with app.app_context():
    db.create_all() 
    email='admin123@hospital.com'
    password='Hadmin@1234'
    admin_person=Admin.query.filter_by(email_id=email,password=password).first()

    if not admin_person:
        admins=Admin(email_id=email,password=password,admin_name='ADMIN123')
        db.session.add(admins)
        db.session.commit()
@app.route("/")
def initial():
    return render_template("signin.html")
            
@app.route("/sign_in",methods=['POST','GET'])
def sign_in():
    if request.method=='POST':
        email=request.form['mail']
        password=request.form['password']
        role=request.form['role']

        pat_blacklist=PatientBlacklist.query.all()
        pat_black_ids=[pat.patient_id for pat in pat_blacklist]
        doc_blacklist=DoctorBlacklist.query.all()
        doc_black_ids=[doc.doctor_id for doc in doc_blacklist]

        if role.lower()=='patient':
            person=Patient.query.filter_by(email=email,password=password).first()
            if person:
                if person.patient_id in pat_black_ids:
                    flash("You are blacklisted! You can't login","danger")
                    return redirect("/sign_in")
                else:
                    session['role']='patient'
                    session['id']=person.patient_id
                    return redirect(url_for('patient',patient_id=person.patient_id))
            else:
                flash("No patient available please check the username or password","danger")
                return redirect("/sign_in")
        
        elif role.lower()=='doctor':
            person=Doctor.query.filter_by(email=email,password=password).first()
            if person:
                if person.doc_id in doc_black_ids:
                    flash("You are blacklisted! You can't login","danger")
                    return redirect("/sign_in")
                else:
                    session['role']='doctor'
                    session['id']=person.doc_id
                    return redirect(url_for('doctors',doctor_id=person.doc_id))
            else:
                flash("No Doctor available please check the username or password","danger")
                return redirect("/sign_in")
            
        elif role.lower()=='admin':
            person=Admin.query.filter_by(email_id=email,password=password).first()
            if person:
                session['role']='admin'
                session['id']=person.admin_id
                return redirect(url_for('admin',admin_id=person.admin_id))
            else:
                flash("No admin available please check the username or password","danger")
                return redirect("/sign_in")
        else:
            flash("Invalid Login! Sign Up if you dont have an account","danger")

    return render_template("signin.html")
@app.route("/patient_signup",methods=['POST','GET'])
def patient_signup():
    if request.method=='POST':
        name=request.form['name']
        age=int(request.form['age'])
        phone=request.form['phoneno']
        gender=request.form['gender']
        email=request.form['mail']
        password=request.form['password']
        height=request.form['height']
        weight=request.form['weight']
        city=request.form['city']
        address=request.form['address']
        state=request.form['state']
        dob=request.form['dob']
        
        password_pattern=r"^(?=.*[A-Za-z0-9])[A-Za-z0-9@]{8,}$"
        if not re.fullmatch(password_pattern,password):
            flash("Choose another password! Min 8 characters","warning")
            return render_template("pat_signup.html")

        phone_pattern=r"^[6789][0-9]{9}$"
        if not re.fullmatch(phone_pattern,phone):
            flash("Enter valid phone number!" ,"warning")
            return render_template("pat_signup.html")

        name_pattern=r"^[a-zA-Z ]+$"
        if not re.fullmatch(name_pattern,name):
            flash("Enter valid name!" ,"warning")
            return render_template("pat_signup.html")
        if Patient.query.filter_by(name=name,
            age=age,
            phone=phone,
            gender=gender,
            email=email,
            height=height,
            weight=weight,
            city=city,
            state=state,
            dob=dob).first():
            flash("You already have an account! Sign In","danger")
            return redirect("/sign_in")
        dob=datetime.strptime(dob,"%Y-%m-%d").date()
        pat=Patient(
            name=name,
            age=age,
            phone=phone,
            gender=gender,
            email=email,
            password=password,
            height=height,
            weight=weight,
            city=city,
            state=state,
            address=address,
            dob=dob
        )
        db.session.add(pat)
        db.session.commit()
        flash("Successfully registered yourself","success")
        return render_template("signin.html")
    
    return render_template("pat_signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return render_template("signin.html")

class DoctorResource(Resource):
    def get(self,doctor_id=None):
         if 'add' in request.path:
            if session.get('role')=='admin':
                html=render_template('doc_signup.html')
                return make_response(html,200)
            else:
                return redirect("/sign_in")
            
    def post(self,doctor_id=None):
        if session.get('role')=='admin':
            name=request.form['name']
            speciality=request.form['speciality']
            phone=request.form['phoneno']
            email=request.form['mail']
            department=request.form['department']
            password=request.form['password']
            experience=int(request.form['experience'])
            comment=request.form['comments']
            
            departments=Department.query.filter_by(dept_Name=department).first()
            if departments:
                dept=departments.dept_id

                doc=Doctor(
                    name=name,
                    speciality=speciality,
                    phone=phone,
                    email=email,
                    dept_id=dept,
                    password=password,
                    experience=experience,
                    comments=comment
                )
                if Doctor.query.filter_by(name=name,
                    speciality=speciality,
                    phone=phone,
                    email=email,
                    dept_id=dept,
                    password=password,
                    experience=experience,
                    comments=comment).first():
                    flash("already added doctor","primary")
                db.session.add(doc)
                db.session.commit()
                flash("Successfully registered doctor","success")
                return redirect(url_for("admin"))
            elif not departments:
                flash("No department! Add department first","warning")
                return redirect(url_for("admin"))
        else:
            return redirect("/sign_in")
              
class DepartmentResource(Resource):
    def get(self,dept_name=None):
        if 'add' in request.path:
            if session.get('role')=='admin':
                html=render_template('deptadd.html')
                return make_response(html,200)
            else:
                return redirect("/sign_in")
            
        if dept_name:
            dept=Department.query.filter_by(dept_Name=dept_name).first()
            if dept:
                doct_list=[doc for doc in dept.doctors]
                html=render_template("dept_desc.html",name=dept.dept_Name,ID=dept.dept_id,doctors=doct_list,desc=dept.description,sesson_user_id=session.get("id"))
                return make_response(html,200)
            else:
                flash("No department found","danger")
                return redirect(url_for("admin"))
        dept=Department.query.all()
        html=render_template("deptlist.html",departments=dept,sesson_user_id=session.get("id"))
        return make_response(html,200)
    
    def post(self):
        deptName=request.form['name']
        description=request.form['description']

        dept=Department(dept_Name=deptName,description=description)

        db.session.add(dept)
        db.session.commit()

        return redirect('/departments')
    
api.add_resource(DepartmentResource,"/departments","/departments/add","/departments/<string:dept_name>")
api.add_resource(DoctorResource,"/add_doctors",endpoint='add_doctors')

if __name__=="__main__":
    app.run(debug=True)
