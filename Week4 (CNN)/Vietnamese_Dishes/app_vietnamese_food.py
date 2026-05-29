import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from flask import Flask, render_template_string
import os
import numpy as np
from tensorflow.keras.models import load_model
from flask import Flask, render_template_string, request, jsonify
import base64
from PIL import Image
import io

# ========== CẤU HÌNH ==========
model_path = "vietnamese_food_model.keras"
IMG_SIZE = 150

# Tên hiển thị tiếng Việt (khớp với 5 món trong dataset của bạn)
display_names = {
    'Banh_chung': 'Bánh Chưng 🍚',
    'Banh_my': 'Bánh Mì 🥖',
    'Bun_thit_nuong': 'Bún Thịt Nướng 🍢',
    'Com_tam': 'Cơm Tấm 🍚',
    'Goi_cuon': 'Gỏi Cuốn 🌯'
}

# Lấy danh sách class từ thư mục dataset
data_dir = r"D:\vn dishes"
if os.path.exists(data_dir):
    class_names = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
else:
    class_names = list(display_names.keys())

# Tạo mapping index -> tên hiển thị
idx_to_name = {}
for i, name in enumerate(class_names):
    idx_to_name[i] = display_names.get(name, name)

# ========== LOAD MODEL ==========
if not os.path.exists(model_path):
    print(f"\n❌ LỖI: Không tìm thấy model!")
    print(f"📌 File model '{model_path}' không tồn tại.")
    print(f"📌 Vui lòng chạy file 'vn dishes.py' để train model trước.")
    print(f"📌 Các file trong thư mục hiện tại:")
    for f in os.listdir('.'):
        print(f"   - {f}")
    exit()

print(f"\n📂 Đang tải model từ {model_path}...")
model = load_model(model_path)
print("✅ Tải model thành công!")
print(f"✅ Nhận diện {len(class_names)} món: {list(idx_to_name.values())}")

# ========== WEB APP ==========
app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Nhận diện món ăn Việt Nam</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 500px;
            width: 100%;
            text-align: center;
        }
        h1 { color: #e74c3c; margin-bottom: 10px; }
        .sub { color: #7f8c8d; margin-bottom: 30px; }
        .upload-area {
            border: 2px dashed #bdc3c7;
            border-radius: 15px;
            padding: 40px;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 20px;
        }
        .upload-area:hover { border-color: #e74c3c; background: #fef5f5; }
        .upload-area.dragover { border-color: #27ae60; background: #f0fff4; }
        #preview { max-width: 100%; max-height: 250px; margin: 15px 0; border-radius: 10px; display: none; }
        button {
            background: #e74c3c; color: white; border: none; padding: 12px 30px;
            border-radius: 25px; font-size: 16px; cursor: pointer; transition: 0.3s; margin-top: 10px;
        }
        button:hover { background: #c0392b; transform: scale(1.02); }
        button:disabled { background: #95a5a6; cursor: not-allowed; }
        .result { margin-top: 25px; padding: 20px; border-radius: 15px; display: none; }
        .result.success { background: #d5f4e6; border: 1px solid #27ae60; display: block; }
        .dish-name { font-size: 28px; font-weight: bold; color: #27ae60; }
        .confidence { font-size: 20px; color: #e67e22; margin-top: 10px; }
        .loading { display: none; margin: 20px 0; }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #e74c3c;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .dish-list { margin-top: 20px; display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; }
        .dish-tag { background: #ecf0f1; padding: 5px 12px; border-radius: 20px; font-size: 14px; }
        .preview-container { position: relative; display: inline-block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🍜 Nhận diện món ăn Việt Nam</h1>
        <div class="sub">Tải ảnh lên để AI nhận diện</div>
        
        <div class="upload-area" id="uploadArea">
            📸 Kéo thả ảnh vào đây hoặc bấm để chọn
            <input type="file" id="fileInput" accept="image/*" style="display: none">
        </div>
        
        <div class="preview-container">
            <img id="preview" alt="Xem trước">
            <button id="removeBtn" style="display: none; position: absolute; top: -10px; right: -10px; background: red; border-radius: 50%; width: 30px; height: 30px; padding: 0;">✕</button>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Đang phân tích...</p>
        </div>
        
        <div class="result" id="result">
            <div class="dish-name" id="dishName"></div>
            <div class="confidence" id="confidence"></div>
        </div>
        
        <div class="dish-list" id="dishList"></div>
        
        <button id="predictBtn" disabled>🔍 Nhận diện</button>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const preview = document.getElementById('preview');
        const removeBtn = document.getElementById('removeBtn');
        const predictBtn = document.getElementById('predictBtn');
        const loading = document.getElementById('loading');
        const resultDiv = document.getElementById('result');
        const dishNameSpan = document.getElementById('dishName');
        const confidenceSpan = document.getElementById('confidence');
        
        let currentImage = null;
        
        uploadArea.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => {
            if (e.target.files[0]) handleFile(e.target.files[0]);
        });
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
        });
        
        function handleFile(file) {
            if (!file.type.startsWith('image/')) {
                alert('Vui lòng chọn file ảnh!');
                return;
            }
            currentImage = file;
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.src = e.target.result;
                preview.style.display = 'block';
                removeBtn.style.display = 'block';
                predictBtn.disabled = false;
                resultDiv.className = 'result';
            };
            reader.readAsDataURL(file);
        }
        
        removeBtn.addEventListener('click', () => {
            currentImage = null;
            preview.src = '';
            preview.style.display = 'none';
            removeBtn.style.display = 'none';
            predictBtn.disabled = true;
            resultDiv.className = 'result';
            fileInput.value = '';
        });
        
        predictBtn.addEventListener('click', async () => {
            if (!currentImage) return;
            
            const reader = new FileReader();
            reader.onload = async (e) => {
                const base64 = e.target.result;
                loading.style.display = 'block';
                predictBtn.disabled = true;
                
                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image: base64 })
                    });
                    const data = await response.json();
                    
                    if (data.success) {
                        dishNameSpan.innerHTML = data.dish_name;
                        confidenceSpan.innerHTML = `Độ tin cậy: ${data.confidence}%`;
                        resultDiv.className = 'result success';
                    } else {
                        alert('Lỗi: ' + data.error);
                    }
                } catch (error) {
                    alert('Không thể kết nối server!');
                } finally {
                    loading.style.display = 'none';
                    predictBtn.disabled = false;
                }
            };
            reader.readAsDataURL(currentImage);
        });
        
        fetch('/class_names')
            .then(res => res.json())
            .then(data => {
                const dishList = document.getElementById('dishList');
                dishList.innerHTML = data.map(name => `<span class="dish-tag">🍲 ${name}</span>`).join('');
            });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/class_names')
def get_class_names():
    return jsonify(list(idx_to_name.values()))

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        img_data = base64.b64decode(data['image'].split(',')[1])
        
        img = Image.open(io.BytesIO(img_data))
        img = img.resize((IMG_SIZE, IMG_SIZE))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        predictions = model.predict(img_array, verbose=0)
        predicted_class = np.argmax(predictions[0])
        confidence = float(np.max(predictions[0]) * 100)
        
        return jsonify({
            'success': True,
            'dish_name': idx_to_name[predicted_class],
            'confidence': round(confidence, 1)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ========== CHẠY APP ==========
if __name__ == '__main__':
    print("\n" + "="*50)
    print("🍜 NHẬN DIỆN MÓN ĂN VIỆT NAM")
    print("="*50)
    print("🚀 Mở trình duyệt: http://127.0.0.1:5000")
    print("="*50)
    app.run(debug=True, port=5000) 
    request, jsonify
import base64
from PIL import Image
import io

# ========== CẤU HÌNH ==========
model_path = "vietnamese_food_model.keras"
IMG_SIZE = 200

# Tên hiển thị tiếng Việt (phải khớp với class của model bạn đã train)
display_names = {
    'Banh_chung': 'Bánh chưng ',
    'Banh_my': 'Bánh Mì 🥖',
    'Goi_cuon': 'Gỏi Cuốn 🌯',
    'Com_tam': 'Cơm Tấm 🍚',
    'Bun_thit_nuong': 'Bún Thịt Nướng 🍢',
}

# ========== LOAD MODEL ==========
if not os.path.exists(model_path):
    print(f"❌ LỖI: Không tìm thấy model {model_path}")
    print(f"   Vui lòng chạy file train trước!")
    exit()

print(f"📂 Đang tải model từ {model_path}...")
model = load_model(model_path)
print("✅ Tải model thành công!")

# Lấy danh sách class từ model (cách đơn giản là bạn biết trước)
# Vì model đã train với 5 class, bạn cần biết thứ tự class
class_names = ['Pho', 'Banh_my', 'Goi_cuon', 'Com_tam', 'Bun_thit_nuong']

# Tạo mapping index -> tên hiển thị
idx_to_name = {}
for i, name in enumerate(class_names):
    idx_to_name[i] = display_names.get(name, name)

print(f"✅ Các class model nhận diện: {list(idx_to_name.values())}")

# ========== WEB APP ==========
app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Nhận diện món ăn Việt Nam</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 500px;
            width: 100%;
            text-align: center;
        }
        h1 { color: #e74c3c; margin-bottom: 10px; }
        .sub { color: #7f8c8d; margin-bottom: 30px; }
        .upload-area {
            border: 2px dashed #bdc3c7;
            border-radius: 15px;
            padding: 40px;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 20px;
        }
        .upload-area:hover { border-color: #e74c3c; background: #fef5f5; }
        .upload-area.dragover { border-color: #27ae60; background: #f0fff4; }
        #preview { max-width: 100%; max-height: 250px; margin: 15px 0; border-radius: 10px; display: none; }
        button {
            background: #e74c3c; color: white; border: none; padding: 12px 30px;
            border-radius: 25px; font-size: 16px; cursor: pointer; transition: 0.3s; margin-top: 10px;
        }
        button:hover { background: #c0392b; transform: scale(1.02); }
        button:disabled { background: #95a5a6; cursor: not-allowed; }
        .result { margin-top: 25px; padding: 20px; border-radius: 15px; display: none; }
        .result.success { background: #d5f4e6; border: 1px solid #27ae60; display: block; }
        .dish-name { font-size: 28px; font-weight: bold; color: #27ae60; }
        .confidence { font-size: 20px; color: #e67e22; margin-top: 10px; }
        .loading { display: none; margin: 20px 0; }
        .spinner {
            border: 4px solid #f3f3f3; border-top: 4px solid #e74c3c;
            border-radius: 50%; width: 40px; height: 40px;
            animation: spin 1s linear infinite; margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .dish-list { margin-top: 20px; display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; }
        .dish-tag { background: #ecf0f1; padding: 5px 12px; border-radius: 20px; font-size: 14px; }
        .preview-container { position: relative; display: inline-block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🍜 Nhận diện món ăn Việt Nam</h1>
        <div class="sub">Tải ảnh lên để AI nhận diện</div>
        
        <div class="upload-area" id="uploadArea">
            📸 Kéo thả ảnh vào đây hoặc bấm để chọn
            <input type="file" id="fileInput" accept="image/*" style="display: none">
        </div>
        
        <div class="preview-container">
            <img id="preview" alt="Xem trước">
            <button id="removeBtn" style="display: none; position: absolute; top: -10px; right: -10px; background: red; border-radius: 50%; width: 30px; height: 30px; padding: 0;">✕</button>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Đang phân tích...</p>
        </div>
        
        <div class="result" id="result">
            <div class="dish-name" id="dishName"></div>
            <div class="confidence" id="confidence"></div>
        </div>
        
        <div class="dish-list" id="dishList"></div>
        
        <button id="predictBtn" disabled>🔍 Nhận diện</button>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const preview = document.getElementById('preview');
        const removeBtn = document.getElementById('removeBtn');
        const predictBtn = document.getElementById('predictBtn');
        const loading = document.getElementById('loading');
        const resultDiv = document.getElementById('result');
        const dishNameSpan = document.getElementById('dishName');
        const confidenceSpan = document.getElementById('confidence');
        
        let currentImage = null;
        
        uploadArea.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => {
            if (e.target.files[0]) handleFile(e.target.files[0]);
        });
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
        });
        
        function handleFile(file) {
            if (!file.type.startsWith('image/')) {
                alert('Vui lòng chọn file ảnh!');
                return;
            }
            currentImage = file;
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.src = e.target.result;
                preview.style.display = 'block';
                removeBtn.style.display = 'block';
                predictBtn.disabled = false;
                resultDiv.className = 'result';
            };
            reader.readAsDataURL(file);
        }
        
        removeBtn.addEventListener('click', () => {
            currentImage = null;
            preview.src = '';
            preview.style.display = 'none';
            removeBtn.style.display = 'none';
            predictBtn.disabled = true;
            resultDiv.className = 'result';
            fileInput.value = '';
        });
        
        predictBtn.addEventListener('click', async () => {
            if (!currentImage) return;
            
            const reader = new FileReader();
            reader.onload = async (e) => {
                const base64 = e.target.result;
                loading.style.display = 'block';
                predictBtn.disabled = true;
                
                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image: base64 })
                    });
                    const data = await response.json();
                    
                    if (data.success) {
                        dishNameSpan.innerHTML = data.dish_name;
                        confidenceSpan.innerHTML = `Độ tin cậy: ${data.confidence}%`;
                        resultDiv.className = 'result success';
                    } else {
                        alert('Lỗi: ' + data.error);
                    }
                } catch (error) {
                    alert('Không thể kết nối server!');
                } finally {
                    loading.style.display = 'none';
                    predictBtn.disabled = false;
                }
            };
            reader.readAsDataURL(currentImage);
        });
        
        fetch('/class_names')
            .then(res => res.json())
            .then(data => {
                const dishList = document.getElementById('dishList');
                dishList.innerHTML = data.map(name => `<span class="dish-tag">🍲 ${name}</span>`).join('');
            });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/class_names')
def get_class_names():
    return jsonify([display_names.get(c, c) for c in class_names])

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        img_data = base64.b64decode(data['image'].split(',')[1])
        
        img = Image.open(io.BytesIO(img_data))
        img = img.resize((IMG_SIZE, IMG_SIZE))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        predictions = model.predict(img_array, verbose=0)
        predicted_class = np.argmax(predictions[0])
        confidence = float(np.max(predictions[0]) * 100)
        
        return jsonify({
            'success': True,
            'dish_name': idx_to_name[predicted_class],
            'confidence': round(confidence, 1)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ========== CHẠY APP ==========
if __name__ == '__main__':
    print("\n🚀 Khởi động web app...")
    print("📱 Mở trình duyệt tại: http://127.0.0.1:5000")
    print("="*50)
    app.run(debug=True, port=5000)