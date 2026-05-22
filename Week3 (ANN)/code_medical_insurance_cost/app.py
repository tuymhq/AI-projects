from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os
import tensorflow as tf
from keras.models import load_model




os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.keras.backend.clear_session()




custom_objects = {
    'mse': tf.keras.losses.MeanSquaredError(),
    'mae': tf.keras.metrics.MeanAbsoluteError()
}




app = Flask(__name__, template_folder='.')
CORS(app)




# Load model
print("Loading model...")
try:
    model = load_model('insurance_model.h5', custom_objects=custom_objects, compile=False)
    print("✅ Model loaded")
except Exception as e:
    print(f"⚠️ Error: {e}, trying with compile=False...")
    model = load_model('insurance_model.h5', compile=False)
    print("✅ Model loaded with compile=False")




scaler = joblib.load('scaler.pkl')
model_columns = joblib.load('model_columns.pkl')
print(f"✅ Features: {len(model_columns)}")




# Recompile model
model.compile(optimizer='adam', loss='mse', metrics=['mae'])




# Load metadata để lấy RMSE
try:
    metadata = joblib.load('model_metadata.pkl')
    rmse = metadata.get('rmse', 1500.0)
    print(f"✅ Loaded RMSE from metadata: {rmse:.2f}")
except:
    rmse = 1500.0
    print("⚠️ Using default RMSE = 1500")




# Load confidence config từ train_model.py
try:
    confidence_config = joblib.load('confidence_config.pkl')
    OVERALL_MAPE = confidence_config['overall_mape']
    CONF_BINS = confidence_config['bins']
    CONF_LABELS = confidence_config['labels']
    CONF_RATIOS = confidence_config['adjustment_ratios']
    print(f"✅ Loaded confidence config: MAPE={OVERALL_MAPE:.1f}%")
except:
    # Fallback nếu chưa chạy train_model.py
    OVERALL_MAPE = 31.73
    CONF_BINS = [0, 5000, 15000, 30000, 100000]
    CONF_LABELS = ['very_low', 'low', 'medium', 'high']
    CONF_RATIOS = {'very_low': 1.4, 'low': 1.0, 'medium': 0.7, 'high': 0.5}
    print("⚠️ Using default confidence config")




def calculate_confidence(prediction):
    """Tính confidence dựa trên MAPE theo nhóm từ dữ liệu thật"""
    # Xác định nhóm của prediction
    group = 'medium'
    for i in range(len(CONF_BINS) - 1):
        if CONF_BINS[i] <= prediction < CONF_BINS[i+1]:
            group = CONF_LABELS[i]
            break
   
    # Lấy adjustment ratio cho nhóm đó
    ratio = CONF_RATIOS.get(group, 1.0)
   
    # Tính MAPE dự kiến và confidence
    expected_mape = OVERALL_MAPE * ratio
    confidence = 100 - expected_mape
   
    # Giới hạn an toàn
    return round(max(55, min(95, confidence)), 1)




@app.route('/')
def index():
    return render_template('index.html')




@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        age = data['age']
        sex = data['sex']
        bmi = data['bmi']
        children = data['children']
        smoker = data['smoker']
        region = data['region']




        sex_male = 1 if sex == 'male' else 0
        smoker_yes = 1 if smoker == 'yes' else 0




        region_northwest = 1 if region == 'northwest' else 0
        region_southeast = 1 if region == 'southeast' else 0
        region_southwest = 1 if region == 'southwest' else 0




        input_array = np.array([[
            age, bmi, children, sex_male, smoker_yes,
            region_northwest, region_southeast, region_southwest
        ]])
        bmi_x_smoker = bmi * smoker_yes
        input_array = np.column_stack([input_array, [[bmi_x_smoker]]])
        input_scaled = scaler.transform(input_array)
        prediction = float(model.predict(input_scaled, verbose=0)[0][0])




        # Tính confidence (ĐÃ SỬA - KHÔNG DÙNG RMSE NỮA)
        confidence = calculate_confidence(prediction)




        # Phân loại BMI
        if bmi < 18.5:
            bmi_category = "Thiếu cân"
        elif bmi < 25:
            bmi_category = "Lý tưởng"
        elif bmi < 30:
            bmi_category = "Thừa cân"
        else:
            bmi_category = "Béo phì"




        return jsonify({
            'success': True,
            'total_cost': prediction,
            'confidence': confidence,
            'bmi_category': bmi_category
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})




if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Server running at: http://127.0.0.1:5000")
    print("🤖 Using ANN model with dynamic confidence")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)



