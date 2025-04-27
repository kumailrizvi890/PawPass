"""
Enhanced features for PawPass including weight tracking and AI functionality
"""
import logging
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Pet, WeightRecord, EnhancedChecklistItem
import app_utils

# Setup logging
logger = logging.getLogger(__name__)

# Create a Flask Blueprint
enhanced_features = Blueprint('enhanced_features', __name__)

@enhanced_features.route('/pet/<int:pet_id>/weight', methods=['GET'])
def weight_tracker(pet_id):
    """Weight tracker page for a pet"""
    from app import get_pet_by_id
    pet = get_pet_by_id(pet_id)
    if not pet:
        flash('Pet not found', 'error')
        return redirect(url_for('index'))
    
    # Get weight records
    weight_records = WeightRecord.query.filter_by(pet_id=pet.id)\
        .order_by(WeightRecord.record_date.desc(), WeightRecord.record_time.desc()).all()
    
    # Prepare data for chart
    weight_dates = [record.record_date.strftime('%Y-%m-%d') for record in weight_records]
    weight_values = [float(record.weight) for record in weight_records]
    
    # Get AI analysis if we have enough data
    weight_analysis = None
    if len(weight_records) >= 2:
        weight_analysis = app_utils.analyze_weight_trend(pet)
        if 'error' in weight_analysis:
            weight_analysis = None

    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('weight_tracker.html', pet=pet, weight_records=weight_records, 
                           weight_dates=weight_dates, weight_values=weight_values, 
                           weight_analysis=weight_analysis, today=today)

@enhanced_features.route('/pet/<int:pet_id>/weight/add', methods=['POST'])
def add_weight_record(pet_id):
    """Add a weight record for a pet"""
    from app import get_pet_by_id
    pet = get_pet_by_id(pet_id)
    if not pet:
        flash('Pet not found', 'error')
        return redirect(url_for('index'))
    
    try:
        # Get form data
        weight = request.form.get('weight')
        record_date = request.form.get('record_date')
        volunteer_name = request.form.get('volunteer_name', '')
        notes = request.form.get('notes', '')
        
        # Validate weight
        try:
            weight = float(weight)
            if weight <= 0:
                raise ValueError("Weight must be greater than zero")
        except (ValueError, TypeError):
            flash('Please enter a valid weight', 'error')
            return redirect(url_for('enhanced_features.weight_tracker', pet_id=pet_id))
        
        # Parse date
        try:
            record_date = datetime.strptime(record_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Please enter a valid date', 'error')
            return redirect(url_for('enhanced_features.weight_tracker', pet_id=pet_id))
        
        # Create and save weight record
        record = WeightRecord(
            pet_id=pet.id,
            weight=weight,
            record_date=record_date,
            record_time=datetime.now().time(),
            volunteer_name=volunteer_name,
            notes=notes
        )
        db.session.add(record)
        db.session.commit()
        
        flash(f'Weight record added for {pet.name}: {weight}kg', 'success')
        logger.info(f"Added weight record for pet {pet.id}: {weight}kg")
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding weight record: {e}")
        flash('Error adding weight record. Please try again.', 'error')
    
    return redirect(url_for('enhanced_features.weight_tracker', pet_id=pet_id))

@enhanced_features.route('/pet/<int:pet_id>/weight/<int:record_id>/delete', methods=['POST'])
def delete_weight_record(pet_id, record_id):
    """Delete a weight record"""
    from app import get_pet_by_id
    pet = get_pet_by_id(pet_id)
    if not pet:
        flash('Pet not found', 'error')
        return redirect(url_for('index'))
    
    # Get the record
    record = WeightRecord.query.get(record_id)
    if not record or record.pet_id != pet_id:
        flash('Weight record not found', 'error')
        return redirect(url_for('enhanced_features.weight_tracker', pet_id=pet_id))
    
    try:
        # Delete the record
        db.session.delete(record)
        db.session.commit()
        flash('Weight record deleted successfully', 'success')
        logger.info(f"Deleted weight record {record_id} for pet {pet_id}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting weight record: {e}")
        flash('Error deleting weight record. Please try again.', 'error')
    
    return redirect(url_for('enhanced_features.weight_tracker', pet_id=pet_id))

@enhanced_features.route('/pet/<int:pet_id>/ai-summary')
def ai_summary(pet_id):
    """Get AI summary for a pet"""
    from app import get_pet_by_id
    pet = get_pet_by_id(pet_id)
    if not pet:
        flash('Pet not found', 'error')
        return redirect(url_for('index'))
    
    days = int(request.args.get('days', 7))
    
    summary = app_utils.generate_ai_summary(pet, days)
    
    return jsonify(summary)

@enhanced_features.route('/pet/<int:pet_id>/care-instructions')
def care_instructions(pet_id):
    """Get care instructions for a pet"""
    from app import get_pet_by_id
    pet = get_pet_by_id(pet_id)
    if not pet:
        flash('Pet not found', 'error')
        return redirect(url_for('index'))
    
    care_type = request.args.get('care_type', 'general')
    
    instructions = app_utils.get_pet_care_instructions(pet.species, care_type)
    
    return jsonify(instructions)

@enhanced_features.route('/pet/<int:pet_id>/enhanced-checklist', methods=['GET', 'POST'])
def enhanced_checklist(pet_id):
    """Enhanced checklist page with clickable buttons and more options"""
    from app import get_pet_by_id
    from datetime import datetime
    from models import Checklist, ChecklistCompletion
    
    pet = get_pet_by_id(pet_id)
    if not pet:
        flash('Pet not found', 'error')
        return redirect(url_for('index'))
    
    # Get items applicable to this pet's species
    checklist_items = EnhancedChecklistItem.query.filter(
        db.or_(
            EnhancedChecklistItem.species_applicable == None,
            EnhancedChecklistItem.species_applicable == pet.species.lower()
        )
    ).order_by(EnhancedChecklistItem.item_type, EnhancedChecklistItem.description).all()
    
    # Group items by type
    grouped_items = {}
    for item in checklist_items:
        if item.item_type not in grouped_items:
            grouped_items[item.item_type] = []
        
        # Parse options if available
        item.parsed_options = []
        if item.options:
            try:
                item.parsed_options = json.loads(item.options)
            except json.JSONDecodeError:
                item.parsed_options = []
        
        grouped_items[item.item_type].append(item)
    
    # For POST request, handle form submission
    if request.method == 'POST':
        try:
            # Get form data
            volunteer_name = request.form.get('volunteer_name', '')
            general_notes = request.form.get('general_notes', '')
            
            # Get Pacific Time
            from datetime import datetime, timedelta
            import pytz
            pacific_tz = pytz.timezone('America/Los_Angeles')
            now_utc = datetime.utcnow()
            now_pacific = now_utc.replace(tzinfo=pytz.utc).astimezone(pacific_tz)
            
            # Create the checklist record
            checklist = Checklist(
                pet_id=pet.id,
                volunteer_name=volunteer_name,
                completion_date=now_pacific.date(),
                completion_time=now_pacific.time(),
                notes=general_notes
            )
            db.session.add(checklist)
            db.session.flush()  # To get the checklist ID
            
            # Process completed items
            completed_count = 0
            for key, value in request.form.items():
                if key.startswith('item_') and value.strip():
                    item_id = int(key.split('_')[1])
                    item_value = value.strip()
                    item_notes = request.form.get(f'notes_{item_id}', '')
                    measurement = request.form.get(f'measurement_{item_id}', '')
                    
                    # Combine value and measurement if present
                    if measurement:
                        item_value = f"{item_value} - {measurement}"
                    
                    # Create checklist completion
                    completion = ChecklistCompletion(
                        checklist_id=checklist.id,
                        checklist_item_id=item_id,
                        completed=True,
                        value=item_value,
                        notes=item_notes
                    )
                    db.session.add(completion)
                    completed_count += 1
            
            # Commit the transaction
            db.session.commit()
            
            # Success message
            flash(f'Enhanced checklist completed with {completed_count} items for {pet.name}!', 'success')
            return redirect(url_for('pet_profile', pet_id=pet_id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error completing enhanced checklist: {e}")
            flash('Error completing checklist. Please try again.', 'error')
    
    return render_template('enhanced_checklist.html', pet=pet, grouped_items=grouped_items)