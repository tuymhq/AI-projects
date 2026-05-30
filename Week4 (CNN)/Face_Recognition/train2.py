import os
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam

data_dir = r"D:\AI projects\Freshman year\Week4\Face_Recognition"
BATCH_SIZE = 32
MODEL_NAME = "face_id_model2.keras"

print("="*50)
print("👤 TRAIN NHẬN DIỆN KHUÔN MẶT TỪ ĐẦU")
print("="*50)

# Data augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.15,
    height_shift_range=0.15,
    zoom_range=0.15,
    horizontal_flip=True,
    brightness_range=[0.8, 1.2],
    shear_range=0.15,
    validation_split=0.2
)

val_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

# Load dữ liệu
train_generator = train_datagen.flow_from_directory(
    data_dir,
    target_size=(200, 200),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

val_generator = val_datagen.flow_from_directory(
    data_dir,
    target_size=(200, 200),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

num_classes = len(train_generator.class_indices)
print(f"\n📋 Số người cần nhận diện: {num_classes}")
print(f"📊 Tổng số ảnh train: {train_generator.samples}")
print(f"📊 Tổng số ảnh validation: {val_generator.samples}")

model = Sequential([
    # Block 1
    Conv2D(32, (3,3), activation='relu', padding='same', input_shape=(200, 200, 3)),
    BatchNormalization(),
    MaxPooling2D(2,2),
    Dropout(0.25),
    
    # Block 2
    Conv2D(64, (3,3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(2,2),
    Dropout(0.25),
    
    # Block 3
    Conv2D(128, (3,3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(2,2),
    Dropout(0.25),
    
    # Block 4
    Conv2D(256, (3,3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(2,2),
    Dropout(0.3),
    
    # Fully Connected
    Flatten(),
    Dense(256, activation='relu'),
    BatchNormalization(),
    Dropout(0.5),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(num_classes, activation='softmax')
])

# Compile
model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

callbacks = [
    ModelCheckpoint(
        MODEL_NAME, 
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    ),
    EarlyStopping(
        monitor='val_accuracy',
        patience=15,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=0.00001,
        verbose=1
    )
]

# Train
EPOCHS = 50
print(f"\n🚀 BẮT ĐẦU TRAIN {EPOCHS} EPOCHS")
print(f"💾 Model sẽ được lưu vào: {MODEL_NAME}")

history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=val_generator,
    callbacks=callbacks,
    verbose=1
)

# Kết quả
best_val_acc = max(history.history['val_accuracy'])
final_train_acc = history.history['accuracy'][-1]
final_val_acc = history.history['val_accuracy'][-1]

print("\n" + "="*50)
print("📊 KẾT QUẢ TRAIN")
print("="*50)
print(f"🏆 Validation Accuracy tốt nhất: {best_val_acc:.4f}")
print(f"✅ Training Accuracy cuối: {final_train_acc:.4f}")
print(f"✅ Validation Accuracy cuối: {final_val_acc:.4f}")
print(f"💾 Model đã lưu: {MODEL_NAME}")

# Kiểm tra overfitting
gap = final_train_acc - final_val_acc
if gap > 0.1:
    print(f"\n⚠️ Cảnh báo: Model có dấu hiệu overfit (chênh lệch {gap:.4f})")
elif gap < -0.05:
    print(f"\n✅ Tuyệt vời! Model tổng quát hóa rất tốt")
else:
    print(f"\n✅ Model cân bằng (chênh lệch {abs(gap):.4f})")

# Vẽ biểu đồ
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].plot(history.history['accuracy'], label='Train', linewidth=2)
axes[0].plot(history.history['val_accuracy'], label='Validation', linewidth=2)
axes[0].axhline(y=best_val_acc, color='g', linestyle='--', alpha=0.5, label=f'Best: {best_val_acc:.3f}')
axes[0].set_title('📈 Model Accuracy', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Accuracy')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(history.history['loss'], label='Train', linewidth=2)
axes[1].plot(history.history['val_loss'], label='Validation', linewidth=2)
axes[1].set_title('📉 Model Loss', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Loss')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("\n🎉 HOÀN THÀNH!")
print(f"👉 Dùng model '{MODEL_NAME}' để test webcam")
