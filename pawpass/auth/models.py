"""
Authentication models for PawPass
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

# This will be imported from the main application
# For now, we're defining it here for reference
# db = SQLAlchemy()

# This class will be integrated with the main models in the future
class User:
    """User model for authentication"""
    
    # Schema definition for reference
    # id = Column(Integer, primary_key=True)
    # username = Column(String(64), unique=True, nullable=False)
    # email = Column(String(120), unique=True, nullable=False)
    # password_hash = Column(String(256), nullable=False)
    # first_name = Column(String(64), nullable=True)
    # last_name = Column(String(64), nullable=True)
    # role = Column(String(20), default='volunteer')
    # is_active = Column(Boolean, default=True)
    # created_at = Column(DateTime, default=datetime.utcnow)
    # last_login = Column(DateTime, nullable=True)
    
    def set_password(self, password):
        """Set the user's password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
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