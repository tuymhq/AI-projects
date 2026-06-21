import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping, ModelCheckpoint
from tensorflow.keras.regularizers import l2
import os

# ==================== ĐƯỜNG DẪN ====================
train_dir = r"D:\AI projects\Freshman year\Final\dataset"
print("GPU available:", tf.config.list_physical_devices('GPU'))

# ==================== THAM SỐ ====================
IMG_SIZE = (200, 200)
BATCH_SIZE = 32
EPOCHS_PHASE1 = 20
EPOCHS_PHASE2 = 30

# ==================== DATA AUGMENTATION ====================
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=40,
    width_shift_range=0.3,
    height_shift_range=0.3,
    shear_range=0.3,
    zoom_range=0.3,
    horizontal_flip=True,
    brightness_range=[0.7, 1.3],
    fill_mode='nearest',
    validation_split=0.2
)

val_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

train_gen = train_datagen.flow_from_directory(
    train_dir,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

val_gen = val_datagen.flow_from_directory(
    train_dir,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

num_classes = len(train_gen.class_indices)
print(f"Số lớp: {num_classes}")
print(f"Class indices: {train_gen.class_indices}")
print(f"Train samples: {train_gen.samples}, Val samples: {val_gen.samples}")

# ==================== XÂY DỰNG MÔ HÌNH ====================
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(200, 200, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False   # Ban đầu đóng băng toàn bộ

model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    BatchNormalization(),
    Dense(256, activation='relu', kernel_regularizer=l2(0.001)),
    Dropout(0.5),
    Dense(128, activation='relu', kernel_regularizer=l2(0.001)),
    Dropout(0.3),
    Dense(num_classes, activation='softmax')
])

reduce_lr = ReduceLROnPlateau(monitor='val_accuracy', factor=0.2, patience=3, min_lr=1e-6, verbose=1)
early_stop = EarlyStopping(monitor='val_accuracy', patience=10, restore_best_weights=True, verbose=1)
checkpoint = ModelCheckpoint('best_model.keras', monitor='val_accuracy', save_best_only=True, verbose=1)

# ========== GIAI ĐOẠN 1: Train top layers (base_model frozen) ==========
model.compile(optimizer=Adam(learning_rate=1e-3),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

print("===== GIAI ĐOẠN 1: Chỉ train phần top (base model đóng băng) =====")
history1 = model.fit(train_gen, validation_data=val_gen,
                     epochs=EPOCHS_PHASE1,
                     callbacks=[reduce_lr, early_stop, checkpoint],
                     verbose=1)

# ========== GIAI ĐOẠN 2: Mở 20 lớp cuối của base_model (fine-tune) ==========
print("===== GIAI ĐOẠN 2: Mở 20 lớp cuối của MobileNetV2 để fine-tune =====")
base_model.trainable = True

# Nhưng ta sẽ chỉ mở 20 lớp cuối, các lớp đầu giữ nguyên frozen
for layer in base_model.layers[:-20]:
    layer.trainable = False

# Kiểm tra số lượng trainable parameters
model.compile(optimizer=Adam(learning_rate=1e-5),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

history2 = model.fit(train_gen, validation_data=val_gen,
                     epochs=EPOCHS_PHASE2,
                     callbacks=[reduce_lr, early_stop, checkpoint],
                     verbose=1)

# Lưu model cuối
model.save("final_model.keras")
print("Đã lưu model: final_model.keras")

# Kết quả tốt nhất
best_val_acc = max(history2.history['val_accuracy']) if history2.history['val_accuracy'] else history1.history['val_accuracy'][-1]
print(f"Validation accuracy tốt nhất: {best_val_acc:.4f}")