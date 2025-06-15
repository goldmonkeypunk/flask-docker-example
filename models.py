from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role     = db.Column(db.String, default="parent")      # teacher | parent

class Student(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class Song(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.Integer, default=1)          # 1‑4 ★

class Attendance(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    date       = db.Column(db.Date, nullable=False)

class StudentSong(db.Model):
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), primary_key=True)
    song_id    = db.Column(db.Integer, db.ForeignKey("song.id"), primary_key=True)
