from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def calculate_bmi(weight, height):
    """Calculate BMI and return status"""
    # weight in kg, height in cm
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        weight = float(data.get('weight'))
        height = float(data.get('height'))
        
        if weight <= 0 or height <= 0:
            return jsonify({"error": "Weight and height must be positive numbers"}), 400
        
        result = calculate_bmi(weight, height)
        return jsonify(result)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input. Please enter valid numbers."}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
