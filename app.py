from __future__ import annotations
import pathlib, datetime as dt, time, logging
from flask import Flask, render_template, jsonify, abort, request
from flask_login import LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, User, Student, Song, Attendance, StudentSong

PRICE = 130
DATA_DIR = pathlib.Path("/data"); DATA_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.update(
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{DATA_DIR/'app.db'}",
    SECRET_KEY="replace-me",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db.init_app(app)

# ───── Login ─────
login = LoginManager(app); login.login_view = "auth.login"
@login.user_loader
def load_user(uid): return db.session.get(User, uid)

# ───── Blueprint auth ─────
from auth import bp as auth_bp             # noqa: E402
app.register_blueprint(auth_bp)

# ───── helpers ─────
def week_range(today: dt.date) -> tuple[dt.date, dt.date]:
    start = today - dt.timedelta(days=today.weekday())      # Monday
    end   = start + dt.timedelta(days=6)                    # Sunday
    return start, end

def week_dates(today: dt.date) -> list[dt.date]:
    s, _ = week_range(today); return [s + dt.timedelta(d) for d in range(7)]

def week_sum(stu_id: int, start: dt.date, end: dt.date) -> int:
    cnt = Attendance.query.filter_by(student_id=stu_id)\
          .filter(Attendance.date.between(start, end)).count()
    return cnt * PRICE

def admin_required():
    if current_user.role != "teacher":
        abort(403, "Тільки адміністратор може виконати дію")

# ───── Routes ─────
@app.get("/")
@login_required
def index():
    today = dt.date.today()
    week_start, week_end = week_range(today)
    days = week_dates(today)

    studs = (Student.query.all() if current_user.role == "teacher"
             else Student.query.filter_by(parent_id=current_user.id).all())

    # Attendance dict: {student_id: set("YYYY-MM-DD", ...)}
    attend = {s.id: set() for s in studs}
    for a in Attendance.query.filter(Attendance.date.between(week_start, week_end)).all():
        attend.setdefault(a.student_id, set()).add(a.date.isoformat())

    # список студентов + недельная сумма
    data = [{"id": s.id, "name": s.name,
             "week": week_sum(s.id, week_start, week_end)} for s in studs]

    return render_template("index.html",
        students=data, days=days, attend=attend, price=PRICE,
        total=sum(d["week"] for d in data), songs=Song.query.all())

# ───── API: attendance toggle ─────
@app.post("/api/attendance/toggle")
@login_required
def toggle_attendance():
    admin_required()
    sid = request.json.get("student_id")
    d   = dt.date.fromisoformat(request.json.get("date"))
    row = Attendance.query.filter_by(student_id=sid, date=d).first()
    if row:
        db.session.delete(row)
    else:
        db.session.add(Attendance(student_id=sid, date=d))
    db.session.commit()
    ws, we = week_range(dt.date.today())
    return jsonify({"week": week_sum(sid, ws, we),
                    "total": sum(week_sum(s.id, ws, we) for s in Student.query.all())})

# ───── API: assign song ─────
@app.post("/api/assign")
@login_required
def assign():
    admin_required()
    sid, tid = request.json.get("student_id"), request.json.get("song_id")
    if not (sid and tid): abort(400)
    db.session.merge(StudentSong(student_id=sid, song_id=tid)); db.session.commit()
    return "", 201

# ───── API: add student ─────
@app.post("/api/student")
@login_required
def add_student():
    admin_required()
    name = request.json.get("name", "").strip()
    if not name: abort(400)
    s = Student(name=name, parent_id=current_user.id)
    db.session.add(s); db.session.commit(); return jsonify({"id": s.id, "name": s.name}), 201

# ───── API: add song ─────
@app.post("/api/song")
@login_required
def add_song():
    admin_required()
    title = request.json.get("title", "").strip()
    author = request.json.get("author", "").strip()
    diff = int(request.json.get("difficulty", 1))
    if not title or not author: abort(400)
    song = Song(title=title, author=author, difficulty=diff)
    db.session.add(song); db.session.commit()
    return jsonify({"id": song.id, "title": song.title,
                    "author": song.author, "difficulty": song.difficulty}), 201

@app.get("/healthz")
def health(): return "ok", 200

# ───── Seed ─────
with app.app_context():
    db.create_all()
    if not User.query.first():
        admin = User(email="teacher@example.com",
                     password=generate_password_hash("secret"),
                     role="teacher")
        db.session.add(admin); db.session.commit()
        for n in ["Діана","Саша","Андріана","Маша","Ліза",
                  "Кіріл","Остап","Єва","Валерія","Аня"]:
            db.session.add(Student(name=n, parent_id=admin.id))
        for t,a,d in [("Bluestone Alley","Chad Lawson",2),
                      ("Smells like teen spirit","Nirvana",1),
                      ("Horimia","Masaru Yokoyama",3)]:
            db.session.add(Song(title=t, author=a, difficulty=d))
        db.session.commit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=5000, debug=True)
