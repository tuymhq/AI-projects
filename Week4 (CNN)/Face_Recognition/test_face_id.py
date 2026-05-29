import os
import cv2
import math
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Cố gắng nạp tensorflow
try:
    from tensorflow.keras.models import load_model
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

# ====================== CẤU HÌNH ======================
data_dir = r"D:\AI projects\Freshman year\Week4\Face_Recognition"
model_path = "face_id_model2.keras"

# ====================== KHỞI TẠO AI ======================
print("⏳ Đang kiểm tra hệ thống và nạp mô hình AI...")
model = None
class_names = []

if HAS_TENSORFLOW:
    try:
        if os.path.exists(model_path):
            model = load_model(model_path)
            print("✅ Nạp model thành công!")
        else:
            print(f"⚠️ Không tìm thấy file model. Chạy DEMO MODE.")
        
        if os.path.exists(data_dir):
            class_names = sorted([d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))])
            print(f"📋 Các lớp: {class_names}")
        else:
            class_names = ["User_A", "User_B", "Unknown"]
    except Exception as e:
        print(f"❌ Lỗi: {e}")
else:
    print("⚠️ Không có TensorFlow. DEMO MODE.")
    class_names = ["Hoang_Anh", "Khanh_Vy", "Minh_Quan", "Unknown"]

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ====================== HÀM NHẬN DIỆN ======================
def predict_frame(img_rgb_frame):
    if model is None:
        import random
        mock_name = random.choice(class_names) if class_names else "Demo User"
        mock_conf = random.uniform(85.0, 99.9)
        return mock_name, mock_conf

    try:
        img_resized = cv2.resize(img_rgb_frame, (200, 200))
        processed = img_resized.astype('float32') / 255.0
        processed = np.expand_dims(processed, axis=0)

        predictions = model.predict(processed, verbose=0)
        class_id = np.argmax(predictions)
        confidence = predictions[0][class_id] * 100

        name = class_names[class_id] if class_id < len(class_names) else "Unknown"
        return name, confidence
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return "Error", 0.0


# ====================== POPUP KẾT QUẢ (GIỐNG INTRO) ======================
# ====================== POPUP KẾT QUẢ (Y CHANG INTRO) ======================
class ResultPopup:
    """Popup hiển thị kết quả nhận diện với style giống hệt intro"""
    def __init__(self, parent, name, confidence):
        self.parent = parent
        self.name = name
        self.confidence = confidence
        self.eye_size = 0
        self.rx = 0
        self.ry = 0
        
        # Tạo cửa sổ popup
        self.window = tk.Toplevel(parent)
        self.window.title("🎉 KẾT QUẢ NHẬN DIỆN 🎉")
        self.window.geometry("500x450")
        self.window.configure(bg="#f4ebe1")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center popup
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (450 // 2)
        self.window.geometry(f"+{x}+{y}")
        
        # Canvas vẽ kết quả
        self.canvas = tk.Canvas(self.window, bg="#f4ebe1", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Configure>", self.draw_result)
        
        # Bắt đầu animation nháy mắt
        self.window.after(800, self.start_wink_animation)
        
        # Tự động đóng sau 3 giây
        self.window.after(3000, self.window.destroy)
    
    def draw_result(self, event=None):
        """Vẽ popup y chang cái intro nhưng không có mặt người"""
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return
        
        accent_red = "#d32f2f"
        light_pink = "#f6cac5"
        bg_color = "#f4ebe1"
        
        # 1. Vẽ Rèm đỏ phía trên (Scallop Curtains) - Y CHANG INTRO
        num_scallops = 6
        scallop_w = w / num_scallops
        scallop_h = h * 0.15
        
        self.canvas.create_rectangle(0, 0, w, scallop_h / 2, fill=accent_red, outline="")
        for i in range(num_scallops):
            x1 = i * scallop_w
            x2 = x1 + scallop_w
            self.canvas.create_oval(
                x1 - 2, -scallop_h * 0.2, 
                x2 + 2, scallop_h, 
                fill=accent_red, outline=""
            )

        # 2. Vẽ hai bên Má Hồng (Soft Blush Cheeks) - Y CHANG INTRO
        cheek_r = min(w, h) * 0.12
        # Má trái
        self.canvas.create_oval(
            w * 0.15 - cheek_r, h * 0.55 - cheek_r,
            w * 0.15 + cheek_r, h * 0.55 + cheek_r,
            fill=light_pink, outline=""
        )
        # Má phải
        self.canvas.create_oval(
            w * 0.85 - cheek_r, h * 0.55 - cheek_r,
            w * 0.85 + cheek_r, h * 0.55 + cheek_r,
            fill=light_pink, outline=""
        )

        # 3. Vẽ Mắt Trái (hình vuông màu đỏ) - Y CHANG INTRO
        eye_size = min(w, h) * 0.05
        lx = w * 0.32
        ly = h * 0.45
        self.canvas.create_rectangle(
            lx - eye_size/2, ly - eye_size/2,
            lx + eye_size/2, ly + eye_size/2,
            fill=accent_red, outline="", tags="left_eye"
        )

        # 4. Vẽ Mắt Phải (cho animation nháy) - Y CHANG INTRO
        self.rx = w * 0.68
        self.ry = h * 0.45
        self.eye_size = eye_size
        self.draw_right_eye(height=self.eye_size)
        
        # 5. DÒNG CHỮ KẾT QUẢ (thay vì chữ FACE RECOGNITION)
        # Đặt ở vị trí giống chữ FACE RECOGNITION trong intro
        font_size = int(min(w, h) * 0.045)
        if font_size < 16:
            font_size = 16
        
        # Chữ TÊN
        name_str = self.name.upper()
        cx = w * 0.5
        cy = h * 0.58
        total_width = w * 0.6
        start_x = cx - total_width / 2
        dx = total_width / (len(name_str) - 1) if len(name_str) > 1 else 0
        smile_depth = h * 0.06
        
        for idx, char in enumerate(name_str):
            tx = start_x + idx * dx
            normalized_dist = (tx - cx) / (total_width / 2) if total_width > 0 else 0
            ty = cy + smile_depth * (1.0 - normalized_dist ** 2)
            
            # Đổ bóng
            self.canvas.create_text(
                tx + 2, ty + 2, text=char, 
                fill="#ebdcd0", 
                font=("Georgia", font_size, "bold"), 
                anchor="center"
            )
            # Chữ chính màu đỏ
            self.canvas.create_text(
                tx, ty, text=char, 
                fill=accent_red, 
                font=("Georgia", font_size, "bold"), 
                anchor="center"
            )
        
        # 6. DÒNG CONFIDENCE (đặt phía dưới)
        conf_font = int(font_size * 0.65)
        conf_text = f"Confidence: {self.confidence:.1f}%"
        conf_y = cy + smile_depth + 40
        
        # Đổ bóng
        self.canvas.create_text(
            cx + 2, conf_y + 2, text=conf_text,
            fill="#ebdcd0",
            font=("Courier New", conf_font, "bold")
        )
        self.canvas.create_text(
            cx, conf_y, text=conf_text,
            fill=accent_red,
            font=("Courier New", conf_font, "bold")
        )
    
    def draw_right_eye(self, height):
        """Vẽ lại mắt phải với chiều cao động để tạo hiệu ứng nhắm/mở"""
        self.canvas.delete("right_eye")
        self.canvas.create_rectangle(
            self.rx - self.eye_size/2, self.ry - height/2,
            self.rx + self.eye_size/2, self.ry + height/2,
            fill="#d32f2f", outline="", tags="right_eye"
        )
    
    def start_wink_animation(self):
        """Kích hoạt chuỗi hoạt ảnh Wink (Nháy mắt) giống intro"""
        steps = [self.eye_size, self.eye_size*0.7, self.eye_size*0.4, 6]
        for idx, h in enumerate(steps):
            self.window.after(idx * 80, lambda current_h=h: self.draw_right_eye(current_h))
        
        # Mở mắt ra lại
        self.window.after(1000, lambda: self.draw_right_eye(self.eye_size))
        
        # Nhắm mắt chốt hạ
        self.window.after(1600, lambda: self.wink_close())
    
    def wink_close(self):
        """Thu hẹp mắt phải thành nét gạch ngang"""
        self.canvas.delete("right_eye")
        dash_w = self.eye_size * 1.5
        dash_h = 8
        self.canvas.create_rectangle(
            self.rx - dash_w/2, self.ry - dash_h/2,
            self.rx + dash_w/2, self.ry + dash_h/2,
            fill="#d32f2f", outline="", tags="right_eye"
        )

# ====================== GIAO DIỆN CHÍNH ======================
class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Premium System")
        self.root.geometry("1050x820")
        self.root.minsize(980, 750)
        
        self.bg_color = "#f4ebe1"
        self.accent_red = "#d32f2f"
        self.dark_text = "#2c1d11"
        self.light_pink = "#f6cac5"
        
        self.root.configure(bg=self.bg_color)

        self.current_image_path = None
        self.display_photo = None
        
        # Laser
        self.laser_y = 0
        self.laser_direction = 5
        self.scanning_active = False
        self.scan_job = None
        self.scan_area = {"x1": 0, "y1": 0, "x2": 300, "y2": 300}
        
        # Camera
        self.cap = None
        self.camera_active = False
        self.camera_job = None
        self.frame_skip_counter = 0
        self.last_frame = None  # Lưu frame hiện tại để scan khi nhấn Space
        
        # Bind phím Space
        self.root.bind("<space>", self.manual_scan_camera)
        
        self.create_intro_screen()

    # ==================== MÀN HÌNH INTRO ====================
    def create_intro_screen(self):
        self.intro_frame = tk.Frame(self.root, bg=self.bg_color)
        self.intro_frame.place(relwidth=1, relheight=1)

        self.intro_canvas = tk.Canvas(self.intro_frame, bg=self.bg_color, highlightthickness=0)
        self.intro_canvas.pack(fill=tk.BOTH, expand=True)

        self.intro_canvas.bind("<Configure>", self.draw_intro_elements)

        self.root.after(800, self.start_wink_animation)
        self.root.after(3500, self.transition_to_main)

    def draw_intro_elements(self, event=None):
        self.intro_canvas.delete("all")
        
        w = self.intro_canvas.winfo_width()
        h = self.intro_canvas.winfo_height()
        if w < 10 or h < 10:
            return

        # Rèm đỏ
        num_scallops = 6
        scallop_w = w / num_scallops
        scallop_h = h * 0.15
        self.intro_canvas.create_rectangle(0, 0, w, scallop_h / 2, fill=self.accent_red, outline="")
        for i in range(num_scallops):
            x1 = i * scallop_w
            x2 = x1 + scallop_w
            self.intro_canvas.create_oval(x1 - 2, -scallop_h * 0.2, x2 + 2, scallop_h,
                                          fill=self.accent_red, outline="")

        # Má hồng
        cheek_r = min(w, h) * 0.12
        self.intro_canvas.create_oval(w * 0.15 - cheek_r, h * 0.55 - cheek_r,
                                      w * 0.15 + cheek_r, h * 0.55 + cheek_r,
                                      fill=self.light_pink, outline="")
        self.intro_canvas.create_oval(w * 0.85 - cheek_r, h * 0.55 - cheek_r,
                                      w * 0.85 + cheek_r, h * 0.55 + cheek_r,
                                      fill=self.light_pink, outline="")

        # Mắt trái
        eye_size = min(w, h) * 0.05
        lx = w * 0.32
        ly = h * 0.45
        self.intro_canvas.create_rectangle(lx - eye_size/2, ly - eye_size/2,
                                           lx + eye_size/2, ly + eye_size/2,
                                           fill=self.accent_red, outline="", tags="left_eye")

        # Mắt phải
        self.rx = w * 0.68
        self.ry = h * 0.45
        self.eye_size = eye_size
        self.draw_right_eye(height=self.eye_size)

        # ===== CHỮ FACE RECOGNITION (ĐÃ CHỈNH KHOẢNG CÁCH VÀ VỊ TRÍ) =====
        text_str = "FACE RECOGNITION"
        font_size = int(min(w, h) * 0.045)
        if font_size < 18:
            font_size = 18
        
        cx = w * 0.5
        cy = h * 0.58  # Đẩy xuống xíu so với trước
        total_width = w * 0.6  # Thu hẹp lại để chữ gần nhau hơn
        start_x = cx - total_width / 2
        dx = total_width / (len(text_str) - 1) if len(text_str) > 1 else 0
        smile_depth = h * 0.06  # Độ cong nhẹ

        for idx, char in enumerate(text_str):
            tx = start_x + idx * dx
            normalized_dist = (tx - cx) / (total_width / 2) if total_width > 0 else 0
            ty = cy + smile_depth * (1.0 - normalized_dist ** 2)
            
            # Đổ bóng
            self.intro_canvas.create_text(tx + 2, ty + 2, text=char,
                                          fill="#ebdcd0",
                                          font=("Georgia", font_size, "bold"),
                                          anchor="center")
            self.intro_canvas.create_text(tx, ty, text=char,
                                          fill=self.accent_red,
                                          font=("Georgia", font_size, "bold"),
                                          anchor="center")

    def draw_right_eye(self, height):
        self.intro_canvas.delete("right_eye")
        self.intro_canvas.create_rectangle(self.rx - self.eye_size/2, self.ry - height/2,
                                           self.rx + self.eye_size/2, self.ry + height/2,
                                           fill=self.accent_red, outline="", tags="right_eye")

    def start_wink_animation(self):
        steps = [self.eye_size, self.eye_size*0.7, self.eye_size*0.4, 6]
        for idx, h in enumerate(steps):
            self.root.after(idx * 80, lambda current_h=h: self.draw_right_eye(current_h))
        self.root.after(1000, lambda: self.draw_right_eye(self.eye_size))
        self.root.after(1600, lambda: self.wink_close())

    def wink_close(self):
        self.intro_canvas.delete("right_eye")
        dash_w = self.eye_size * 1.5
        dash_h = 8
        self.intro_canvas.create_rectangle(self.rx - dash_w/2, self.ry - dash_h/2,
                                           self.rx + dash_w/2, self.ry + dash_h/2,
                                           fill=self.accent_red, outline="", tags="right_eye")

    def transition_to_main(self):
        self.intro_frame.destroy()
        self.create_main_ui()

    # ==================== GIAO DIỆN CHÍNH ====================
    def create_main_ui(self):
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Header rèm đỏ
        self.header_canvas = tk.Canvas(self.main_container, bg=self.bg_color, height=85, highlightthickness=0)
        self.header_canvas.pack(fill=tk.X, side=tk.TOP)
        self.header_canvas.bind("<Configure>", self.draw_header_curtains)

        # Khung quét ở giữa
        self.center_scanner_frame = tk.Frame(self.main_container, bg=self.bg_color)
        self.center_scanner_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=(10, 10))

        scanner_title = tk.Label(self.center_scanner_frame, text="FACE SCANNER WINDOW",
                                 font=("Georgia", 13, "bold"), fg=self.accent_red, bg=self.bg_color)
        scanner_title.pack(anchor="w", pady=(0, 6))

        self.scan_box_outer = tk.Frame(self.center_scanner_frame, bg=self.accent_red, bd=3)
        self.scan_box_outer.pack(fill=tk.BOTH, expand=True)

        self.image_canvas = tk.Canvas(self.scan_box_outer, bg="#fbf8f5", highlightthickness=0)
        self.image_canvas.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        self.image_canvas.create_text(150, 150,
                                      text="[ NO IMAGE SELECTED ]\n\nClick 'Choose Image' or 'Sample Images'\n\n📸 CAMERA MODE: Press SPACE to scan 📸",
                                      fill="#a89a8f", font=("Courier", 11, "bold"),
                                      justify=tk.CENTER, tags="placeholder_text")
        self.image_canvas.bind("<Configure>", self.center_placeholder_text)

        # Panel dưới
        self.bottom_panel = tk.Frame(self.main_container, bg=self.bg_color)
        self.bottom_panel.pack(fill=tk.X, side=tk.BOTTOM, padx=25, pady=(5, 10))

        # Nút bấm
        right_col = tk.Frame(self.bottom_panel, bg=self.bg_color)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(right_col, text="SYSTEM ACTIONS", font=("Georgia", 11, "bold"),
                 fg=self.accent_red, bg=self.bg_color).pack(anchor="w", pady=(5, 8))

        buttons_container = tk.Frame(right_col, bg=self.bg_color)
        buttons_container.pack(fill=tk.X, pady=2)

        btn_choose = tk.Button(buttons_container, text="📁 CHOOSE IMAGE",
                               font=("Arial", 10, "bold"), bg=self.accent_red, fg="white",
                               activebackground="#b71c1c", relief=tk.FLAT, bd=0, height=2,
                               cursor="hand2", command=self.choose_image)
        btn_choose.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        btn_samples = tk.Button(buttons_container, text="🧪 SAMPLE IMAGES",
                                font=("Arial", 10, "bold"), bg="#fcf8f5", fg=self.accent_red,
                                activebackground="#ebdcd0", highlightbackground=self.accent_red,
                                highlightthickness=2, relief=tk.FLAT, bd=0, height=2,
                                cursor="hand2", command=self.show_sample_dialog)
        btn_samples.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.btn_realtime = tk.Button(buttons_container, text="📹 CAMERA MODE",
                                      font=("Arial", 10, "bold"), bg=self.accent_red, fg="white",
                                      activebackground="#b71c1c", relief=tk.FLAT, bd=0, height=2,
                                      cursor="hand2", command=self.toggle_camera)
        self.btn_realtime.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Hướng dẫn phím Space
        space_hint = tk.Label(right_col, text="💡 TIP: Press SPACE to scan when Camera is ON",
                              font=("Arial", 9, "italic"), fg="#e65100", bg=self.bg_color)
        space_hint.pack(pady=(8, 2))

        

    def draw_header_curtains(self, event=None):
        self.header_canvas.delete("all")
        w = self.header_canvas.winfo_width()
        h = self.header_canvas.winfo_height()
        if w < 10 or h < 10:
            return

        num_scallops = 10
        scallop_w = w / num_scallops
        scallop_h = h * 0.75
        self.header_canvas.create_rectangle(0, 0, w, scallop_h * 0.4, fill=self.accent_red, outline="")
        for i in range(num_scallops):
            x1 = i * scallop_w
            x2 = x1 + scallop_w
            self.header_canvas.create_oval(x1 - 2, -scallop_h * 0.2, x2 + 2, scallop_h,
                                          fill=self.accent_red, outline="")

    def center_placeholder_text(self, event=None):
        w = self.image_canvas.winfo_width()
        h = self.image_canvas.winfo_height()
        self.image_canvas.coords("placeholder_text", w/2, h/2)

    # ==================== LASER SCAN ====================
    def start_laser_scan_effect(self):
        self.scanning_active = True
        self.laser_y = self.scan_area["y1"]
        self.laser_direction = 4
        self.run_laser_scan()

    def run_laser_scan(self):
        if not self.scanning_active:
            return
        y1, y2 = self.scan_area["y1"], self.scan_area["y2"]
        x1, x2 = self.scan_area["x1"], self.scan_area["x2"]
        self.image_canvas.delete("laser_line")
        self.image_canvas.delete("laser_glow")
        self.laser_y += self.laser_direction
        if self.laser_y >= y2 or self.laser_y <= y1:
            self.laser_direction = -self.laser_direction
            self.laser_y = max(y1, min(self.laser_y, y2))
        self.image_canvas.create_line(x1, self.laser_y, x2, self.laser_y,
                                      fill="#ff1744", width=3, tags="laser_line")
        self.image_canvas.create_rectangle(x1, self.laser_y - 4, x2, self.laser_y + 4,
                                           fill="", outline="#ff8a80", width=1, tags="laser_glow")
        self.scan_job = self.root.after(16, self.run_laser_scan)

    def stop_laser_scan_effect(self):
        self.scanning_active = False
        if self.scan_job:
            self.root.after_cancel(self.scan_job)
            self.scan_job = None
        self.image_canvas.delete("laser_line")
        self.image_canvas.delete("laser_glow")

    # ==================== CAMERA (CHỈ SCAN KHI NHẤN SPACE) ====================
    def toggle_camera(self):
        if self.camera_active:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        self.stop_laser_scan_effect()
        self.image_canvas.delete("all")
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Không thể mở Camera!")
            return

        self.camera_active = True
        self.btn_realtime.config(text="⏹ STOP CAMERA", bg="#c62828")
        self.frame_skip_counter = 0
        self.last_frame = None
        
        self.update_camera_frame()

    def stop_camera(self):
        self.camera_active = False
        if self.camera_job:
            self.root.after_cancel(self.camera_job)
            self.camera_job = None
        if self.cap:
            self.cap.release()
            self.cap = None
        self.btn_realtime.config(text="📹 CAMERA MODE", bg="#c62828")
        self.image_canvas.delete("all")
        w = self.image_canvas.winfo_width()
        h = self.image_canvas.winfo_height()
        self.image_canvas.create_text(w/2, h/2,
                                      text="[ CAMERA STOPPED ]\n\nPress CAMERA MODE to start\nThen press SPACE to scan",
                                      fill="#a89a8f", font=("Courier", 11, "bold"),
                                      justify=tk.CENTER, tags="placeholder_text")

    def manual_scan_camera(self, event=None):
        """Nhấn Space để scan frame hiện tại"""
        if self.camera_active and self.last_frame is not None:
            # Hiệu ứng scan đẹp mắt
            self.scan_area = {"x1": 0, "y1": 0, "x2": self.image_canvas.winfo_width(),
                              "y2": self.image_canvas.winfo_height()}
            self.start_laser_scan_effect()
            
            # Xử lý nhận diện sau 0.8s
            self.root.after(800, lambda: self.process_camera_scan(self.last_frame))
        elif self.camera_active and self.last_frame is None:
            messagebox.showinfo("Info", "Đang khởi tạo camera, chờ xíu rồi thử lại nha!")

    def process_camera_scan(self, frame):
        """Xử lý frame từ camera và hiện popup"""
        self.stop_laser_scan_effect()
        
        try:
            # Phát hiện khuôn mặt
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
            
            if len(faces) > 0:
                x, y, w, h = faces[0]
                # Cắt mặt
                face_crop = frame[y:y+h, x:x+w]
                if face_crop.size > 0:
                    face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
                    face_resized = cv2.resize(face_rgb, (200, 200))
                    name, confidence = predict_frame(face_resized)
                    
                    # HIỂN THỊ POPUP THAY VÌ IN LÊN LABEL
                    ResultPopup(self.root, name, confidence)
                else:
                    ResultPopup(self.root, "No Face", 0.0)
            else:
                ResultPopup(self.root, "No Face Detected", 0.0)
                
        except Exception as e:
            print(f"Lỗi scan: {e}")
            ResultPopup(self.root, "Scan Error", 0.0)

    def update_camera_frame(self):
        if not self.camera_active or self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.stop_camera()
            return

        frame = cv2.flip(frame, 1)
        self.last_frame = frame.copy()  # Lưu lại để scan khi nhấn Space
        
        # Phát hiện và vẽ khung mặt
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
        
        for (x, y, w, h) in faces:
            length = int(w * 0.25)
            cv2.line(frame, (x, y), (x + length, y), (47, 47, 211), 3)
            cv2.line(frame, (x, y), (x, y + length), (47, 47, 211), 3)
            cv2.line(frame, (x + w, y), (x + w - length, y), (47, 47, 211), 3)
            cv2.line(frame, (x + w, y), (x + w, y + length), (47, 47, 211), 3)
            cv2.line(frame, (x, y + h), (x + length, y + h), (47, 47, 211), 3)
            cv2.line(frame, (x, y + h), (x, y + h - length), (47, 47, 211), 3)
            cv2.line(frame, (x + w, y + h), (x + w - length, y + h), (47, 47, 211), 3)
            cv2.line(frame, (x + w, y + h), (x + w, y + h - length), (47, 47, 211), 3)
            break
        
        # Hiển thị frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(frame_rgb)
        canvas_w = self.image_canvas.winfo_width()
        canvas_h = self.image_canvas.winfo_height()
        if canvas_w < 10:
            canvas_w = 600
        if canvas_h < 10:
            canvas_h = 450
        pil_img.thumbnail((canvas_w, canvas_h))
        self.display_photo = ImageTk.PhotoImage(pil_img)
        
        self.image_canvas.delete("all")
        self.image_canvas.create_image(canvas_w/2, canvas_h/2,
                                       image=self.display_photo, anchor="center")
        self.image_canvas.create_text(55, 25, text="● LIVE", fill="#ff1744",
                                      font=("Courier", 11, "bold"))
        self.image_canvas.create_text(canvas_w - 55, 25, text="SPACE → SCAN",
                                      fill="#2e7d32", font=("Courier", 10, "bold"))

        self.camera_job = self.root.after(30, self.update_camera_frame)

    # ==================== XỬ LÝ FILE ẢNH ====================
    def process_and_display(self, img_path):
        self.stop_camera()
        self.stop_laser_scan_effect()
        self.image_canvas.delete("all")

        try:
            pil_img = Image.open(img_path)
            canvas_w = self.image_canvas.winfo_width()
            canvas_h = self.image_canvas.winfo_height()
            if canvas_w < 10:
                canvas_w = 600
            if canvas_h < 10:
                canvas_h = 450
            pil_img.thumbnail((canvas_w, canvas_h))
            img_w, img_h = pil_img.size
            self.display_photo = ImageTk.PhotoImage(pil_img)
            x_offset = (canvas_w - img_w) // 2
            y_offset = (canvas_h - img_h) // 2
            self.image_canvas.create_image(x_offset, y_offset,
                                           image=self.display_photo, anchor="nw",
                                           tags="processed_image")
            
            # 🎯 SỬA: Quét TOÀN BỘ KHUNG CANVAS (viền trắng) thay vì chỉ ảnh
            self.scan_area["x1"] = 0  # Quét từ mép trái của canvas
            self.scan_area["y1"] = 0  # Quét từ mép trên của canvas
            self.scan_area["x2"] = canvas_w  # Đến mép phải
            self.scan_area["y2"] = canvas_h  # Đến mép dưới
            
        except Exception as e:
            messagebox.showerror("Error", f"Không thể tải ảnh: {e}")
            return

        self.start_laser_scan_effect()
        self.root.after(1200, lambda: self.reveal_ai_prediction(img_path))

    def reveal_ai_prediction(self, img_path):
        if self.camera_active:
            return
        self.stop_laser_scan_effect()
        try:
            img_bgr = cv2.imread(img_path)
            if img_bgr is not None:
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                name, confidence = predict_frame(img_rgb)
            else:
                name, confidence = "Unknown", 0.0
        except Exception as e:
            name, confidence = "Error", 0.0
        
        # HIỂN THỊ POPUP THAY VÌ LABEL
        ResultPopup(self.root, name, confidence)
        self.current_image_path = img_path

    def choose_image(self):
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh chứa khuôn mặt",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("All files", "*.*")]
        )
        if file_path:
            self.process_and_display(file_path)

    def show_sample_dialog(self):
        sample_images = []
        if os.path.exists(data_dir):
            sample_images = [f for f in os.listdir(data_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        if not sample_images:
            sample_images = ["anh_test_1.jpg", "anh_test_2.jpg", "anh_test_3.jpg"]

        dialog = tk.Toplevel(self.root)
        dialog.title("Select Sample Face")
        dialog.geometry("450x380")
        dialog.resizable(False, False)
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="🧪 SELECT SAMPLE IMAGE",
                 font=("Georgia", 13, "bold"), fg=self.accent_red, bg=self.bg_color).pack(pady=(15, 5))
        tk.Label(dialog, text="Select one of the images in your test pool:",
                 font=("Arial", 10, "italic"), fg="#6d5c50", bg=self.bg_color).pack(pady=(0, 10))

        list_frame = tk.Frame(dialog, bg=self.accent_red, bd=2)
        list_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)

        listbox = tk.Listbox(list_frame, font=("Courier New", 11, "bold"),
                             bg="#fdfbf9", fg=self.dark_text,
                             selectbackground=self.accent_red, selectforeground="white",
                             highlightthickness=0, bd=0)
        listbox.pack(pady=3, padx=3, fill=tk.BOTH, expand=True)

        for img in sample_images:
            listbox.insert(tk.END, f" 👤 {img}")

        def on_select():
            selection = listbox.curselection()
            if selection:
                img_name = sample_images[selection[0]]
                img_path = os.path.join(data_dir, img_name)
                if not os.path.exists(img_path):
                    img_path = self.create_demo_image_file(img_name)
                dialog.destroy()
                self.process_and_display(img_path)
            else:
                messagebox.showwarning("Warning", "Please select an image first!")

        btn_frame = tk.Frame(dialog, bg=self.bg_color)
        btn_frame.pack(pady=(10, 20))
        btn_confirm = tk.Button(btn_frame, text="CONFIRM SCAN",
                                font=("Arial", 10, "bold"), bg=self.accent_red, fg="white",
                                activebackground="#b71c1c", relief=tk.FLAT, bd=0, padx=15, pady=8,
                                cursor="hand2", command=on_select)
        btn_confirm.pack(side=tk.LEFT, padx=10)
        btn_cancel = tk.Button(btn_frame, text="CANCEL",
                               font=("Arial", 10, "bold"), bg="#dfcfc3", fg=self.dark_text,
                               activebackground="#ebdcd0", relief=tk.FLAT, bd=0, padx=15, pady=8,
                               cursor="hand2", command=dialog.destroy)
        btn_cancel.pack(side=tk.LEFT, padx=10)

    def create_demo_image_file(self, filename):
        temp_dir = os.path.join(os.path.expanduser("~"), "FaceRecogDemo")
        os.makedirs(temp_dir, exist_ok=True)
        img_path = os.path.join(temp_dir, filename)
        canvas_img = np.zeros((400, 400, 3), dtype=np.uint8)
        canvas_img[:] = [225, 235, 244]
        cv2.circle(canvas_img, (200, 200), 100, (0, 215, 255), -1)
        cv2.circle(canvas_img, (200, 200), 100, (0, 165, 255), 3)
        cv2.circle(canvas_img, (165, 180), 12, (25, 29, 44), -1)
        cv2.circle(canvas_img, (235, 180), 12, (25, 29, 44), -1)
        cv2.ellipse(canvas_img, (200, 220), (50, 30), 0, 0, 180, (25, 29, 44), 6)
        cv2.putText(canvas_img, filename, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (43, 29, 18), 2)
        cv2.imwrite(img_path, canvas_img)
        return img_path


# ====================== KHỞI CHẠY ======================
if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()