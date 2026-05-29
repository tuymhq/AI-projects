import os
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint

# Giải phóng bộ nhớ
tf.config.threading.set_intra_op_parallelism_threads(4)
tf.config.threading.set_inter_op_parallelism_threads(4)

# ========== CẤU HÌNH ==========
data_dir = r"D:\vn dishes"  # SỬA: đường dẫn đến thư mục chứa 5 món (Pho, Banh_my, Goi_cuon, Com_tam, Bun_thit_nuong)
BATCH_SIZE = 32
model_path = "vietnamese_food_model.keras"
IMG_SIZE = 150

# Kiểm tra thư mục dữ liệu
if not os.path.exists(data_dir):
    print(f"❌ LỖI: Không tìm thấy thư mục {data_dir}")
    print(f"📌 Thư mục hiện tại: {os.getcwd()}")
    exit()

# ========== DATA GENERATOR ==========
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split=0.2  # 20% để validation
)

train_generator = train_datagen.flow_from_directory(
    data_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

val_generator = train_datagen.flow_from_directory(
    data_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

# Lấy số lớp tự động
num_classes = train_generator.num_classes
class_names = list(train_generator.class_indices.keys())

print(f"\n✅ Tìm thấy {num_classes} lớp:")
for i, name in enumerate(class_names, 1):
    print(f"   {i}. {name}")
print(f"📊 Tổng số ảnh train: {train_generator.samples}")
print(f"📊 Tổng số ảnh val: {val_generator.samples}")

# ========== TẠO HOẶC LOAD MODEL ==========
if os.path.exists(model_path):
    print(f"\n-> Đang tải lại mô hình từ {model_path} để tiếp tục train...")
    model = load_model(model_path)
    print("-> Tải mô hình thành công!")
    continue_training = True
else:
    print(f"\n-> Không tìm thấy model cũ. Tạo model mới...")
    
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
        BatchNormalization(),
        MaxPooling2D(2, 2),

        Conv2D(64, (3, 3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D(2, 2),

        Conv2D(128, (3, 3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D(2, 2),

        Conv2D(256, (3, 3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D(2, 2),
        
        Flatten(),
        Dense(256, activation='relu'),
        Dropout(0.4),
        Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    print("-> Tạo model mới thành công!")
    continue_training = False

model.summary()

# ========== CALLBACKS ==========
checkpoint = ModelCheckpoint(
    model_path,
    monitor='val_accuracy',
    verbose=1,
    save_best_only=True,
    mode='max'
)

# ========== HUẤN LUYỆN ==========
if continue_training:
    MORE_EPOCHS = 15
    print(f"\n--- BẮT ĐẦU HUẤN LUYỆN TIẾP TỤC ({MORE_EPOCHS} EPOCHS MỚI) ---")
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=MORE_EPOCHS,
        callbacks=[checkpoint]
    )
    
    final_accuracy = history.history['accuracy'][-1]
    final_val_accuracy = history.history['val_accuracy'][-1]
    print("\n-------------------------------------------")
    print(f"Huấn luyện nối tiếp hoàn tất!")
    print(f"✅ Train Accuracy: {final_accuracy * 100:.2f}%")
    print(f"✅ Val Accuracy: {final_val_accuracy * 100:.2f}%")
    print("-------------------------------------------")
    
    # Vẽ biểu đồ continued training
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Train Accuracy', color='blue')
    plt.plot(history.history['val_accuracy'], label='Val Accuracy', color='orange')
    plt.title('Model Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Train Loss', color='red')
    plt.plot(history.history['val_loss'], label='Val Loss', color='purple')
    plt.title('Model Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
    
else:
    EPOCHS = 70
    print(f"\n--- BẮT ĐẦU HUẤN LUYỆN TỪ ĐẦU ({EPOCHS} EPOCHS) ---")
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=EPOCHS,
        callbacks=[checkpoint]
    )
    
    final_accuracy = history.history['accuracy'][-1]
    final_val_accuracy = history.history['val_accuracy'][-1]
    print("\n-------------------------------------------")
    print(f"🎉 HUẤN LUYỆN HOÀN TẤT!")
    print(f"✅ Train Accuracy: {final_accuracy * 100:.2f}%")
    print(f"✅ Val Accuracy: {final_val_accuracy * 100:.2f}%")
    print(f"✅ Model lưu tại: {model_path}")
    print("-------------------------------------------")
    
    # Vẽ biểu đồ
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Train Accuracy', color='blue')
    plt.plot(history.history['val_accuracy'], label='Val Accuracy', color='orange')
    plt.title('Model Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Train Loss', color='red')
    plt.plot(history.history['val_loss'], label='Val Loss', color='purple')
    plt.title('Model Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()