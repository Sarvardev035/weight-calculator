# BMI Calculator App

A simple Flask-based web application to calculate BMI (Body Mass Index) and determine fitness status based on weight and height.

## Features

- **Weight & Height Input**: Easy-to-use form for entering your measurements
- **BMI Calculation**: Automatically calculates BMI from weight (kg) and height (cm)
- **Fitness Status**: Shows fitness category:
  - **Underweight**: BMI < 18.5 (Blue)
  - **Normal Weight (Fit)**: BMI 18.5 - 24.9 (Green)
  - **Overweight**: BMI 25 - 29.9 (Orange)
  - **Obese**: BMI ≥ 30 (Red)
- **Visual Chart**: Interactive BMI chart with a pointer showing your BMI range
- **Responsive Design**: Works on desktop and mobile devices

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd weight-calculator
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Enter your weight (in kg) and height (in cm)** and click "Calculate BMI"

## Usage

- Enter your weight in **kilograms**
- Enter your height in **centimeters**
- Click the "Calculate BMI" button
- View your BMI value and fitness status immediately

## File Structure

```
weight-calculator/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── templates/
    └── index.html        # HTML template with styling and JavaScript
```

## Technical Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Modern gradient design with responsive layout

## Notes

- BMI categories follow standard WHO (World Health Organization) guidelines
- The app validates input to ensure positive numbers only
- Client-side and server-side validation for better user experience

Enjoy tracking your fitness! 💪
