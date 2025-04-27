from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Pet(db.Model):
    """Pet model for storing pet-related information"""
    __tablename__ = 'pets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    is_emergency = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    updates = relationship("PetUpdate", back_populates="pet", cascade="all, delete-orphan")
    checklists = relationship("Checklist", back_populates="pet", cascade="all, delete-orphan")
    # Defer relationship to avoid circular dependencies
    # The pet-weight relationship will be set at the bottom of this file

    def __repr__(self):
        return f"<Pet {self.name}>"


class PetUpdate(db.Model):
    """Model for storing pet care updates"""
    __tablename__ = 'pet_updates'

    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, ForeignKey('pets.id', ondelete='CASCADE'), nullable=False)
    update_text = db.Column(db.Text, nullable=False)
    update_date = db.Column(db.Date, nullable=False)
    update_time = db.Column(db.Time, nullable=False)
    volunteer_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    pet = relationship("Pet", back_populates="updates")

    def __repr__(self):
        return f"<PetUpdate {self.id} for Pet {self.pet_id}>"


class ChecklistItem(db.Model):
    """Model for checklist item templates"""
    __tablename__ = 'checklist_items'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    species_applicable = db.Column(db.String(50), nullable=True)  # e.g., 'dog', 'cat', or NULL for all
    
    # Relationships
    checklist_completions = relationship("ChecklistCompletion", back_populates="checklist_item")
    
    def __repr__(self):
        return f"<ChecklistItem {self.description}>"


class Checklist(db.Model):
    """Model for completed checklists"""
    __tablename__ = 'checklists'

    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, ForeignKey('pets.id', ondelete='CASCADE'), nullable=False)
    volunteer_name = db.Column(db.String(100), nullable=True)
    completion_date = db.Column(db.Date, nullable=False)
    completion_time = db.Column(db.Time, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    pet = relationship("Pet", back_populates="checklists")
    completed_items = relationship("ChecklistCompletion", back_populates="checklist", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Checklist {self.id} for Pet {self.pet_id}>"


class ChecklistCompletion(db.Model):
    """Model for linking completed checklist items to a checklist"""
    __tablename__ = 'checklist_completions'

    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, ForeignKey('checklists.id', ondelete='CASCADE'), nullable=False)
    checklist_item_id = db.Column(db.Integer, ForeignKey('checklist_items.id'), nullable=False)
    completed = db.Column(db.Boolean, default=True)
    value = db.Column(db.String(255), nullable=True)  # To store additional info like water intake amount, etc.
    notes = db.Column(db.Text, nullable=True)  # For any additional observations
    
    # Relationships
    checklist = relationship("Checklist", back_populates="completed_items")
    checklist_item = relationship("ChecklistItem", back_populates="checklist_completions")
    
    def __repr__(self):
        return f"<ChecklistCompletion {self.id} for Checklist {self.checklist_id}>"


class WeightRecord(db.Model):
    """Model for tracking pet weight over time"""
    __tablename__ = 'weight_records'
    
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, ForeignKey('pets.id', ondelete='CASCADE'), nullable=False)
    weight = db.Column(db.Float, nullable=False)  # Weight in kilograms
    record_date = db.Column(db.Date, nullable=False)
    record_time = db.Column(db.Time, nullable=False)
    volunteer_name = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    pet = relationship("Pet", back_populates="weight_records")
    
    def __repr__(self):
        return f"<WeightRecord {self.id} for Pet {self.pet_id}: {self.weight}kg>"


class EnhancedChecklistItem(db.Model):
    """Model for enhanced checklist items with specific types"""
    __tablename__ = 'enhanced_checklist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)  # medication, feeding, water, litter, etc.
    is_default = db.Column(db.Boolean, default=False)
    species_applicable = db.Column(db.String(50), nullable=True)
    options = db.Column(db.Text, nullable=True)  # JSON string of options for selection items
    unit = db.Column(db.String(20), nullable=True)  # e.g., ml, g, etc. for measurement items
    frequency = db.Column(db.String(50), nullable=True)  # daily, twice daily, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<EnhancedChecklistItem {self.description} ({self.item_type})>"


# Add the relationship after all classes are defined to avoid circular dependencies
Pet.weight_records = relationship("WeightRecord", back_populates="pet", cascade="all, delete-orphan")