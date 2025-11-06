import cv2
import pandas as pd
from datetime import datetime
import time
import os

# ========== Step 1: CSV File Setup ==========
if not os.path.exists('attendance.csv'):
    with open('attendance.csv', 'w', newline='') as f:
        f.write('StudentID,Name,Date,Time,Emotion\n')

# ========== Step 2: Webcam Start ==========
cap = cv2.VideoCapture(0)

# Aaj ki date
today_date = datetime.now().strftime('%d-%m-%Y')

# Already marked student IDs ko store karne ke liye
already_marked_ids = set()

# ========== Step 3: Load today's attendance ==========
def load_todays_marked_ids():
    try:
        df_att = pd.read_csv('attendance.csv')
        todays_entries = df_att[df_att['Date'] == today_date]
        return set(todays_entries['StudentID'].astype(str))
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return set()

already_marked_ids = load_todays_marked_ids()
print(f"Aaj in IDs ki attendance ho chuki hai: {already_marked_ids}")

print("\n📸 QR Code scanner shuru ho gaya hai. 'q' dabakar band karein...\n")

# ========== Step 4: Main loop with OpenCV QR Code Detector ==========
qr_detector = cv2.QRCodeDetector()

while True:
    success, img = cap.read()
    if not success:
        print("❌ Camera se frame capture nahi ho pa raha hai.")
        break

    # QR code detect aur decode karein using OpenCV
    data, bbox, _ = qr_detector.detectAndDecode(img)
    
    if data:
        qr_data_string = data.strip()
        print(f"QR Data received: {qr_data_string}")

        # Parse QR data
        lines = qr_data_string.strip().split('\n')
        details = {}
        for line in lines:
            parts = line.split(':', 1)
            if len(parts) == 2:
                details[parts[0].strip()] = parts[1].strip()

        student_id = details.get('StudentID')

        # ========== Step 5: Attendance Marking ==========
        if student_id and student_id not in already_marked_ids:
            name = details.get('Name', 'N/A')
            current_time = datetime.now().strftime('%H:%M:%S')

            with open('attendance.csv', 'a', newline='') as f:
                f.write(f'{student_id},{name},{today_date},{current_time},\n')

            print(f"✅ Attendance Marked: ID - {student_id}, Naam - {name}")
            already_marked_ids.add(student_id)
            
            # Success message display karein
            cv2.putText(img, f"Attendance Marked: {name}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Attendance System - QR Scanner', img)
            cv2.waitKey(2000)  # 2 second ke liye display karein
            time.sleep(3)

        elif student_id in already_marked_ids:
            print(f"⚠️ ID: {student_id} ki attendance aaj pehle hi mark ho chuki hai.")
            
            # Warning message display karein
            cv2.putText(img, f"Already Marked: {student_id}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow('Attendance System - QR Scanner', img)
            cv2.waitKey(2000)
            time.sleep(2)

    # Webcam feed display karo
    cv2.imshow('Attendance System - QR Scanner', img)

    # 'q' key dabane par loop break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ========== Step 6: Cleanup ==========
print("\n🛑 Scanner band kar diya gaya hai.")
cap.release()
cv2.destroyAllWindows()