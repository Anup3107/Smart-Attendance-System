from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# Ensure attendance.csv exists
if not os.path.exists('attendance.csv'):
    with open('attendance.csv', 'w') as f:
        f.write('StudentID,Name,Date,Time,Emotion\n')

# Ensure student.csv exists
if not os.path.exists('student.csv'):
    with open('student.csv', 'w') as f:
        f.write('StudentID,Name\n')  # empty template

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/scanner')
def scanner():
    return render_template('scanner.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    qr_data = data.get("qr_data", "")
    lines = qr_data.strip().split('\n')
    details = {}
    for line in lines:
        parts = line.split(':', 1)
        if len(parts) == 2:
            details[parts[0].strip()] = parts[1].strip()

    student_id = details.get("StudentID")
    name = details.get("Name", "N/A")

    if not student_id:
        return jsonify({"status": "error", "message": "Invalid QR data"})

    today = datetime.now().strftime('%d-%m-%Y')
    df = pd.read_csv('attendance.csv')

    # Mark attendance only once per day
    if not ((df['StudentID'] == int(student_id)) & (df['Date'] == today)).any():
        with open('attendance.csv', 'a') as f:
            f.write(f"{student_id},{name},{today},{datetime.now().strftime('%H:%M:%S')},\n")
        return jsonify({"status": "success", "message": f"Attendance marked for {name}"})
    else:
        return jsonify({"status": "exists", "message": "Already marked today"})

@app.route('/attendance_data')
def attendance_data():
    df = pd.read_csv('attendance.csv')
    return jsonify(df.to_dict(orient='records'))

@app.route('/students_data')
def students_data():
    """Show all students and their attendance status"""
    students_df = pd.read_csv('student.csv')
    attendance_df = pd.read_csv('attendance.csv')
    today = datetime.now().strftime('%d-%m-%Y')

    # Find IDs present today
    attendance_today = attendance_df[attendance_df['Date'] == today]['StudentID'].tolist()
    students_df['Status'] = students_df['StudentID'].apply(
        lambda x: 'Present' if int(x) in attendance_today else 'Absent'
    )

    return jsonify(students_df.to_dict(orient='records'))

@app.route('/download_csv')
def download_csv():
    return send_file('attendance.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
