import os
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam

path = r'D:\AI projects\Freshman year\Week4\Vietnamese_Banknotes'

IMG_HEIGHT = 288
IMG_WIDTH = 384
BATCH_SIZE = 24
MODEL_NAME = "money_model2.keras"

print("="*50)
print("💰 TRAIN NHẬN DIỆN TIỀN VIỆT NAM")
print("="*50)
print(f"📐 Kích thước ảnh: {IMG_WIDTH} x {IMG_HEIGHT} pixels")
print(f"📊 Tổng số pixels: {IMG_WIDTH * IMG_HEIGHT:,}")
print(f"🎯 Tỷ lệ khung hình: {IMG_WIDTH/IMG_HEIGHT:.2f} (4:3)")

# Data augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=30,
    zoom_range=0.25,
    horizontal_flip=True,
    brightness_range=[0.8, 1.2],
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2
)

val_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

# Load dữ liệu
train_generator = train_datagen.flow_from_directory(
    path,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

val_generator = val_datagen.flow_from_directory(
    path,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

num_classes = len(train_generator.class_indices)
print(f"\n📋 Classes: {train_generator.class_indices}")
print(f"🎯 Số loại tiền: {num_classes}")
print(f"📊 Tổng số ảnh train: {train_generator.samples}")
print(f"📊 Tổng số ảnh validation: {val_generator.samples}")

# Xây dựng model
model = Sequential([
    # Block 1
    Conv2D(32, (3,3), activation='relu', padding='same', input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)),
    BatchNormalization(),
    Conv2D(32, (3,3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(2,2),
    Dropout(0.25),

    # Block 2
    Conv2D(64, (3,3), activation='relu', padding='same'),
    BatchNormalization(),
    Conv2D(64, (3,3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(2,2),
    Dropout(0.25),

    # Block 3
    Conv2D(128, (3,3), activation='relu', padding='same'),
    BatchNormalization(),
    Conv2D(128, (3,3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(2,2),
    Dropout(0.25),

    # FC Layers
    Flatten(),
    Dense(128, activation='relu'),
    BatchNormalization(),
    Dropout(0.5),
    Dense(256, activation='relu'),
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

# Callbacks
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
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].plot(history.history['accuracy'], 'b-', label='Train Accuracy', linewidth=2)
axes[0].plot(history.history['val_accuracy'], 'r-', label='Validation Accuracy', linewidth=2)
axes[0].axhline(y=best_val_acc, color='g', linestyle='--', alpha=0.5, label=f'Best: {best_val_acc:.3f}')
axes[0].set_title('📈 Model Accuracy', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Epoch', fontsize=12)
axes[0].set_ylabel('Accuracy', fontsize=12)
axes[0].legend(fontsize=12)
axes[0].grid(True, alpha=0.3)

axes[1].plot(history.history['loss'], 'b-', label='Train Loss', linewidth=2)
axes[1].plot(history.history['val_loss'], 'r-', label='Validation Loss', linewidth=2)
axes[1].set_title('📉 Model Loss', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Epoch', fontsize=12)
axes[1].set_ylabel('Loss', fontsize=12)
axes[1].legend(fontsize=12)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("\n🎉 HOÀN THÀNH!")
print(f"🎯 Final Training Accuracy: {final_train_acc:.4f}")
print(f"🎯 Final Validation Accuracy: {final_val_acc:.4f}")
print(f"👉 Dùng model '{MODEL_NAME}' để test")