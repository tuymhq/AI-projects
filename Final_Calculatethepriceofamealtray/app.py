import os
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import requests
import base64
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='static', static_url_path='')

# ==================== ĐƯỜNG DẪN ====================
model_path = r"D:\AI projects\Freshman year\Final\final_model.keras"
dataset_dir = r"D:\AI projects\Freshman year\Final\dataset"

# ==================== CẤU HÌNH ROBOFLOW ====================
ROBOFLOW_API_KEY = "Hh32KsKk1eojQ0ACtNpw"
ROBOFLOW_MODEL_ID = "ai_number_of_eggs_tut/1"

# ==================== LOAD MODEL ====================
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Không tìm thấy model tại {model_path}")

print("[*] Dang load model TensorFlow...")
model = load_model(model_path)
print("[+] Loaded model:", model_path)

if os.path.exists(dataset_dir):
    class_names = sorted([d for d in os.listdir(dataset_dir) 
                         if os.path.isdir(os.path.join(dataset_dir, d))])
else:
    class_names = [
        'Cơm', 'Đậu hũ sốt cà', 'Cá hú kho', 'Thịt kho trứng', 'Thịt kho',
        'Canh chua có cá', 'Canh chua không cá', 'Sườn nướng', 'Canh rau cải thảo',
        'Canh rau muống', 'Rau xào củ sắn', 'Rau xào đậu đũa', 'Rau xào đậu que',
        'Rau xào Lagim', 'Trứng chiên', 'Trứng chiên thịt'
    ]
print("[i] Cac mon chi tiet (16 classes):", class_names)

FOOD_PRICES = {
    'Cơm': ('Cơm trắng', 10000),
    'Đậu hũ sốt cà': ('Đậu hũ sốt cà', 25000),
    'Cá hú kho': ('Cá hú kho', 30000),
    'Thịt kho trứng': ('Thịt kho trứng', 30000),
    'Thịt kho': ('Thịt kho', 25000),
    'Canh chua có cá': ('Canh chua có cá', 25000),
    'Canh chua không cá': ('Canh chua không cá', 10000),
    'Sườn nướng': ('Sườn nướng', 30000),
    'Canh rau cải thảo': ('Canh rau', 7000),
    'Canh rau muống': ('Canh rau', 7000),
    'Rau xào củ sắn': ('Rau xào', 10000),
    'Rau xào đậu đũa': ('Rau xào', 10000),
    'Rau xào đậu que': ('Rau xào', 10000),
    'Rau xào Lagim': ('Rau xào', 10000),
    'Trứng chiên': ('Trứng chiên', 25000),
    'Trứng chiên thịt': ('Trứng chiên', 25000),
}

def count_eggs_in_thit_kho_trung(image_bgr):
    try:
        _, img_encoded = cv2.imencode('.jpg', image_bgr)
        image_bytes = img_encoded.tobytes()
        response = requests.post(
            f"https://detect.roboflow.com/{ROBOFLOW_MODEL_ID}",
            params={"api_key": ROBOFLOW_API_KEY},
            files={"file": ("image.jpg", image_bytes, "image/jpeg")}
        )
        if response.status_code == 200:
            result = response.json()
            predictions = result.get('predictions', [])
            egg_count = len([p for p in predictions if p.get('confidence', 0) > 0.3])
            return egg_count
        else:
            return None
    except Exception:
        return None

def split_food_tray(image, expand=0, move_lr=0, move_ud=0):
    h, w = image.shape[:2]
    
    # Tọa độ dạng % (cố định theo tỷ lệ, áp dụng cho mọi ảnh)
    regions_percent = {
        'o_tren_trai':   (21.5, 9.5, 41.5, 41.5),
        'o_tren_giua':   (42.0, 10.5, 61.5, 42.5),
        'o_tren_phai':   (61.5, 11.5, 81.5, 44.5),
        'o_duoi_trai':   (19.5, 43.0, 44.5, 91.5),
        'o_duoi_phai':   (50.0, 45.0, 80.5, 93.5)
    }
    
    # Chuyển % sang pixel và áp dụng expand, move
    regions = {}
    for name, (x1_pct, y1_pct, x2_pct, y2_pct) in regions_percent.items():
        x1 = (x1_pct + move_lr/10) * w / 100 - expand
        y1 = (y1_pct + move_ud/10) * h / 100 - expand
        x2 = (x2_pct + move_lr/10) * w / 100 + expand
        y2 = (y2_pct + move_ud/10) * h / 100 + expand
        regions[name] = (x1, y1, x2, y2)
    
    crops = []
    region_names = []
    annotated_image = image.copy()
    
    for name, (x1, y1, x2, y2) in regions.items():
        x1 = max(0, int(x1))
        y1 = max(0, int(y1))
        x2 = min(w, int(x2))
        y2 = min(h, int(y2))
        
        if x2 <= x1 or y2 <= y1:
            crop = np.zeros((50, 50, 3), dtype=np.uint8)
        else:
            crop = image[y1:y2, x1:x2]
        
        crops.append(crop)
        region_names.append(name)
        
        # Vẽ khung lên ảnh gốc để hiển thị
        cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (46, 204, 113), 3)
        display_name = name.replace('o_', '').replace('tren_trai', 'Tren Trai').replace('tren_giua', 'Tren Giua').replace('tren_phai', 'Tren Phai').replace('duoi_trai', 'Duoi Trai').replace('duoi_phai', 'Duoi Phai')
        cv2.putText(annotated_image, display_name, (x1 + 5, y1 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2, cv2.LINE_AA)
    
    # Resize ảnh về kích thước hiển thị (giữ nguyên tỷ lệ)
    display_height = 500
    display_width = int(w * display_height / h)
    annotated_image = cv2.resize(annotated_image, (display_width, display_height))
    
    return annotated_image, crops, region_names

def predict_food(food_img):
    if food_img.size == 0 or food_img.shape[0] < 10 or food_img.shape[1] < 10:
        return "Lỗi ảnh", 0, 0.0, "Error"
    
    img = cv2.resize(food_img, (200, 200)) / 255.0
    img = np.expand_dims(img, axis=0)
    pred = model.predict(img, verbose=0)[0]
    class_idx = np.argmax(pred)
    confidence = float(pred[class_idx])
    detail_name = class_names[class_idx]
    display_name, price = FOOD_PRICES.get(detail_name, (detail_name, 0))
    return display_name, price, confidence, detail_name

def image_to_base64(img):
    _, buffer = cv2.imencode('.jpg', img)
    return f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

def resolve_conflicts_by_group(results, crops):
    """Xử lý xung đột theo nhóm - mỗi nhóm chỉ 1 món"""
    GROUPS = {
        'Canh chua': ['Canh chua có cá', 'Canh chua không cá'],
        'Canh rau': ['Canh rau cải thảo', 'Canh rau muống'],
        'Rau xào': ['Rau xào củ sắn', 'Rau xào đậu đũa', 'Rau xào đậu que', 'Rau xào Lagim'],
        'Trứng': ['Trứng chiên', 'Trứng chiên thịt'],
        'Thịt kho': ['Thịt kho trứng', 'Thịt kho']
    }
    
    dish_to_group = {}
    for group, dishes in GROUPS.items():
        for d in dishes:
            dish_to_group[d] = group
    
    def get_top_predictions(crop, top_k=8):
        if crop.size == 0 or crop.shape[0] < 10:
            return [('Cơm', 0.5)]
        img = cv2.resize(crop, (200, 200)) / 255.0
        img = np.expand_dims(img, axis=0)
        pred = model.predict(img, verbose=0)[0]
        indices = np.argsort(pred)[::-1][:top_k]
        return [(class_names[i], float(pred[i])) for i in indices]
    
    all_preds = [get_top_predictions(crop) for crop in crops]
    order = sorted(range(len(results)), key=lambda i: results[i]['confidence'], reverse=True)
    
    selected = [None] * len(results)
    used_dishes = set()
    used_groups = set()
    
    for idx in order:
        placed = False
        for dish_name, conf in all_preds[idx]:
            group = dish_to_group.get(dish_name)
            if dish_name in used_dishes:
                continue
            if group is not None and group in used_groups:
                continue
            display_name, price = FOOD_PRICES.get(dish_name, (dish_name, 0))
            selected[idx] = {
                'stt': results[idx]['stt'],
                'region_id': results[idx]['region_id'],
                'region_name': results[idx]['region_name'],
                'dish_name': display_name,
                'detail_name': dish_name,
                'price': price,
                'confidence': conf,
                'egg_count': None,
                'crop_image': results[idx]['crop_image']
            }
            used_dishes.add(dish_name)
            if group:
                used_groups.add(group)
            placed = True
            break
        if not placed:
            dish_name, conf = all_preds[idx][0]
            display_name, price = FOOD_PRICES.get(dish_name, (dish_name, 0))
            selected[idx] = {
                'stt': results[idx]['stt'],
                'region_id': results[idx]['region_id'],
                'region_name': results[idx]['region_name'],
                'dish_name': display_name,
                'detail_name': dish_name,
                'price': price,
                'confidence': conf,
                'egg_count': None,
                'crop_image': results[idx]['crop_image']
            }
    
    # Xử lý Thịt kho trứng
    for i, item in enumerate(selected):
        if item and item['detail_name'] == 'Thịt kho trứng':
            egg_count = count_eggs_in_thit_kho_trung(crops[i])
            if egg_count and egg_count > 0:
                if egg_count == 1:
                    item['dish_name'] = "Thịt kho trứng (1 trứng)"
                    item['price'] = 30000
                elif egg_count == 2:
                    item['dish_name'] = "Thịt kho 2 trứng"
                    item['price'] = 35000
                else:
                    item['dish_name'] = f"Thịt kho {egg_count} trứng"
                    item['price'] = 30000 + (egg_count - 1) * 5000
                item['egg_count'] = egg_count
            else:
                item['detail_name'] = 'Thịt kho'
                item['dish_name'] = 'Thịt kho'
                item['price'] = 25000
    
    selected.sort(key=lambda x: x['stt'])
    return selected

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
        
    expand = int(request.form.get('expand', 0))
    move_lr = int(request.form.get('move_lr', 0))
    move_ud = int(request.form.get('move_ud', 0))
    
    file_bytes = np.frombuffer(file.read(), np.uint8)
    image_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if image_bgr is None:
        return jsonify({'error': 'Invalid image format'}), 400
    
    # Resize ảnh về kích thước chuẩn để xử lý (giữ tỷ lệ, chỉnh về chiều cao 800)
    h, w = image_bgr.shape[:2]
    target_height = 800
    target_width = int(w * target_height / h)
    image_bgr = cv2.resize(image_bgr, (target_width, target_height))
    
    annotated_img, crops, region_names = split_food_tray(image_bgr, expand, move_lr, move_ud)
    
    initial_results = []
    for idx, (crop, region) in enumerate(zip(crops, region_names), start=1):
        name, price, conf, detail_name = predict_food(crop)
        
        display_region = region.replace('o_tren_trai', 'Trên trái').replace('o_tren_giua', 'Trên giữa').replace('o_tren_phai', 'Trên phải').replace('o_duoi_trai', 'Dưới trái').replace('o_duoi_phai', 'Dưới phải')
        
        egg_count = None
        if detail_name == 'Thịt kho trứng':
            egg_count = count_eggs_in_thit_kho_trung(crop)
            if egg_count and egg_count > 0:
                if egg_count == 1:
                    name = "Thịt kho trứng (1 trứng)"; price = 30000
                elif egg_count == 2:
                    name = "Thịt kho 2 trứng"; price = 35000
                else:
                    name = f"Thịt kho {egg_count} trứng"; price = 30000 + (egg_count - 1) * 5000
            else:
                name = "Thịt kho"; price = 25000; detail_name = "Thịt kho"
        
        crop_resized = cv2.resize(crop, (150, 150))
        crop_base64 = image_to_base64(crop_resized)
        
        initial_results.append({
            'stt': idx, 'region_id': region, 'region_name': display_region,
            'dish_name': name, 'detail_name': detail_name, 'price': price,
            'confidence': conf, 'egg_count': egg_count, 'crop_image': crop_base64
        })
    
    print("\n" + "="*60)
    print("DỰ ĐOÁN BAN ĐẦU:")
    for r in initial_results:
        print(f"  Ô {r['stt']} ({r['region_name']}): {r['dish_name']} ({r['confidence']:.2%})")
    
    final_results = resolve_conflicts_by_group(initial_results, crops)
    
    print("\nKẾT QUẢ CUỐI CÙNG:")
    for r in final_results:
        print(f"  Ô {r['stt']} ({r['region_name']}): {r['dish_name']} ({r['confidence']:.2%})")
    print("="*60 + "\n")
    
    total_price = sum(item['price'] for item in final_results)
    annotated_base64 = image_to_base64(annotated_img)
    
    return jsonify({
        'annotated_image': annotated_base64,
        'items': final_results,
        'total_price': total_price
    })

if __name__ == '__main__':
    print("[*] Dang khoi dong Flask server tai http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=True)