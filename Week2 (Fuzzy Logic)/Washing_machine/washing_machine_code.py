import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import tkinter as tk
from tkinter import ttk, messagebox
import time

def create_fuzzy_sim():
    # Antecedents & Consequents
    load = ctrl.Antecedent(np.arange(0, 11, 1), 'load')
    dirt_level = ctrl.Antecedent(np.arange(0, 11, 1), 'dirt_level')
    fabric_type = ctrl.Antecedent(np.arange(0, 11, 1), 'fabric_type')
    dirt_type = ctrl.Antecedent(np.arange(0, 11, 1), 'dirt_type')

    wash_time = ctrl.Consequent(np.arange(0, 121, 1), 'wash_time')
    water_level = ctrl.Consequent(np.arange(0, 81, 1), 'water_level')
    water_temp = ctrl.Consequent(np.arange(20, 91, 1), 'water_temp')

    # Membership Functions
    load['small'] = fuzz.trimf(load.universe, [0, 0, 5])
    load['medium'] = fuzz.trimf(load.universe, [0, 5, 10])
    load['large'] = fuzz.trimf(load.universe, [5, 10, 10])

    dirt_level['low'] = fuzz.trimf(dirt_level.universe, [0, 0, 5])
    dirt_level['normal'] = fuzz.trimf(dirt_level.universe, [0, 5, 10])
    dirt_level['high'] = fuzz.trimf(dirt_level.universe, [5, 10, 10])

    dirt_type['mo_hoi'] = fuzz.trimf(dirt_type.universe, [0, 0, 5])
    dirt_type['bun_dat'] = fuzz.trimf(dirt_type.universe, [0, 5, 10])
    dirt_type['dau_mo'] = fuzz.trimf(dirt_type.universe, [5, 10, 10])

    fabric_type['delicate'] = fuzz.trimf(fabric_type.universe, [0, 0, 3])
    fabric_type['regular'] = fuzz.trimf(fabric_type.universe, [2, 5, 8])
    fabric_type['heavy'] = fuzz.trimf(fabric_type.universe, [7, 10, 10])

    wash_time['short'] = fuzz.trimf(wash_time.universe, [0, 0, 25])
    wash_time['medium'] = fuzz.trimf(wash_time.universe, [20, 35, 50])
    wash_time['long'] = fuzz.trimf(wash_time.universe, [45, 70, 70])

    water_level['low'] = fuzz.trimf(water_level.universe, [0, 0, 40])
    water_level['medium'] = fuzz.trimf(water_level.universe, [0, 40, 80])
    water_level['high'] = fuzz.trimf(water_level.universe, [40, 80, 80])

    water_temp['lanh'] = fuzz.trimf(water_temp.universe, [20, 20, 55])
    water_temp['am'] = fuzz.trimf(water_temp.universe, [20, 55, 90])
    water_temp['nong'] = fuzz.trimf(water_temp.universe, [55, 90, 90])

    # Rules (Tạo danh sách 45 rule như code của bạn)
    # Tải & Bẩn
    r1 = ctrl.Rule(load['small'] & dirt_level['low'], [wash_time['short'], water_level['low']])
    r2 = ctrl.Rule(load['small'] & dirt_level['normal'], [wash_time['medium'], water_level['medium']])
    r3 = ctrl.Rule(load['small'] & dirt_level['high'], [wash_time['long'], water_level['medium']])
    r4 = ctrl.Rule(load['medium'] & dirt_level['low'], [wash_time['medium'], water_level['medium']])
    r5 = ctrl.Rule(load['medium'] & dirt_level['normal'], [wash_time['long'], water_level['medium']])
    r6 = ctrl.Rule(load['medium'] & dirt_level['high'], [wash_time['long'], water_level['high']])
    r7 = ctrl.Rule(load['large'] & dirt_level['low'], [wash_time['medium'], water_level['high']])
    r8 = ctrl.Rule(load['large'] & dirt_level['normal'], [wash_time['long'], water_level['high']])
    r9 = ctrl.Rule(load['large'] & dirt_level['high'], [wash_time['long'], water_level['high']])
    # Vải & Loại bẩn
    r10 = ctrl.Rule(fabric_type['delicate'] & dirt_type['mo_hoi'], [water_temp['lanh'], wash_time['short']])
    r11 = ctrl.Rule(fabric_type['delicate'] & dirt_type['bun_dat'], [water_temp['am'], wash_time['medium']])
    r12 = ctrl.Rule(fabric_type['delicate'] & dirt_type['dau_mo'], [water_temp['am'], wash_time['medium']])
    r13 = ctrl.Rule(fabric_type['regular'] & dirt_type['mo_hoi'], [water_temp['lanh'], wash_time['medium']])
    r14 = ctrl.Rule(fabric_type['regular'] & dirt_type['bun_dat'], [water_temp['am'], wash_time['medium']])
    r15 = ctrl.Rule(fabric_type['regular'] & dirt_type['dau_mo'], [water_temp['nong'], wash_time['long']])
    r16 = ctrl.Rule(fabric_type['heavy'] & dirt_type['mo_hoi'], [water_temp['am'], wash_time['medium']])
    r17 = ctrl.Rule(fabric_type['heavy'] & dirt_type['bun_dat'], [water_temp['nong'], wash_time['long']])
    r18 = ctrl.Rule(fabric_type['heavy'] & dirt_type['dau_mo'], [water_temp['nong'], wash_time['long']])
    # Bẩn & Loại bẩn
    r19 = ctrl.Rule(dirt_level['low'] & dirt_type['mo_hoi'], [wash_time['short'], water_temp['lanh']])
    r20 = ctrl.Rule(dirt_level['low'] & dirt_type['bun_dat'], [wash_time['short'], water_temp['lanh']])
    r21 = ctrl.Rule(dirt_level['low'] & dirt_type['dau_mo'], [wash_time['medium'], water_temp['am']])
    r22 = ctrl.Rule(dirt_level['normal'] & dirt_type['mo_hoi'], [wash_time['medium'], water_temp['lanh']])
    r23 = ctrl.Rule(dirt_level['normal'] & dirt_type['bun_dat'], [wash_time['medium'], water_temp['am']])
    r24 = ctrl.Rule(dirt_level['normal'] & dirt_type['dau_mo'], [wash_time['long'], water_temp['nong']])
    r25 = ctrl.Rule(dirt_level['high'] & dirt_type['mo_hoi'], [wash_time['medium'], water_temp['am']])
    r26 = ctrl.Rule(dirt_level['high'] & dirt_type['bun_dat'], [wash_time['long'], water_temp['nong']])
    r27 = ctrl.Rule(dirt_level['high'] & dirt_type['dau_mo'], [wash_time['long'], water_temp['nong']])
    # Tải & Vải
    r28 = ctrl.Rule(load['small'] & fabric_type['delicate'], [water_level['low'], water_temp['lanh']])
    r29 = ctrl.Rule(load['small'] & fabric_type['regular'], [water_level['low'], water_temp['am']])
    r30 = ctrl.Rule(load['small'] & fabric_type['heavy'], [water_level['medium'], water_temp['am']])
    r31 = ctrl.Rule(load['medium'] & fabric_type['delicate'], [water_level['medium'], water_temp['lanh']])
    r32 = ctrl.Rule(load['medium'] & fabric_type['regular'], [water_level['medium'], water_temp['am']])
    r33 = ctrl.Rule(load['medium'] & fabric_type['heavy'], [water_level['high'], water_temp['nong']])
    r34 = ctrl.Rule(load['large'] & fabric_type['delicate'], [water_level['high'], water_temp['am']])
    r35 = ctrl.Rule(load['large'] & fabric_type['regular'], [water_level['high'], water_temp['am']])
    r36 = ctrl.Rule(load['large'] & fabric_type['heavy'], [water_level['high'], water_temp['nong']])
    # Vải & Mức bẩn
    r37 = ctrl.Rule(fabric_type['delicate'] & dirt_level['low'], [wash_time['short'], water_temp['lanh']])
    r38 = ctrl.Rule(fabric_type['delicate'] & dirt_level['normal'], [wash_time['medium'], water_temp['lanh']])
    r39 = ctrl.Rule(fabric_type['delicate'] & dirt_level['high'], [wash_time['medium'], water_temp['am']])
    r40 = ctrl.Rule(fabric_type['regular'] & dirt_level['low'], [wash_time['short'], water_temp['lanh']])
    r41 = ctrl.Rule(fabric_type['regular'] & dirt_level['normal'], [wash_time['medium'], water_temp['am']])
    r42 = ctrl.Rule(fabric_type['regular'] & dirt_level['high'], [wash_time['long'], water_temp['nong']])
    r43 = ctrl.Rule(fabric_type['heavy'] & dirt_level['low'], [wash_time['medium'], water_temp['am']])
    r44 = ctrl.Rule(fabric_type['heavy'] & dirt_level['normal'], [wash_time['long'], water_temp['am']])
    r45 = ctrl.Rule(fabric_type['heavy'] & dirt_level['high'], [wash_time['long'], water_temp['nong']])

    system = ctrl.ControlSystem([r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12,r13,r14,r15,r16,r17,r18,r19,r20,r21,r22,r23,r24,r25,r26,r27,r28,r29,r30,r31,r32,r33,r34,r35,r36,r37,r38,r39,r40,r41,r42,r43,r44,r45])
    return ctrl.ControlSystemSimulation(system)


class UltimateWasherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Premium Washer - Sync Fixed")
        self.root.geometry("900x850")
        self.root.configure(bg="#f5f6fa")
        
        try:
            self.sim = create_fuzzy_sim()
        except NameError:
            messagebox.showerror("Lỗi", "Thiếu hàm create_fuzzy_sim() rồi!")
            
        self.angle = 0
        self.is_washing = False

        display_frame = tk.Frame(root, bg="#2d3436", bd=4, relief="sunken")
        display_frame.pack(pady=15, padx=50, fill="x")
        self.led_status = tk.Label(display_frame, text="HỆ THỐNG SẴN SÀNG", font=("Consolas", 18, "bold"), bg="#2d3436", fg="#00ff00")
        self.led_status.pack(pady=5)
        self.led_info = tk.Label(display_frame, text="Nhập số hoặc kéo thanh trượt", font=("Consolas", 10), bg="#2d3436", fg="#00ff00")
        self.led_info.pack(pady=5)

        mid_container = tk.Frame(root, bg="#f5f6fa")
        mid_container.pack(fill="both", expand=True, padx=20)

        self.canvas = tk.Canvas(mid_container, width=350, height=350, bg="#f5f6fa", highlightthickness=0)
        self.canvas.pack(side="left", padx=20)
        self.draw_washer(0)

        guide_frame = tk.LabelFrame(mid_container, text=" 📖 CẨM NANG THÔNG SỐ ", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#ff4757", padx=15, pady=15)
        guide_frame.pack(side="right", fill="both", expand=True, padx=10)
        guide_data = [("Tải trọng", "0-3: Ít | 4-7: Vừa | 8-10: Nhiều"), ("Độ bẩn", "0-3: Sơ | 4-7: Thường | 8-10: Rất bẩn"), ("Loại vải", "0-3: Lụa/Mỏng | 4-7: Thường | 8-10: Jean"), ("Vết bẩn", "0-3: Mồ hôi | 4-7: Bùn đất | 8-10: Dầu mỡ")]
        for title, desc in guide_data:
            f = tk.Frame(guide_frame, bg="#ffffff"); f.pack(fill="x", pady=5)
            tk.Label(f, text=title, font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#2d3436").pack(anchor="w")
            tk.Label(f, text=desc, font=("Segoe UI", 9), bg="#ffffff", fg="#747d8c").pack(anchor="w")

        ctrl_panel = tk.Frame(root, bg="#dfe6e9", pady=20)
        ctrl_panel.pack(fill="x", side="bottom")
        input_sub_frame = tk.Frame(ctrl_panel, bg="#dfe6e9"); input_sub_frame.pack()

        self.vars = {}
        fields = [("TẢI TRỌNG", "load"), ("ĐỘ BẨN", "dirt_level"), ("LOẠI VẢI", "fabric_type"), ("VẾT BẨN", "dirt_type")]

        for i, (label_text, key) in enumerate(fields):
            row, col = i // 2, (i % 2) * 3
            tk.Label(input_sub_frame, text=label_text, font=("Segoe UI", 9, "bold"), bg="#dfe6e9", fg="#2d3436").grid(row=row, column=col, padx=10, pady=10)
            
            v = tk.IntVar(value=5)
            self.vars[key] = v
            
            slider = tk.Scale(input_sub_frame, from_=0, to=10, orient="horizontal", resolution=1, variable=v, showvalue=0, length=120, bg="#dfe6e9", highlightthickness=0)
            slider.grid(row=row, column=col+1, padx=5)
            
            entry = tk.Entry(input_sub_frame, width=4, font=("Consolas", 11, "bold"), justify="center")
            entry.insert(0, "5")
            entry.grid(row=row, column=col+2, padx=5)


            def update_entry(var, ent):
                ent.delete(0, tk.END)
                ent.insert(0, str(var.get()))
            
   
            def update_slider(event, var, ent):
                try:
                    val = ent.get()
                    if val == "": return 
                    num = int(val)
                    if 0 <= num <= 10:
                        var.set(num)
                except ValueError:
                    pass
            v.trace_add("write", lambda *args, var=v, ent=entry: update_entry(var, ent))
           
            entry.bind("<KeyRelease>", lambda e, var=v, ent=entry: update_slider(e, var, ent))
           
            entry.bind("<FocusOut>", lambda e, var=v, ent=entry: update_entry(var, ent))

        btn_sub_frame = tk.Frame(ctrl_panel, bg="#dfe6e9"); btn_sub_frame.pack(pady=10)
        self.btn_start = tk.Button(btn_sub_frame, text="GIẶT NGAY", font=("Segoe UI", 12, "bold"), bg="#ff4757", fg="white", width=15, height=2, bd=0, command=self.process_wash)
        self.btn_start.pack(side="left", padx=10)
        self.btn_stop = tk.Button(btn_sub_frame, text="DỪNG", font=("Segoe UI", 12, "bold"), bg="#2d3436", fg="white", width=10, height=2, bd=0, command=self.stop_wash)
        self.btn_stop.pack(side="left", padx=10)

    def draw_washer(self, angle):
        self.canvas.delete("all")
        cx, cy, r = 175, 175, 130
        self.canvas.create_rectangle(cx-150, cy-150, cx+150, cy+170, fill="#ffffff", outline="#dfe6e9", width=2)
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#dfe6e9", outline="#b2bec3", width=5)
        self.canvas.create_oval(cx-r+20, cy-r+20, cx+r-20, cy+r-20, fill="#f1f2f6", outline="#ff4757", width=2)
        rad = np.radians(angle)
        for i in range(3):
            a = rad + i * (2 * np.pi / 3)
            self.canvas.create_line(cx, cy, cx + 90*np.cos(a), cy + 90*np.sin(a), width=10, fill="#ff4757", capstyle="round")

    def process_wash(self):
        if self.is_washing: return
        try:
            for k in self.vars: self.sim.input[k] = self.vars[k].get()
            self.sim.compute()
            self.is_washing = True
            self.led_status.config(text="ĐANG GIẶT...", fg="#f1c40f")
            self.animate(80)
        except: messagebox.showwarning("Lỗi", "Kiểm tra lại thông số!")

    def stop_wash(self):
        self.is_washing = False
        self.led_status.config(text="ĐÃ DỪNG", fg="#ff4757")
        self.btn_start.config(state="normal")

    def animate(self, count):
        if not self.is_washing: return
        if count > 0:
            self.angle = (self.angle + 30) % 360
            self.draw_washer(self.angle)
            self.root.after(40, self.animate, count - 1)
        else:
            self.is_washing = False
            self.btn_start.config(state="normal")
            t, w, temp = int(self.sim.output['wash_time']), int(self.sim.output['water_level']), int(self.sim.output['water_temp'])
            self.led_status.config(text="HOÀN THÀNH!", fg="#00ff00")
            self.led_info.config(text=f"{t} phút | {w} Lít | {temp} độ C")

if __name__ == "__main__":
    app_root = tk.Tk()
    my_app = UltimateWasherApp(app_root)
    app_root.mainloop()