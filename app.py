import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "pawpass-dev-key")

# Data storage path
PETS_DATA_FILE = os.path.join(os.path.dirname(__file__), 'static', 'data', 'pets.json')

# Ensure data directory exists
os.makedirs(os.path.dirname(PETS_DATA_FILE), exist_ok=True)

def load_pets():
    """Load pets data from JSON file"""
    try:
        if os.path.exists(PETS_DATA_FILE):
            with open(PETS_DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            # Create initial data if file doesn't exist
            initial_data = [
                {
                    "id": 1,
                    "name": "Luna",
                    "image": "https://images.unsplash.com/photo-1543852786-1cf6624b9987",
                    "species": "Cat",
                    "feeding_instructions": "Feed twice a day, morning and evening. 1/2 cup of dry food each meal.",
                    "medical_notes": "Allergy meds once daily in the morning. Pill can be hidden in treat.",
                    "behavior_notes": "Shy, hides at first but friendly once comfortable. Loves string toys.",
                    "updates": [
                        {"date": "2023-06-15", "time": "09:00", "note": "Fed at 9am. Hiding under bed."},
                        {"date": "2023-06-15", "time": "18:30", "note": "Took meds. Ate all food. Played for 10 minutes."}
                    ],
                    "checklists": [
                        {
                            "date": "2023-06-15",
                            "time": "18:00",
                            "fed": True,
                            "meds": True,
                            "water": True,
                            "playtime": True,
                            "notes": "All tasks completed"
                        }
                    ]
                },
                {
                    "id": 2,
                    "name": "Max",
                    "image": "https://images.unsplash.com/photo-1534351450181-ea9f78427fe8",
                    "species": "Dog",
                    "feeding_instructions": "Feed three times a day. 1 cup of kibble mixed with 1/4 can wet food.",
                    "medical_notes": "No current medications. Due for vaccines next month.",
                    "behavior_notes": "Very energetic. Needs at least 30 minutes of exercise daily. Good with other dogs.",
                    "updates": [
                        {"date": "2023-06-14", "time": "08:30", "note": "Morning walk for 20 minutes. Fed breakfast."},
                        {"date": "2023-06-14", "time": "17:00", "note": "Afternoon play session in yard. Very energetic today."}
                    ],
                    "checklists": [
                        {
                            "date": "2023-06-14",
                            "time": "21:00",
                            "fed": True,
                            "meds": False, 
                            "water": True,
                            "playtime": True,
                            "notes": "No meds needed"
                        }
                    ]
                },
                {
                    "id": 3,
                    "name": "Bella",
                    "image": "https://images.unsplash.com/photo-1537151608828-ea2b11777ee8",
                    "species": "Dog",
                    "feeding_instructions": "Feed twice daily. Special diet for sensitive stomach.",
                    "medical_notes": "Eye drops twice daily. Heart medication in the morning.",
                    "behavior_notes": "Senior dog, gentle and calm. Prefers short walks and lots of naps.",
                    "updates": [
                        {"date": "2023-06-15", "time": "10:00", "note": "Morning meds given. Ate about half her breakfast."},
                        {"date": "2023-06-15", "time": "15:30", "note": "Short walk around the block. Seems a bit tired today."}
                    ],
                    "checklists": [
                        {
                            "date": "2023-06-15",
                            "time": "20:00",
                            "fed": True,
                            "meds": True,
                            "water": True,
                            "playtime": False,
                            "notes": "Too tired for playtime today, extra rest recommended"
                        }
                    ]
                }
            ]
            save_pets(initial_data)
            return initial_data
    except Exception as e:
        logging.error(f"Error loading pets data: {e}")
        return []

def save_pets(pets_data):
    """Save pets data to JSON file"""
    try:
        with open(PETS_DATA_FILE, 'w') as f:
            json.dump(pets_data, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving pets data: {e}")

def get_pet_by_id(pet_id):
    """Get a pet by ID"""
    pets = load_pets()
    for pet in pets:
        if pet['id'] == int(pet_id):
            return pet
    return None

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
        # Sort updates by date and time, most recent first
        pet['updates'] = sorted(pet['updates'], 
                                key=lambda x: (x['date'], x['time']), 
                                reverse=True)
        return render_template('pet.html', pet=pet)
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
        update_note = request.form.get('update')
        if update_note:
            now = datetime.now()
            new_update = {
                "date": now.strftime('%Y-%m-%d'),
                "time": now.strftime('%H:%M'),
                "note": update_note
            }
            
            pets = load_pets()
            for p in pets:
                if p['id'] == pet_id:
                    p['updates'].append(new_update)
                    break
            
            save_pets(pets)
            flash('Update added successfully', 'success')
            return redirect(url_for('pet_profile', pet_id=pet_id))
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
    
    if request.method == 'POST':
        fed = 'fed' in request.form
        meds = 'meds' in request.form
        water = 'water' in request.form
        playtime = 'playtime' in request.form
        notes = request.form.get('notes', '')
        
        now = datetime.now()
        new_checklist = {
            "date": now.strftime('%Y-%m-%d'),
            "time": now.strftime('%H:%M'),
            "fed": fed,
            "meds": meds,
            "water": water,
            "playtime": playtime,
            "notes": notes
        }
        
        pets = load_pets()
        for p in pets:
            if p['id'] == pet_id:
                if 'checklists' not in p:
                    p['checklists'] = []
                p['checklists'].append(new_checklist)
                break
        
        save_pets(pets)
        flash('Checklist completed successfully', 'success')
        return redirect(url_for('pet_profile', pet_id=pet_id))
    
    return render_template('checklist.html', pet=pet)

# API Endpoints for JSON data (optional, for future use)
@app.route('/api/pets', methods=['GET'])
def api_get_pets():
    """API endpoint to get all pets"""
    return jsonify(load_pets())

@app.route('/api/pets/<int:pet_id>', methods=['GET'])
def api_get_pet(pet_id):
    """API endpoint to get a specific pet"""
    pet = get_pet_by_id(pet_id)
    if pet:
        return jsonify(pet)
    else:
        return jsonify({"error": "Pet not found"}), 404

@app.route('/api/pets/<int:pet_id>/update', methods=['POST'])
def api_add_update(pet_id):
    """API endpoint to add an update to a pet"""
    data = request.get_json()
    if not data or 'update' not in data:
        return jsonify({"error": "Missing update data"}), 400
    
    update_note = data['update']
    pet = get_pet_by_id(pet_id)
    if not pet:
        return jsonify({"error": "Pet not found"}), 404
    
    now = datetime.now()
    new_update = {
        "date": now.strftime('%Y-%m-%d'),
        "time": now.strftime('%H:%M'),
        "note": update_note
    }
    
    pets = load_pets()
    for p in pets:
        if p['id'] == pet_id:
            p['updates'].append(new_update)
            break
    
    save_pets(pets)
    return jsonify({"success": True, "update": new_update})

@app.route('/api/pets/<int:pet_id>/checklist', methods=['POST'])
def api_complete_checklist(pet_id):
    """API endpoint to complete a checklist for a pet"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing checklist data"}), 400
    
    pet = get_pet_by_id(pet_id)
    if not pet:
        return jsonify({"error": "Pet not found"}), 404
    
    fed = data.get('fed', False)
    meds = data.get('meds', False)
    water = data.get('water', False)
    playtime = data.get('playtime', False)
    notes = data.get('notes', '')
    
    now = datetime.now()
    new_checklist = {
        "date": now.strftime('%Y-%m-%d'),
        "time": now.strftime('%H:%M'),
        "fed": fed,
        "meds": meds,
        "water": water,
        "playtime": playtime,
        "notes": notes
    }
    
    pets = load_pets()
    for p in pets:
        if p['id'] == pet_id:
            if 'checklists' not in p:
                p['checklists'] = []
            p['checklists'].append(new_checklist)
            break
    
    save_pets(pets)
    return jsonify({"success": True, "checklist": new_checklist})

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
