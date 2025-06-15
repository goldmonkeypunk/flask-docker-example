from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, Length, ValidationError

bp = Blueprint("auth", __name__, url_prefix="/auth")
ADMIN_INVITE_CODE = "admin123"              # измените при необходимости

# ───── WTForms ─────
class LoginForm(FlaskForm):
    email    = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(6)])
    submit   = SubmitField("Увійти")

class RegisterForm(FlaskForm):
    email       = EmailField("Email", validators=[DataRequired(), Email()])
    password    = PasswordField("Пароль", validators=[DataRequired(), Length(6)])
    role        = RadioField("Роль", choices=[("parent", "Батьки / Учень"),
                                              ("teacher", "Адмін")],
                             default="parent", validators=[DataRequired()])
    admin_code  = PasswordField("Код для адміна")
    submit      = SubmitField("Зареєструватись")

    def validate_admin_code(form, field):
        if form.role.data == "teacher" and field.data != ADMIN_INVITE_CODE:
            raise ValidationError("Невірний admin‑код")

# ───── маршруты ─────
@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("index"))
        flash("Невірний логін / пароль", "danger")
    return render_template("login.html", form=form)

@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email вже зареєстровано", "warning")
        else:
            new_user = User(email=form.email.data,
                            password=generate_password_hash(form.password.data),
                            role=form.role.data)
            db.session.add(new_user); db.session.commit()
            flash("Успішно! Увійдіть під своїм логіном.", "success")
            return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
