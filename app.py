import os
import csv
import io
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///weights.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

class WeightEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    weight_kg = db.Column(db.Float, nullable=False)
    height_cm = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(200), nullable=True)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('entries', lazy=True))

# Helpers
def to_kg(weight, unit):
    unit = unit.lower() if unit else 'kg'
    if unit in ('kg', 'kilogram', 'kilograms'):
        return weight
    if unit in ('lb', 'lbs', 'pound', 'pounds'):
        return weight * 0.45359237
    raise ValueError('Unknown weight unit')

def to_cm(height, unit):
    unit = unit.lower() if unit else 'cm'
    if unit in ('cm', 'centimeter', 'centimeters'):
        return height
    if unit in ('in', 'inch', 'inches'):
        return height * 2.54
    raise ValueError('Unknown height unit')

def calculate_bmi(weight_kg, height_cm):
    """Calculate BMI and return status"""
    height_m = height_cm / 100
    if height_m <= 0:
        raise ValueError('Height must be positive')
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        status = "Underweight"
        color = "blue"
    elif 18.5 <= bmi < 25:
        status = "Normal Weight (Fit)"
        color = "green"
    elif 25 <= bmi < 30:
        status = "Overweight"
        color = "orange"
    else:
        status = "Obese"
        color = "red"
    
    return {
        "bmi": round(bmi, 2),
        "status": status,
        "color": color
    }

# Initialize DB
@app.before_first_request
def init_db():
    db.create_all()

# Routes
@app.route('/')
def index():
    user = session.get('username')
    return render_template('index.html', username=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            flash('Please enter a username')
            return redirect(url_for('login'))
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        session['username'] = user.username
        session['user_id'] = user.id
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json or request.form
        weight = float(data.get('weight'))
        height = float(data.get('height'))
        unit = data.get('weight_unit', 'kg')
        height_unit = data.get('height_unit', 'cm')
        save = data.get('save', False)

        if weight <= 0 or height <= 0:
            return jsonify({"error": "Weight and height must be positive numbers"}), 400

        weight_kg = to_kg(weight, unit)
        height_cm = to_cm(height, height_unit)

        result = calculate_bmi(weight_kg, height_cm)

        # optional save
        if save:
            user_id = session.get('user_id')
            entry = WeightEntry(user_id=user_id, weight_kg=weight_kg, height_cm=height_cm)
            db.session.add(entry)
            db.session.commit()

        return jsonify(result)
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400

@app.route('/submit', methods=['POST'])
def submit():
    # Form submission - save entry and redirect to history
    try:
        weight = float(request.form.get('weight'))
        height = float(request.form.get('height'))
        unit = request.form.get('weight_unit', 'kg')
        height_unit = request.form.get('height_unit', 'cm')
        note = request.form.get('note')

        weight_kg = to_kg(weight, unit)
        height_cm = to_cm(height, height_unit)

        user_id = session.get('user_id')
        entry = WeightEntry(user_id=user_id, weight_kg=weight_kg, height_cm=height_cm, note=note)
        db.session.add(entry)
        db.session.commit()

        flash('Entry saved')
        return redirect(url_for('history'))
    except Exception as e:
        flash(str(e))
        return redirect(url_for('index'))

@app.route('/history')
def history():
    user_id = session.get('user_id')
    if user_id:
        entries = WeightEntry.query.filter_by(user_id=user_id).order_by(WeightEntry.recorded_at.asc()).all()
    else:
        entries = WeightEntry.query.order_by(WeightEntry.recorded_at.asc()).all()

    data = [{
        'id': e.id,
        'weight_kg': e.weight_kg,
        'height_cm': e.height_cm,
        'bmi': calculate_bmi(e.weight_kg, e.height_cm)['bmi'],
        'recorded_at': e.recorded_at.isoformat(),
        'note': e.note
    } for e in entries]

    return render_template('history.html', entries=data, username=session.get('username'))

@app.route('/export')
def export_csv():
    user_id = session.get('user_id')
    if user_id:
        entries = WeightEntry.query.filter_by(user_id=user_id).order_by(WeightEntry.recorded_at.asc()).all()
    else:
        entries = WeightEntry.query.order_by(WeightEntry.recorded_at.asc()).all()

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['id', 'weight_kg', 'height_cm', 'bmi', 'recorded_at', 'note'])
    for e in entries:
        bmi = calculate_bmi(e.weight_kg, e.height_cm)['bmi']
        cw.writerow([e.id, f"{e.weight_kg:.2f}", f"{e.height_cm:.1f}", f"{bmi:.2f}", e.recorded_at.isoformat(), e.note or ''])

    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)

    return send_file(output, as_attachment=True, download_name='weights.csv', mimetype='text/csv')

if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT', 5000)))
