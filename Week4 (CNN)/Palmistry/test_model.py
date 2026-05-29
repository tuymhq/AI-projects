import cv2
from ultralytics import YOLO
from matplotlib import pyplot as plt

model_path = 'palmistry_model.pt'
image_paths = ['anh_test_1.png', 'anh_test_2.png', 'anh_test_3.png']

print("Đang tải model...")
model = YOLO(model_path)

vietnamese_names = {0: 'Sự nghiệp', 1: 'Sinh đạo', 2: 'Trí đạo', 3: 'Tam đạo'}
model.model.names = vietnamese_names

print("Đang xử lý ảnh...\n")
results = model.predict(source=image_paths, conf=0.25, imgsz=640)

for i, result in enumerate(results):
    print(f"{'='*50}")
    print(f"ẢNH {i+1}: {image_paths[i]}")
    
    annotated_img = result.plot()
    
    if len(result.boxes) > 0:
        print(f"Phát hiện {len(result.boxes)} đường chỉ tay:")
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            print(f"  - {vietnamese_names[class_id]}: {confidence:.2%}")
    else:
        print("  Không phát hiện đường chỉ tay nào")
    
    # Hiển thị ảnh
    img_rgb = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(10, 8))
    plt.imshow(img_rgb)
    plt.axis('off')
    plt.title(f'Kết quả: {image_paths[i]}')
    plt.show()

print("\n✅ Hoàn tất!")