import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
import warnings
warnings.filterwarnings('ignore')








print("="*70)
print("🏥 MEDICAL INSURANCE COST PREDICTION - NEURAL NETWORK (OPTIMIZED)")
print("="*70)








# ==========================================
# 1. TẢI DỮ LIỆU
# ==========================================
print("\n📂 1. Đang tải dữ liệu từ GitHub...")
url = "https://raw.githubusercontent.com/stedy/Machine-Learning-with-R-datasets/master/insurance.csv"
df = pd.read_csv(url)








print(f"✅ Đã tải! Shape: {df.shape}")
print(f"\n📊 5 dòng đầu tiên:")
print(df.head())








# ==========================================
# 2. PHÂN TÍCH NHANH
# ==========================================
print("\n📈 2. Phân tích dữ liệu...")
print(f"   • Tuổi: {df['age'].min()} - {df['age'].max()} tuổi")
print(f"   • BMI: {df['bmi'].min():.1f} - {df['bmi'].max():.1f}")
print(f"   • Chi phí: ${df['charges'].min():,.0f} - ${df['charges'].max():,.0f}")
print(f"   • Hút thuốc: {df['smoker'].value_counts()['yes']} người")
print(f"   • Không hút: {df['smoker'].value_counts()['no']} người")








# ==========================================
# 3. TIỀN XỬ LÝ & FEATURE ENGINEERING
# ==========================================
print("\n⚙️ 3. Tiền xử lý và tối ưu hóa đặc trưng...")








# One-Hot Encoding
df_encoded = pd.get_dummies(df, columns=['sex', 'smoker', 'region'], drop_first=True)
df_encoded = df_encoded.astype(float)








# 🎯 FEATURE ENGINEERING QUAN TRỌNG: Tương tác BMI x Smoker
df_encoded['bmi_x_smoker'] = df_encoded['bmi'] * df_encoded['smoker_yes']








print(f"   ✅ Đã tạo feature mới: 'bmi_x_smoker'")








# Tách đặc trưng (X) và nhãn (y)
X = df_encoded.drop(columns=['charges'])
y = df_encoded['charges']








# Lưu danh sách cột (QUAN TRỌNG: phải đúng thứ tự cho app.py)
model_columns = X.columns.tolist()
joblib.dump(model_columns, 'model_columns.pkl')








print(f"\n   📋 Danh sách {len(model_columns)} features đã lưu:")
for i, col in enumerate(model_columns):
    print(f"      {i+1}. {col}")








# ==========================================
# 4. CHIA DỮ LIỆU
# ==========================================
print("\n✂️ 4. Chia dữ liệu Train/Test...")
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
print(f"   ✅ Train: {X_train.shape[0]} mẫu (64%)")
print(f"   ✅ Validation: {X_val.shape[0]} mẫu (16%)")
print(f"   ✅ Test: {X_test.shape[0]} mẫu (20%)")








# ==========================================
# 5. CHUẨN HÓA DỮ LIỆU
# ==========================================
print("\n📊 5. Chuẩn hóa dữ liệu với StandardScaler...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)
joblib.dump(scaler, 'scaler.pkl')
print("   ✅ Đã lưu scaler.pkl")








# ==========================================
# 6. XÂY DỰNG MÔ HÌNH NEURAL NETWORK
# ==========================================
print("\n🧠 6. Xây dựng mô hình Neural Network...")








input_dim = X_train_scaled.shape[1]








model = Sequential([
    Dense(128, activation='relu', input_shape=(input_dim,)),
    Dropout(0.1),
    Dense(64, activation='relu'),
    Dropout(0.1),
    Dense(32, activation='relu'),
    Dense(1)
])








model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
    loss='mse',
    metrics=['mae']
)








print("\n📐 Cấu trúc mô hình:")
model.summary()








# ==========================================
# 7. CALLBACKS
# ==========================================
print("\n⚙️ 7. Thiết lập callbacks...")








early_stop = EarlyStopping(monitor='val_loss', patience=25, restore_best_weights=True, verbose=1)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=10, min_lr=0.00001, verbose=1)
# ==========================================
# 8. HUẤN LUYỆN
# ==========================================
print("\n🔥 8. Bắt đầu huấn luyện...")








history = model.fit(
    X_train_scaled, y_train,
    validation_data=(X_val_scaled, y_val), # 👈 SỬA THÀNH DÒNG NÀY: Dùng trực tiếp tập test để chấm điểm qua từng vòng
    epochs=200,                              # 👈 Giảm xuống 200 cho nhẹ và nhanh ra kết quả
    batch_size=32,
    callbacks=[early_stop, reduce_lr],
    verbose=1
)
# ==========================================
# 9. ĐÁNH GIÁ MÔ HÌNH
# ==========================================
print("\n📊 9. Đánh giá mô hình trên tập test...")








y_pred = model.predict(X_test_scaled).flatten()








r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100








print(f"\n🎯 KẾT QUẢ ĐÁNH GIÁ:")
print(f"   • R² Score: {r2:.4f} ({r2*100:.2f}%)")
print(f"   • MAE: ${mae:,.2f}")
print(f"   • RMSE: ${rmse:,.2f}")
print(f"   • MAPE: {mape:.2f}%")








# ==========================================
# 10. VẼ BIỂU ĐỒ
# ==========================================
print("\n📈 10. Vẽ biểu đồ training history...")








fig, axes = plt.subplots(2, 2, figsize=(14, 10))








axes[0, 0].plot(history.history['loss'], label='Train Loss', linewidth=2, color='blue')
axes[0, 0].plot(history.history['val_loss'], label='Validation Loss', linewidth=2, color='red')
axes[0, 0].set_title('Model Loss (MSE)', fontsize=14, fontweight='bold')
axes[0, 0].set_xlabel('Epoch')
axes[0, 0].set_ylabel('Loss')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)








axes[0, 1].plot(history.history['mae'], label='Train MAE', linewidth=2, color='blue')
axes[0, 1].plot(history.history['val_mae'], label='Validation MAE', linewidth=2, color='red')
axes[0, 1].set_title('Model MAE (USD)', fontsize=14, fontweight='bold')
axes[0, 1].set_xlabel('Epoch')
axes[0, 1].set_ylabel('MAE (USD)')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)








axes[1, 0].plot(history.history['lr'] if 'lr' in history.history else [0.01] * len(history.history['loss']),
                linewidth=2, color='green')
axes[1, 0].set_title('Learning Rate', fontsize=14, fontweight='bold')
axes[1, 0].set_xlabel('Epoch')
axes[1, 0].set_ylabel('Learning Rate')
axes[1, 0].set_yscale('log')
axes[1, 0].grid(True, alpha=0.3)








axes[1, 1].scatter(y_test, y_pred, alpha=0.5, edgecolors='k', linewidth=0.5)
axes[1, 1].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', linewidth=2, label='Perfect Prediction')
axes[1, 1].set_title('Predicted vs Actual Charges', fontsize=14, fontweight='bold')
axes[1, 1].set_xlabel('Actual Charges ($)')
axes[1, 1].set_ylabel('Predicted Charges ($)')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)








plt.tight_layout()
plt.savefig('training_history.png', dpi=150, bbox_inches='tight')
print("   ✅ Đã lưu biểu đồ: training_history.png")








# ==========================================
# 11. LƯU MÔ HÌNH
# ==========================================
print("\n💾 11. Lưu mô hình...")








model.save('insurance_model.h5')
print("   ✅ Đã lưu: insurance_model.h5")








# Lưu metadata
metadata = {
    'model_type': 'Neural Network (Keras)',
    'input_dim': input_dim,
    'n_features': len(model_columns),
    'features': model_columns,
    'r2_score': float(r2),
    'mae': float(mae),
    'rmse': float(rmse),
    'mape': float(mape),
    'best_epoch': len(history.history['loss']),
    'final_learning_rate': float(model.optimizer.learning_rate.numpy())
}
joblib.dump(metadata, 'model_metadata.pkl')
print("   ✅ Đã lưu: model_metadata.pkl")








# ==========================================
# 12. KIỂM TRA THỬ NGHIỆM
# ==========================================
print("\n🧪 12. Kiểm tra thử nghiệm...")








def predict_insurance(age, bmi, children, sex_male, smoker_yes, region_nw, region_se, region_sw):
    input_arr = np.array([[age, bmi, children, sex_male, smoker_yes, region_nw, region_se, region_sw]])
    bmi_x_smoker = bmi * smoker_yes
    input_arr = np.column_stack([input_arr, [[bmi_x_smoker]]])
    input_scaled = scaler.transform(input_arr)
    return model.predict(input_scaled, verbose=0)[0][0]








result1 = predict_insurance(28, 23.5, 0, 1, 0, 0, 0, 1)
print(f"\n   📍 Test 1 (28 tuổi, không hút thuốc): ${result1:,.2f}")








result2 = predict_insurance(40, 30.0, 1, 1, 1, 0, 0, 0)
print(f"   📍 Test 2 (40 tuổi, hút thuốc): ${result2:,.2f}")


# ==========================================
# TÍNH HỆ SỐ CONFIDENCE ĐỘNG TỪ DỮ LIỆU THẬT
# ==========================================
print("\n📊 Tính hệ số confidence động từ dữ liệu thật...")


# Dự đoán trên tập test
y_pred_test = model.predict(X_test_scaled).flatten()


# Tạo dataframe so sánh
df_confidence = pd.DataFrame({
    'actual': y_test.values,
    'predicted': y_pred_test
})
df_confidence['ape'] = abs(df_confidence['actual'] - df_confidence['predicted']) / df_confidence['actual'] * 100


# Tạo bins dựa trên phân phối thực tế của chi phí
max_cost = df['charges'].max()
percentiles = df['charges'].quantile([0.25, 0.5, 0.75]).values
bins = [0, percentiles[0], percentiles[1], percentiles[2], max_cost + 10000]
labels = ['very_low', 'low', 'medium', 'high']


print(f"   ✅ Ngưỡng bins: {[round(b,0) for b in bins]}")


df_confidence['pred_group'] = pd.cut(df_confidence['predicted'], bins=bins, labels=labels)


# Tính MAPE trung bình cho từng nhóm
group_mape = df_confidence.groupby('pred_group')['ape'].mean().to_dict()
overall_mape = df_confidence['ape'].mean()


# Tính hệ số điều chỉnh (ratio)
adjustment_ratios = {}
for group in labels:
    if group in group_mape and overall_mape > 0:
        adjustment_ratios[group] = group_mape[group] / overall_mape
    else:
        adjustment_ratios[group] = 1.0


print(f"   📊 MAPE theo nhóm:")
for group in labels:
    if group in group_mape:
        print(f"      • {group}: {group_mape[group]:.1f}% (ratio = {adjustment_ratios[group]:.2f})")


# Lưu hệ số vào file
confidence_config = {
    'overall_mape': overall_mape,
    'bins': bins,
    'labels': labels,
    'adjustment_ratios': adjustment_ratios,
    'default_confidence': 100 - overall_mape
}
joblib.dump(confidence_config, 'confidence_config.pkl')


print(f"   ✅ Đã lưu confidence_config.pkl")




print("\n" + "="*70)
print("✅ TRAINING COMPLETE! Run 'python app.py'")
print("="*70)
