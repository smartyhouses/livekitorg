from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from database import db, User
from datetime import datetime
from functools import wraps

admin_bp = Blueprint('admin', __name__)

class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    is_admin = BooleanField('Admin Privileges')
    submit = SubmitField('Create User')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

def admin_required(func):
    """Decorator to require admin access for a route"""
    @wraps(func)
    @login_required
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('interact'))
        return func(*args, **kwargs)
    return decorated_view

@admin_bp.route('/')
@admin_required
def index():
    return render_template('admin/index.html')

@admin_bp.route('/users', methods=['GET', 'POST'])
@admin_required
def users():
    form = CreateUserForm()
    
    if form.validate_on_submit():
        # Generate a unique room ID for the user
        room_id = User.generate_room_id()
        
        # Create new user (with no password - will be set on first login)
        user = User(
            username=form.username.data,
            room_id=room_id,
            is_admin=form.is_admin.data,
            is_activated=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User "{form.username.data}" created successfully. User can now activate their account.', 'success')
        
        # Redirect to the same page to reset the form
        return redirect(url_for('admin.users'))
    
    # Get all users except the current admin
    all_users = User.query.filter(User.id != current_user.id).order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', form=form, users=all_users)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting other admins as a safety measure
    if user.is_admin and user.id != current_user.id:
        flash('Cannot delete another administrator account.', 'danger')
        return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User "{username}" deleted successfully.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/reset/<int:user_id>', methods=['POST'])
@admin_required
def reset_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Reset the user's password and activation status
    user.password_hash = None
    user.is_activated = False
    db.session.commit()
    
    flash(f'User "{user.username}" has been reset. They will need to set a new password.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/generate-link/<int:user_id>')
@admin_required
def generate_activation_link(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.is_activated:
        flash(f'User "{user.username}" has already activated their account.', 'warning')
        return redirect(url_for('admin.users'))
    
    # Generate an activation link to share with the user
    activation_link = url_for('auth.authenticate', username=user.username, _external=True)
    
    return render_template('admin/activation_link.html',
                           user=user,
                           activation_link=activation_link)