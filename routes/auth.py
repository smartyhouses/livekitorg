from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from database import db, User, ReferralCode
import uuid

auth_bp = Blueprint('auth', __name__)

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    referral_code = StringField('Referral Code', validators=[DataRequired()])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_referral_code(self, referral_code):
        code = ReferralCode.query.filter_by(code=referral_code.data).first()
        if not code:
            raise ValidationError('Invalid referral code.')
        if code.is_used:
            raise ValidationError('This referral code has already been used.')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('interact'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('interact'))
        else:
            flash('Login failed. Please check your username and password.')
    
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('interact'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        referral_code = ReferralCode.query.filter_by(code=form.referral_code.data).first()
        
        # Generate a unique room ID for the user
        room_id = f"room-{uuid.uuid4()}"
        
        # Create new user
        user = User(
            username=form.username.data,
            password_hash=generate_password_hash(form.password.data),
            room_id=room_id,
            referral_code_id=referral_code.id
        )
        
        # Mark referral code as used
        referral_code.is_used = True
        from datetime import datetime
        referral_code.used_at = datetime.utcnow()
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! You can now log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))