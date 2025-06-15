from __future__ import annotations
import pathlib, os, datetime as dt, time, uuid, logging
from flask import Flask, render_template, jsonify, abort, request
from flask_login import LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, User, Student, Song, Attendance, StudentSong

PRICE = 130
BASE = pathlib.Path(__file__).parent            # /app (read‑only внутри контейнера)
DATA_DIR = pathlib.Path("/data")                # отдельный том под SQLite
DATA_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.update(
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{DATA_DIR/'app.db'}",
    SECRET_KEY="replace-me",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db.init_app(app)

# ───── Flask‑Login ─────
login = LoginManager(app)
login.login_view = "auth.login"

@login.user_loader
def load_user(uid):               # noqa: D401
    return db.session.get(User, uid)

# ───── Blueprint auth ─────
from auth import bp as auth_bp     # noqa: E402  (импорт после инициализации app)
app.register_blueprint(auth_bp)

# ───── helpers ─────
def week_sum(stu_id: int) -> int:
    return Attendance.query.filter_by(student_id=stu_id).count() * PRICE

def total_sum() -> int:
    return db.session.query(Attendance.id).count() * PRICE

# ───── Routes ─────
@app.get("/")
@login_required
def index():
    studs = (Student.query.all() if current_user.role == "teacher"
             else Student.query.filter_by(parent_id=current_user.id).all())
    data = [{"id": s.id, "name": s.name, "week": week_sum(s.id)} for s in studs]
    return render_template("index.html",
        students=data, total=total_sum(), songs=Song.query.all())

@app.post("/api/attendance/<int:stu_id>")
@login_required
def add_lesson(stu_id):
    Attendance(student_id=stu_id, date=dt.date.today())
    db.session.commit()
    return jsonify({"week": week_sum(stu_id), "total": total_sum()})

@app.delete("/api/attendance/<int:stu_id>")
@login_required
def del_lesson(stu_id):
    row = (Attendance.query.filter_by(student_id=stu_id)
           .order_by(Attendance.id.desc()).first())
    if row:
        db.session.delete(row)
        db.session.commit()
    return jsonify({"week": week_sum(stu_id), "total": total_sum()})

@app.post("/api/assign")
@login_required
def assign():
    payload = request.get_json(force=True)
    sid, tid = payload.get("student_id"), payload.get("song_id")
    if not (sid and tid):
        abort(400)
    db.session.merge(StudentSong(student_id=sid, song_id=tid))
    db.session.commit()
    return "", 201

@app.get("/healthz")
def health():
    return "ok", 200

@app.get("/slow-analysis")
def slow():
    time.sleep(2)
    return "done", 200

# ───── Seed (первый запуск) ─────
with app.app_context():
    db.create_all()
    if not User.query.first():
        admin = User(email="teacher@example.com",
                     password=generate_password_hash("secret"),
                     role="teacher")
        db.session.add(admin)
        db.session.commit()

        for n in ["Діана", "Саша", "Андріана", "Маша", "Ліза",
                  "Кіріл", "Остап", "Єва", "Валерія", "Аня"]:
            db.session.add(Student(name=n, parent_id=admin.id))

        for title, diff in [("Bluestone Alley", 2),
                            ("Smells like teen spirit", 1),
                            ("Horimia", 3)]:
            db.session.add(Song(title=title, difficulty=diff))
        db.session.commit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(port=5000, debug=True, host="0.0.0.0")
