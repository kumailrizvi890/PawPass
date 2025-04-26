"""
Authentication models for PawPass
"""
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship

# Setup logging
logger = logging.getLogger(__name__)

class User:
    """User model for authentication"""
    
    def __init__(self, username, email, password=None, first_name=None, last_name=None, role='volunteer'):
        """
        Initialize a new user
        
        Args:
            username: Username
            email: Email address
            password: Plain text password
            first_name: First name
            last_name: Last name
            role: User role
        """
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.last_login = None
        
        if password:
            self.set_password(password)
    
    def set_password(self, password):
        """Set the user's password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if the user has admin role"""
        return self.role == 'admin'
    
    def is_volunteer(self):
        """Check if the user has volunteer role"""
        return self.role == 'volunteer'
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
    
    def to_dict(self):
        """Convert user to a dictionary (for serialization)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }