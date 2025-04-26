import os
import json
import logging
import uuid
from datetime import datetime, date, time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from PIL import Image

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "pawpass-dev-key")

# Configure upload folders
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload size

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
        with app.app_context():
            return Pet.query.all()
    except Exception as e:
        logging.error(f"Error loading pets from database: {e}")
        return []

def get_pet_by_id(pet_id):
    """Get a pet by ID from the database"""
    try:
        with app.app_context():
            return Pet.query.get(pet_id)
    except Exception as e:
        logging.error(f"Error getting pet by ID: {e}")
        return None

# Helper function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to save uploaded image and return the file path
def save_pet_image(file):
    """Save uploaded pet image and return the file path"""
    if file and allowed_file(file.filename):
        try:
            # Generate a unique filename with UUID to prevent overwriting
            original_filename = secure_filename(file.filename)
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            
            # Ensure upload folder exists
            upload_dir = os.path.join('static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Full path to save the file (relative to the app root)
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Save the original file
            file.save(file_path)
            logging.info(f"Saved image to {file_path}")
            
            # Create a thumbnail version (optional for performance)
            try:
                with Image.open(file_path) as img:
                    # Keep aspect ratio, max dimension 800px
                    img.thumbnail((800, 800))
                    img.save(file_path)
                    logging.info(f"Created thumbnail for {file_path}")
            except Exception as e:
                logging.error(f"Error creating thumbnail: {e}")
            
            # Return the relative path for storage in the database WITH leading slash
            relative_path = f"/uploads/{unique_filename}"
            logging.info(f"Returning image path: {relative_path}")
            return relative_path
        except Exception as e:
            logging.error(f"Error saving pet image: {e}")
            
    return None

# Try to migrate data from JSON to database if needed
with app.app_context():
    migrate_data_to_db()

# Routes
@app.route('/')
def index():
    """Home page - displays list of all pets"""
    search_query = request.args.get('search', '').strip()
    
    with app.app_context():
        if search_query:
            # Search for pets by name
            pets = Pet.query.filter(Pet.name.ilike(f'%{search_query}%')).all()
        else:
            # Get all pets
            pets = Pet.query.all()
    
    return render_template('index.html', pets=pets)

@app.route('/pet/<int:pet_id>')
def pet_profile(pet_id):
    """Pet profile page"""
    pet = get_pet_by_id(pet_id)
    if pet:
        # Get the pet's updates, sorted by date and time (most recent first)
        with app.app_context():
            pet_updates = PetUpdate.query.filter_by(pet_id=pet.id)\
                .order_by(PetUpdate.update_date.desc(), PetUpdate.update_time.desc()).all()
            
            # Get pet's checklists, sorted by date and time (most recent first)
            pet_checklists = Checklist.query.filter_by(pet_id=pet.id)\
                .order_by(Checklist.completion_date.desc(), Checklist.completion_time.desc()).all()
            
            # Get completed items for each checklist
            for checklist in pet_checklists:
                checklist.completed_items = []
                completions = ChecklistCompletion.query.filter_by(checklist_id=checklist.id, completed=True).all()
                for completion in completions:
                    item = ChecklistItem.query.get(completion.checklist_item_id)
                    if item:
                        checklist.completed_items.append(item)
        
        return render_template('pet.html', pet=pet, updates=pet_updates, checklists=pet_checklists)
    else:
        flash('Pet not found', 'error')
        return redirect(url_for('index'))

@app.route('/pet/<int:pet_id>/edit', methods=['GET', 'POST'])
def edit_pet(pet_id):
    """Edit pet information"""
    logging.info(f"Editing pet with ID: {pet_id}")
    
    with app.app_context():
        # Get the pet by ID directly
        pet = Pet.query.get(pet_id)
        
        if not pet:
            flash('Pet not found ❌', 'error')
            return redirect(url_for('index'))
        
        pet_name = pet.name
        logging.info(f"Found pet: {pet_name} (ID: {pet_id}) for editing")
    
        if request.method == 'POST':
            # Get form data
            name = request.form.get('name')
            species = request.form.get('species')
            breed = request.form.get('breed', '')
            age = request.form.get('age', None)
            gender = request.form.get('gender', '')
            description = request.form.get('description', '')
            is_emergency = 'is_emergency' in request.form
            
            logging.info(f"Form data: name={name}, species={species}, breed={breed}, age={age}, gender={gender}, is_emergency={is_emergency}")
            
            # Validate required fields
            if not name or not species:
                flash('Name and species are required ❌', 'error')
                return render_template('edit_pet.html', pet=pet)
            
            # Convert age to integer if provided
            if age:
                try:
                    age = int(age)
                except ValueError:
                    age = None
            
            # Process image upload
            image_url = pet.image_url
            if 'image' in request.files:
                file = request.files['image']
                if file.filename:
                    logging.info(f"Processing uploaded image for {pet_name}: {file.filename}")
                    
                    # Save the image and get the relative path
                    relative_path = save_pet_image(file)
                    
                    # Set image URL for the database
                    if relative_path:
                        image_url = relative_path
                        logging.info(f"New image URL for {pet_name}: {image_url}")
            
            try:
                # Update pet information
                pet.name = name
                pet.species = species
                pet.breed = breed
                pet.age = age
                pet.gender = gender
                pet.description = description
                pet.image_url = image_url
                pet.is_emergency = is_emergency
                pet.updated_at = datetime.utcnow()
                
                db.session.commit()
                
                # Success message with emoji
                flash(f'Pet {name} has been updated successfully 🐾✨', 'success')
                logging.info(f"Pet updated: {name} (ID: {pet_id}, Image: {image_url})")
                return redirect(url_for('pet_profile', pet_id=pet_id))
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error updating pet: {e}")
                flash(f'Error updating pet {pet_name}. Please try again. ❌', 'error')
    
        # GET request - show the form with pet data
        return render_template('edit_pet.html', pet=pet)

@app.route('/pet/<int:pet_id>/delete', methods=['POST'])
def delete_pet(pet_id):
    """Delete a pet"""
    logging.info(f"Deleting pet with ID: {pet_id}")
    
    with app.app_context():
        # Get the pet by ID directly
        pet = Pet.query.get(pet_id)
        
        if not pet:
            flash('Pet not found ❌', 'error')
            return redirect(url_for('index'))
        
        pet_name = pet.name
        logging.info(f"Found pet: {pet_name} (ID: {pet_id})")
        
        try:
            # Delete pet updates
            update_count = PetUpdate.query.filter_by(pet_id=pet.id).delete()
            logging.info(f"Deleted {update_count} updates for pet {pet_name}")
            
            # Get all checklists for this pet
            checklists = Checklist.query.filter_by(pet_id=pet.id).all()
            
            # Delete checklist completions for each checklist
            for checklist in checklists:
                completion_count = ChecklistCompletion.query.filter_by(checklist_id=checklist.id).delete()
                logging.info(f"Deleted {completion_count} checklist completions for checklist {checklist.id}")
            
            # Delete checklists
            checklist_count = Checklist.query.filter_by(pet_id=pet.id).delete()
            logging.info(f"Deleted {checklist_count} checklists for pet {pet_name}")
            
            # Delete the pet
            db.session.delete(pet)
            db.session.commit()
            
            # Success message with emoji
            flash(f'Pet {pet_name} has been deleted successfully 🐾✨', 'success')
            logging.info(f"Pet {pet_name} (ID: {pet_id}) successfully deleted")
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting pet: {e}")
            flash(f'Error deleting pet {pet_name}. Please try again. ❌', 'error')
    
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
            with app.app_context():
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

@app.route('/add-pet', methods=['GET', 'POST'])
def add_pet():
    """Add a new pet page"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        species = request.form.get('species')
        breed = request.form.get('breed', '')
        age = request.form.get('age', None)
        gender = request.form.get('gender', '')
        description = request.form.get('description', '')
        is_emergency = 'is_emergency' in request.form
        
        # Validate required fields
        if not name or not species:
            flash('Name and species are required ❌', 'error')
            return render_template('add_pet.html')
        
        # Convert age to integer if provided
        if age:
            try:
                age = int(age)
            except ValueError:
                age = None
        
        # Process image upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                logging.info(f"Processing uploaded image: {file.filename}")
                
                # Save the image and get the relative path
                relative_path = save_pet_image(file)
                
                # Set image URL for the database
                if relative_path:
                    image_url = relative_path
                    logging.info(f"Image URL to save in database: {image_url}")
        
        # Create and save the new pet
        with app.app_context():
            try:
                pet = Pet(
                    name=name,
                    species=species,
                    breed=breed,
                    age=age,
                    gender=gender,
                    description=description,
                    image_url=image_url,
                    is_emergency=is_emergency
                )
                
                db.session.add(pet)
                db.session.commit()
                
                # Success message with emoji
                flash(f'Pet {name} added successfully 🐾✨', 'success')
                logging.info(f"New pet added: {name} (ID: {pet.id}, Image: {image_url})")
                return redirect(url_for('pet_profile', pet_id=pet.id))
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error adding pet: {e}")
                flash('Error adding pet. Please try again. ❌', 'error')
    
    # GET request - show the form
    return render_template('add_pet.html')

@app.route('/pet/<int:pet_id>/checklist', methods=['GET', 'POST'])
def complete_checklist(pet_id):
    """Complete shift checklist page"""
    pet = get_pet_by_id(pet_id)
    if not pet:
        flash('Pet not found', 'error')
        return redirect(url_for('index'))
    
    # Get checklist items
    with app.app_context():
        checklist_items = ChecklistItem.query.all()
    
    if request.method == 'POST':
        notes = request.form.get('notes', '')
        volunteer_name = request.form.get('volunteer_name', '')
        now = datetime.now()
        
        with app.app_context():
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
    with app.app_context():
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
    with app.app_context():
        pets = []
        for pet in Pet.query.all():
            pets.append(pet_to_json(pet))
        return jsonify(pets)

@app.route('/api/pets/<int:pet_id>', methods=['GET'])
def api_get_pet(pet_id):
    """API endpoint to get a specific pet"""
    with app.app_context():
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
    
    with app.app_context():
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
    
    with app.app_context():
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
