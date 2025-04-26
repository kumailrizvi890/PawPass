import os
import json
import logging
from datetime import datetime, date, time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "pawpass-dev-key")

# Configure database
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    logging.info(f"Database configuration loaded: {database_url[:20]}...")
else:
    logging.error("DATABASE_URL environment variable not found")

# Initialize database
from models import db, Pet, PetUpdate, Checklist, ChecklistItem, ChecklistCompletion
db.init_app(app)

# Create all tables
with app.app_context():
    db.create_all()
    
    # Add default checklist items if none exist
    if ChecklistItem.query.count() == 0:
        default_items = [
            ChecklistItem(description="Fed the pet", is_default=True),
            ChecklistItem(description="Gave medication", is_default=True),
            ChecklistItem(description="Refreshed water", is_default=True),
            ChecklistItem(description="Provided playtime/exercise", is_default=True),
            ChecklistItem(description="Cleaned litter box/living area", is_default=True)
        ]
        for item in default_items:
            db.session.add(item)
        db.session.commit()

# Data storage path (for migration/fallback)
PETS_DATA_FILE = os.path.join(os.path.dirname(__file__), 'static', 'data', 'pets.json')

# Ensure data directory exists
os.makedirs(os.path.dirname(PETS_DATA_FILE), exist_ok=True)

# Helper functions to migrate from JSON to database
def migrate_data_to_db():
    """Migrate JSON data to database if needed"""
    # Only migrate if the database is empty and JSON file exists
    if Pet.query.count() == 0 and os.path.exists(PETS_DATA_FILE):
        try:
            # Load JSON data
            with open(PETS_DATA_FILE, 'r') as f:
                pets_data = json.load(f)
            
            # Create Pet objects from JSON data
            for pet_data in pets_data:
                # Create pet
                pet = Pet(
                    name=pet_data['name'],
                    species=pet_data['species'],
                    description=pet_data.get('behavior_notes', ''),
                    image_url=pet_data.get('image', ''),
                    is_emergency=False
                )
                db.session.add(pet)
                db.session.flush()  # To get the pet ID
                
                # Add updates
                for update in pet_data.get('updates', []):
                    update_date = datetime.strptime(update['date'], '%Y-%m-%d').date()
                    update_time = datetime.strptime(update['time'], '%H:%M').time()
                    pet_update = PetUpdate(
                        pet_id=pet.id,
                        update_text=update['note'],
                        update_date=update_date,
                        update_time=update_time
                    )
                    db.session.add(pet_update)
                
                # Add checklists
                for checklist_data in pet_data.get('checklists', []):
                    check_date = datetime.strptime(checklist_data['date'], '%Y-%m-%d').date()
                    check_time = datetime.strptime(checklist_data['time'], '%H:%M').time()
                    
                    checklist = Checklist(
                        pet_id=pet.id,
                        completion_date=check_date,
                        completion_time=check_time,
                        notes=checklist_data.get('notes', '')
                    )
                    db.session.add(checklist)
                    db.session.flush()  # To get the checklist ID
                    
                    # Add checklist items
                    checklist_items = ChecklistItem.query.filter_by(is_default=True).all()
                    for item in checklist_items:
                        is_completed = False
                        if 'fed' in item.description.lower() and checklist_data.get('fed'):
                            is_completed = True
                        elif 'medication' in item.description.lower() and checklist_data.get('meds'):
                            is_completed = True
                        elif 'water' in item.description.lower() and checklist_data.get('water'):
                            is_completed = True
                        elif 'play' in item.description.lower() and checklist_data.get('playtime'):
                            is_completed = True
                        
                        completion = ChecklistCompletion(
                            checklist_id=checklist.id,
                            checklist_item_id=item.id,
                            completed=is_completed
                        )
                        db.session.add(completion)
            
            db.session.commit()
            logging.info("Successfully migrated JSON data to database")
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error migrating data to database: {e}")

def load_pets():
    """Load all pets from the database"""
    try:
        return Pet.query.all()
    except Exception as e:
        logging.error(f"Error loading pets from database: {e}")
        return []

def get_pet_by_id(pet_id):
    """Get a pet by ID from the database"""
    try:
        return Pet.query.get(pet_id)
    except Exception as e:
        logging.error(f"Error getting pet by ID: {e}")
        return None

# Try to migrate data from JSON to database if needed
with app.app_context():
    migrate_data_to_db()

# Routes
@app.route('/')
def index():
    """Home page - displays list of all pets"""
    pets = load_pets()
    return render_template('index.html', pets=pets)

@app.route('/pet/<int:pet_id>')
def pet_profile(pet_id):
    """Pet profile page"""
    pet = get_pet_by_id(pet_id)
    if pet:
        # Get the pet's updates, sorted by date and time (most recent first)
        pet_updates = PetUpdate.query.filter_by(pet_id=pet.id)\
            .order_by(PetUpdate.update_date.desc(), PetUpdate.update_time.desc()).all()
        
        # Get pet's checklists, sorted by date and time (most recent first)
        pet_checklists = Checklist.query.filter_by(pet_id=pet.id)\
            .order_by(Checklist.completion_date.desc(), Checklist.completion_time.desc()).all()
        
        return render_template('pet.html', pet=pet, updates=pet_updates, checklists=pet_checklists)
    else:
        flash('Pet not found', 'error')
        return redirect(url_for('index'))

@app.route('/pet/<int:pet_id>/update', methods=['GET', 'POST'])
def add_update(pet_id):
    """Add update page"""
    pet = get_pet_by_id(pet_id)
    if not pet:
        flash('Pet not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        update_text = request.form.get('update')
        if update_text:
            now = datetime.now()
            
            # Create and save a new update
            new_update = PetUpdate(
                pet_id=pet.id,
                update_text=update_text,
                update_date=now.date(),
                update_time=now.time(),
                volunteer_name=request.form.get('volunteer_name', '')
            )
            
            try:
                db.session.add(new_update)
                db.session.commit()
                flash('Update added successfully', 'success')
                return redirect(url_for('pet_profile', pet_id=pet_id))
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error adding update: {e}")
                flash('Error adding update. Please try again.', 'error')
        else:
            flash('Update cannot be empty', 'error')
    
    return render_template('update.html', pet=pet)

@app.route('/pet/<int:pet_id>/checklist', methods=['GET', 'POST'])
def complete_checklist(pet_id):
    """Complete shift checklist page"""
    pet = get_pet_by_id(pet_id)
    if not pet:
        flash('Pet not found', 'error')
        return redirect(url_for('index'))
    
    # Get checklist items
    checklist_items = ChecklistItem.query.all()
    
    if request.method == 'POST':
        notes = request.form.get('notes', '')
        volunteer_name = request.form.get('volunteer_name', '')
        now = datetime.now()
        
        # Create the checklist
        checklist = Checklist(
            pet_id=pet.id,
            volunteer_name=volunteer_name,
            completion_date=now.date(),
            completion_time=now.time(),
            notes=notes
        )
        
        try:
            db.session.add(checklist)
            db.session.flush()  # Get the checklist ID
            
            # Add checklist completions based on form data
            for item in checklist_items:
                is_completed = str(item.id) in request.form.getlist('items')
                completion = ChecklistCompletion(
                    checklist_id=checklist.id,
                    checklist_item_id=item.id,
                    completed=is_completed
                )
                db.session.add(completion)
            
            db.session.commit()
            flash('Checklist completed successfully', 'success')
            return redirect(url_for('pet_profile', pet_id=pet_id))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error completing checklist: {e}")
            flash('Error saving checklist. Please try again.', 'error')
    
    return render_template('checklist.html', pet=pet, checklist_items=checklist_items)

# Helper function to serialize a Pet object to JSON
def pet_to_json(pet):
    """Convert a Pet object to a JSON-serializable dictionary"""
    # Get pet updates
    updates = []
    for update in PetUpdate.query.filter_by(pet_id=pet.id).order_by(PetUpdate.created_at.desc()).all():
        updates.append({
            "id": update.id,
            "date": update.update_date.strftime('%Y-%m-%d'),
            "time": update.update_time.strftime('%H:%M'),
            "note": update.update_text,
            "volunteer": update.volunteer_name
        })
    
    # Get pet checklists with completed items
    checklists = []
    for checklist in Checklist.query.filter_by(pet_id=pet.id).order_by(Checklist.created_at.desc()).all():
        # Get the completed items for this checklist
        completed_items = []
        for completion in ChecklistCompletion.query.filter_by(checklist_id=checklist.id).all():
            if completion.completed:
                item = ChecklistItem.query.get(completion.checklist_item_id)
                completed_items.append({
                    "id": item.id,
                    "description": item.description
                })
        
        checklists.append({
            "id": checklist.id,
            "date": checklist.completion_date.strftime('%Y-%m-%d'),
            "time": checklist.completion_time.strftime('%H:%M'),
            "notes": checklist.notes,
            "volunteer": checklist.volunteer_name,
            "completed_items": completed_items
        })
    
    return {
        "id": pet.id,
        "name": pet.name,
        "species": pet.species,
        "breed": pet.breed,
        "age": pet.age,
        "gender": pet.gender,
        "description": pet.description,
        "image_url": pet.image_url,
        "is_emergency": pet.is_emergency,
        "updates": updates,
        "checklists": checklists
    }

# API Endpoints
@app.route('/api/pets', methods=['GET'])
def api_get_pets():
    """API endpoint to get all pets"""
    pets = []
    for pet in Pet.query.all():
        pets.append(pet_to_json(pet))
    return jsonify(pets)

@app.route('/api/pets/<int:pet_id>', methods=['GET'])
def api_get_pet(pet_id):
    """API endpoint to get a specific pet"""
    pet = Pet.query.get(pet_id)
    if pet:
        return jsonify(pet_to_json(pet))
    else:
        return jsonify({"error": "Pet not found"}), 404

@app.route('/api/pets/<int:pet_id>/update', methods=['POST'])
def api_add_update(pet_id):
    """API endpoint to add an update to a pet"""
    data = request.get_json()
    if not data or 'update' not in data:
        return jsonify({"error": "Missing update data"}), 400
    
    update_text = data['update']
    volunteer_name = data.get('volunteer_name', '')
    
    pet = Pet.query.get(pet_id)
    if not pet:
        return jsonify({"error": "Pet not found"}), 404
    
    try:
        now = datetime.now()
        new_update = PetUpdate(
            pet_id=pet.id,
            update_text=update_text,
            update_date=now.date(),
            update_time=now.time(),
            volunteer_name=volunteer_name
        )
        
        db.session.add(new_update)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "update": {
                "id": new_update.id,
                "date": new_update.update_date.strftime('%Y-%m-%d'),
                "time": new_update.update_time.strftime('%H:%M'),
                "note": new_update.update_text,
                "volunteer": new_update.volunteer_name
            }
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding update via API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/pets/<int:pet_id>/checklist', methods=['POST'])
def api_complete_checklist(pet_id):
    """API endpoint to complete a checklist for a pet"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing checklist data"}), 400
    
    pet = Pet.query.get(pet_id)
    if not pet:
        return jsonify({"error": "Pet not found"}), 404
    
    notes = data.get('notes', '')
    volunteer_name = data.get('volunteer_name', '')
    completed_items = data.get('completed_items', [])
    
    try:
        now = datetime.now()
        checklist = Checklist(
            pet_id=pet.id,
            volunteer_name=volunteer_name,
            completion_date=now.date(),
            completion_time=now.time(),
            notes=notes
        )
        
        db.session.add(checklist)
        db.session.flush()  # Get the checklist ID
        
        # Add checklist completions
        for item_id in completed_items:
            # Verify item exists
            item = ChecklistItem.query.get(item_id)
            if item:
                completion = ChecklistCompletion(
                    checklist_id=checklist.id,
                    checklist_item_id=item.id,
                    completed=True
                )
                db.session.add(completion)
        
        db.session.commit()
        
        # Return the created checklist data
        items = []
        for completion in ChecklistCompletion.query.filter_by(checklist_id=checklist.id).all():
            if completion.completed:
                item = ChecklistItem.query.get(completion.checklist_item_id)
                items.append({
                    "id": item.id,
                    "description": item.description
                })
        
        return jsonify({
            "success": True, 
            "checklist": {
                "id": checklist.id,
                "date": checklist.completion_date.strftime('%Y-%m-%d'),
                "time": checklist.completion_time.strftime('%H:%M'),
                "notes": checklist.notes,
                "volunteer": checklist.volunteer_name,
                "completed_items": items
            }
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding checklist via API: {e}")
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', error="404 - Page Not Found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('base.html', error="500 - Server Error"), 500

# Initialize the data file if it doesn't exist
load_pets()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
