import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Cấu hình
data_dir = r"D:\AI projects\Freshman year\Week4\Vietnamese_Banknotes"
model_path = "money_model2.keras"

# Load model
class_names = sorted([d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))])
print("Loading model...")
model = load_model(model_path)
print("Ready!")

# Mở camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Resize toàn bộ frame để nhận diện nhanh hơn
    frame_resized = cv2.resize(frame, (288, 384))
    
    # Chuẩn hóa
    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
    processed = frame_rgb.astype('float32') / 255.0
    processed = np.expand_dims(processed, axis=0)
    
    # Dự đoán
    predictions = model.predict(processed, verbose=0)
    class_id = np.argmax(predictions)
    confidence = predictions[0][class_id] * 100
    predicted_class = class_names[class_id]
    
    # Hiển thị kết quả trên frame gốc
    if confidence > 60:
        cv2.putText(frame, f"{predicted_class}", (50, 100), 
                   cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 0), 3)
        cv2.putText(frame, f"{confidence:.1f}%", (50, 150), 
                   cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "Dua tien vao camera", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 10), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    cv2.imshow('Test Banknote Recognition', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Test finished!")