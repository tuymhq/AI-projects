import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Đường dẫn
data_dir = r"D:\AI projects\Freshman year\Week4\Flowers"
model_path = r"D:\AI projects\Freshman year\Week4\Flowers\modelhoa.keras"

# Load model và class names
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
    
    # Xử lý ảnh
    img = cv2.resize(frame, (200, 200))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype('float32') / 255.0
    img = np.expand_dims(img, axis=0)
    
    # Dự đoán
    pred = model.predict(img, verbose=0)
    class_id = np.argmax(pred)
    confidence = pred[0][class_id] * 100
    
    # Hiển thị (chỉ 1 dòng kết quả)
    text = f"{class_names[class_id]}: {confidence:.1f}%"
    cv2.putText(frame, text, (50, 100), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0]-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1)
    
    cv2.imshow('Flower Recognition', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()