import unittest
import sys

# Thiết lập encoding UTF-8 cho stdout/stderr để tránh lỗi Unicode trên Windows terminal
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

import numpy as np
import cv2
import os
from app import app, split_food_tray, predict_food, FOOD_PRICES

class TestCNNFoodBackend(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_routes_exist(self):
        # Kiểm tra route chính
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_split_food_tray(self):
        # Tạo ảnh giả lập 1000x1000 để test hàm split_food_tray
        dummy_img = np.zeros((1000, 1000, 3), dtype=np.uint8)
        annotated_img, crops, region_names = split_food_tray(dummy_img, expand=5, move_lr=2, move_ud=-2)
        
        self.assertEqual(annotated_img.shape, (1000, 1000, 3))
        self.assertEqual(len(crops), 5)
        self.assertEqual(len(region_names), 5)
        self.assertEqual(region_names[0], 'o_tren_trai')

    def test_predict_food_structure(self):
        # Test cấu trúc kết quả dự đoán của predict_food với ảnh dummy
        dummy_crop = np.zeros((200, 200, 3), dtype=np.uint8)
        name, price, conf, detail_name = predict_food(dummy_crop)
        
        self.assertIsInstance(name, str)
        self.assertIsInstance(price, int)
        self.assertIsInstance(conf, float)
        self.assertIsInstance(detail_name, str)
        self.assertTrue(0.0 <= conf <= 1.0)

if __name__ == '__main__':
    print("[*] Bat dau chay unit tests cho Backend...")
    unittest.main()
