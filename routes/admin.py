from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from database import db, User, ReferralCode
from datetime import datetime
from functools import wraps

admin_bp = Blueprint('admin', __name__)

class GenerateCodesForm(FlaskForm):
    count = IntegerField('Number of Codes', validators=[DataRequired(), NumberRange(min=1, max=100)])
    submit = SubmitField('Generate Codes')

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

@admin_bp.route('/referrals', methods=['GET', 'POST'])
@admin_required
def referrals():
    form = GenerateCodesForm()
    
    if form.validate_on_submit():
        count = form.count.data
        codes = []
        
        for _ in range(count):
            code = ReferralCode(code=ReferralCode.generate_code())
            db.session.add(code)
            codes.append(code)
        
        db.session.commit()
        flash(f'Successfully generated {count} new referral codes.')
    
    # Get all codes with usage information
    all_codes = ReferralCode.query.order_by(ReferralCode.created_at.desc()).all()
    
    return render_template('admin/referrals.html', form=form, codes=all_codes)

@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.filter(User.username != 'admin').order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/referrals/delete/<int:code_id>', methods=['POST'])
@admin_required
def delete_referral(code_id):
    code = ReferralCode.query.get_or_404(code_id)
    
    # Check if code is unused before deleting
    if code.is_used:
        flash('Cannot delete a referral code that has been used.', 'error')
    else:
        db.session.delete(code)
        db.session.commit()
        flash('Referral code deleted successfully.')
    
    return redirect(url_for('admin.referrals'))