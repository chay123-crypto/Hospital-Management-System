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