import cv2
import pandas as pd
from datetime import datetime
import os

# Ensure CSV exists
if not os.path.exists('attendance.csv'):
    with open('attendance.csv', 'w') as f:
        f.write('StudentID,Name,Date,Time,Emotion\n')

cap = cv2.VideoCapture(0)
qr = cv2.QRCodeDetector()

today = datetime.now().strftime('%d-%m-%Y')
df = pd.read_csv('attendance.csv')
already = set(df[df['Date'] == today]['StudentID'].astype(str))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    data, bbox, _ = qr.detectAndDecode(frame)
    if data:
        lines = data.strip().split('\n')
        details = {}
        for line in lines:
            parts = line.split(':', 1)
            if len(parts) == 2:
                details[parts[0].strip()] = parts[1].strip()

        sid = details.get('StudentID')
        name = details.get('Name', 'N/A')
        if sid and sid not in already:
            with open('attendance.csv', 'a') as f:
                f.write(f"{sid},{name},{today},{datetime.now().strftime('%H:%M:%S')},\n")
            already.add(sid)
            print(f"✅ Attendance marked for {name}")
            cv2.putText(frame, f"Marked: {name}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Already marked", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('QR Attendance - Camera Live', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
