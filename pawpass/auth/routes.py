"""
Authentication routes for PawPass
"""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from pawpass.auth.auth import authenticate_user, get_current_user

# Setup logging
logger = logging.getLogger(__name__)

# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login
    """
    # Check if user is already logged in
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('auth/login.html')
        
        # Authenticate user
        user_id = authenticate_user(username, password)
        if user_id:
            # Set user in session
            session['user_id'] = user_id
            session.permanent = remember
            
            # Redirect to next page or default
            next_page = request.args.get('next')
            if not next_page or next_page.startswith('//'):
                next_page = url_for('index')
                
            flash('Login successful', 'success')
            logger.info(f"User {username} logged in successfully")
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'error')
            logger.warning(f"Failed login attempt for username: {username}")
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """
    Handle user logout
    """
    # Remove user from session
    session.pop('user_id', None)
    session.pop('user_role', None)
    
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration
    """
    # Check if user is already logged in
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate form data
        if not username or not email or not password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        # Check if username or email already exists
        # This would check against the database in a real implementation
        
        # Create user (placeholder)
        # This would create a new user in the database in a real implementation
        flash('Registration successful! You can now log in.', 'success')
        logger.info(f"User {username} registered successfully")
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/profile')
def profile():
    """
    User profile page
    """
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to view your profile', 'error')
        return redirect(url_for('auth.login'))
    
    # Get current user
    user = get_current_user()
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('auth.logout'))
    
    return render_template('auth/profile.html', user=user)

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """
    Handle password reset requests
    """
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Email is required', 'error')
            return render_template('auth/reset_password.html')
        
        # This would send a password reset email in a real implementation
        
        flash('If your email exists in our system, you will receive a password reset link.', 'success')
        logger.info(f"Password reset requested for email: {email}")
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html')