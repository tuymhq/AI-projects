import streamlit as st
import json
import math
import random
import os
import requests
import time
import pandas as pd
from collections import defaultdict
from datetime import datetime
import folium
from streamlit_folium import st_folium
import base64


def get_img_base64(img_file):
    with open(img_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_font_base64(font_file):
    with open(font_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

font_base64 = get_font_base64("DFVN Soyuz Grotesk 2.0.ttf")

st.set_page_config(
    page_title="Harmoni - Food Advisor",
    page_icon="🥢",
    layout="wide",
    initial_sidebar_state="collapsed"
)


if 'loading_done' not in st.session_state:
    st.session_state.loading_done = False

if not st.session_state.loading_done:
    with open("load.gif", "rb") as f:
        gif_base64 = base64.b64encode(f.read()).decode()
    
    st.markdown(f"""
    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, #d4206e, #b81a5c); z-index: 999999; display: flex; justify-content: center; align-items: center;">
        <img src="data:image/gif;base64,{gif_base64}" style="width: 100%; height: 100%; object-fit: cover;">
    </div>
    """, unsafe_allow_html=True)
    
    time.sleep(4)
    st.session_state.loading_done = True
    st.rerun()
img_base64 = get_img_base64("bg_1.jpg")
shake_img_base64 = get_img_base64("lacque.png")
que_img_base64 = get_img_base64("que.png")
box_ketqua_base64 = get_img_base64("box_ketqua.png")
lacque_btn_base64 = get_img_base64("lac_que.png")
logo_base64 = get_img_base64("snack-3.png")
decor_left = get_img_base64("trang_tri_left.png")
decor_right = get_img_base64("trang_tri_right.png")


st.markdown(f"""
<style>
    @font-face {{
        font-family: 'SoyuzGrotesk';
        src: url(data:font/ttf;base64,{font_base64}) format('truetype');
    }}

    .stApp {{
        background: linear-gradient(
            to bottom, 
            #ffffff 0%,
            #fff0f5 30%,
            #ff69b4 80%,
            #ff1493 100%
        ) !important;
        background-attachment: fixed;
    }}

    .fortune-card {{
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 30px;
        border: 2px solid #ffd700;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        padding: 2rem;
        margin-bottom: 1.5rem;
    }}

    .result-box-container {{
        background-image: url('data:image/png;base64,{box_ketqua_base64}');
        background-size: 100% 100%;
        background-repeat: no-repeat;
        background-position: center;
        width: 100%;
        min-height: 550px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 60px 40px;
        margin-top: 20px;
    }}

    .mon-an-title {{
        font-family: 'SoyuzGrotesk' !important;
        color: #d4206e !important;
        font-size: 45px !important;
        font-weight: bold;
        text-align: center;
        line-height: 1.2;
        margin-bottom: 10px;
    }}

    .explain-text {{
        font-family: 'SoyuzGrotesk' !important;
        color: #333333 !important;
        font-size: 18px !important;
        text-align: center;
        max-width: 80%;
    }}

    h1, h2, h3, h4, p, label, span, .stMarkdown {{
        color: #ffffff !important;
        text-shadow: 1px 2px 4px rgba(0,0,0,0.3);
        font-family: 'SoyuzGrotesk' !important;
    }}

    .info-label {{
        background: #ffd700;
        border-radius: 50px;
        padding: 5px 15px;
        display: inline-block;
        margin: 5px;
        color: #d4206e !important;
        font-weight: bold;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        text-shadow: none !important;
    }}

    .stButton > button {{
        background: #ffd700 !important;
        color: #d4206e !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.8rem 2rem !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        transition: 0.3s !important;
    }}

    .stButton > button:hover {{
        transform: scale(1.05);
        background: #ffffff !important;
    }}

    @keyframes shakeAnim {{
        0% {{ transform: translate(0,0) rotate(0deg); }}
        25% {{ transform: translate(-12px,-8px) rotate(-8deg); }}
        50% {{ transform: translate(12px,8px) rotate(8deg); }}
        75% {{ transform: translate(-6px,6px) rotate(-5deg); }}
        100% {{ transform: translate(0,0) rotate(0deg); }}
    }}

    @keyframes flyQue {{
        0% {{ transform: translateY(150px) scale(0.3); opacity: 0; }}
        50% {{ transform: translateY(-20px) scale(1.1); opacity: 1; }}
        100% {{ transform: translateY(0) scale(1); opacity: 1; }}
    }}

    @keyframes gentleShake {{
        0% {{ transform: translate(0,0) rotate(0deg); }}
        25% {{ transform: translate(-3px,-2px) rotate(-2deg); }}
        50% {{ transform: translate(3px,2px) rotate(2deg); }}
        75% {{ transform: translate(-2px,1px) rotate(-1deg); }}
        100% {{ transform: translate(0,0) rotate(0deg); }}
    }}

    @keyframes textFade {{
        0% {{ opacity: 0; transform: scale(0.8); }}
        100% {{ opacity: 1; transform: scale(1); }}
    }}

    .restaurant-card {{
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(5px);
        border-radius: 20px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255, 215, 0, 0.5);
        transition: 0.3s;
    }}

    .restaurant-card:hover {{
        background: rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-3px);
    }}

    .moving-decor-container {{
        width: 100%;
        display: flex;
        justify-content: space-between;
        padding: 0 20px;
        margin-top: -200px;
        margin-bottom: -100px;
        pointer-events: none;
    }}
    
    .moving-decor-item {{
        width: 180px;
        opacity: 0.9;
        filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.1));
        animation: floatDecor 3s ease-in-out infinite;
    }}
    
    @keyframes floatDecor {{
        0%, 100% {{ transform: translateY(0) rotate(0deg); }}
        50% {{ transform: translateY(-10px) rotate(5deg); }}
    }}

    .footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(212, 32, 110, 0.95);
        padding: 10px;
        text-align: center;
        z-index: 1000;
    }}
</style>
""", unsafe_allow_html=True)


UEH_CAMPUSES = {
    "A (59C Nguyễn Đình Chiểu, Q.3)": {"coords": (10.783219801437031, 106.69463600935255), "code": "A"},
    "B (279 Nguyễn Tri Phương, Q.10)": {"coords": (10.76126399257767, 106.66831508051604), "code": "B"},
    "N (Khu Đô Thị Mới Nguyễn Văn Linh, Q.7)": {"coords": (10.706170578558458, 106.64006059400619), "code": "N"},
    "H (Hoàng Diệu, Q.4)": {"coords": (10.7962007277731, 106.67221551659115), "code": "H"}
}


@st.cache_data(ttl=3600, show_spinner=False)
def get_route(start_lat, start_lng, end_lat, end_lng):
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lng},{start_lat};{end_lng},{end_lat}?overview=full&geometries=geojson"
    try:
        resp = requests.get(url, timeout=8)
        data = resp.json()
        if data.get('code') == 'Ok':
            coords = data['routes'][0]['geometry']['coordinates']
            route = [(lat, lng) for lng, lat in coords]
            return route
        else:
            return None
    except Exception as e:
        return None


@st.cache_data
def load_restaurants_from_csv():
    restaurants = []
    csv_paths = [
        "restaurants.csv",
        os.path.join(os.path.dirname(__file__), "restaurants.csv"),
        os.path.join(os.path.expanduser("~"), "Downloads", "restaurants.csv")
    ]
    csv_file = None
    for path in csv_paths:
        if os.path.exists(path):
            csv_file = path
            break
    if csv_file is None:
        st.warning("⚠️ Không tìm thấy file restaurants.csv!")
        return []
    try:
        df = pd.read_csv(csv_file)
        df.columns = df.columns.str.strip()
        for idx, row in df.iterrows():
            toa_do = str(row.get('Toa_do', ''))
            lat, lng = None, None
            if ',' in toa_do:
                parts = toa_do.replace(' ', '').split(',')
                if len(parts) >= 2:
                    try:
                        lat = float(parts[0])
                        lng = float(parts[1])
                    except:
                        pass
            price = row.get('Price', 50000)
            if isinstance(price, str):
                price = float(price.replace(',', '').replace('đ', '').strip())

            if price < 50000:
                price_range = "cheap"
            elif price <= 200000:
                price_range = "moderate"
            else:
                price_range = "expensive"

                        

            co_so_raw = str(row.get('Co_so', '')).strip()
            if co_so_raw and co_so_raw != 'nan':
                if ',' in co_so_raw:

                    co_so_list = [c.strip().upper() for c in co_so_raw.split(',')]
                else:
                    co_so_list = [co_so_raw.strip().upper()]
            else:
                co_so_list = []
            
            restaurants.append({
                'id': idx,
                'Ten_quan': str(row.get('Ten_quan', f'Quán {idx+1}')),
                'Mon_an': str(row.get('Mon_an', 'Đặc sản')),
                'Cuisine': str(row.get('Cuisine', 'vietnamese')).lower(),
                'Meal_type': str(row.get('Meal_type', 'Món Việt')).lower(),
                'Dia_chi': str(row.get('Dia_chi', 'Đang cập nhật')),
                'Thoi_gian_mo_cua': str(row.get('Thoi_gian_mo_cua', '08:00 - 22:00')),
                'Price': price,
                'price_range': price_range,
                'lat': lat,
                'lng': lng,
                'rating': round(random.uniform(4.0, 4.9), 1),
                'co_so': co_so_list
            })
        
        all_campus_codes = set()
        for r in restaurants:
            for cs in r.get('co_so', []):
                all_campus_codes.add(cs)
        st.sidebar.success(f"📊 Dữ liệu có các cơ sở: {sorted(all_campus_codes)}")
        
        return [r for r in restaurants if r['lat'] is not None]
    except Exception as e:
        st.error(f"Lỗi đọc CSV: {e}")
        return []



def get_weather():
    try:
        resp = requests.get("https://wttr.in/10.7723,106.6682?format=j1", timeout=10)
        data = resp.json()
        temp = float(data['current_condition'][0]['temp_C'])
        if temp <= 20:
            weather_type = "cold"
            weather_desc = "❄️ Trời lạnh"
        elif temp <= 28:
            weather_type = "warm"
            weather_desc = "🌤️ Trời ấm"
        else:
            weather_type = "hot"
            weather_desc = "☀️ Trời nóng"
        return {
            'temp': temp,
            'weather_type': weather_type,
            'weather_desc': weather_desc,
            'icon': '🌤️' if temp > 30 else '☁️'
        }
    except:
        return {'temp': 28, 'weather_type': 'warm', 'weather_desc': '🌤️ Trời ấm', 'icon': '☀️'}

RULES = [
    
    # COLD weather
    {"antecedent": {"weather": "cold", "hungry_level": "light"},
     "consequent": {"meal_type": "snack", "cuisine": "vietnamese", "price_range": "cheap",
                    "explain": "Trời lạnh, hơi đói → Cháo lòng, bánh canh, súp nóng"}},
    
    {"antecedent": {"weather": "cold", "hungry_level": "hungry"},
     "consequent": {"meal_type": "full_meal", "cuisine": "vietnamese", "price_range": "moderate",
                    "explain": "Trời lạnh, đói vừa → Phở tái, bún bò Huế, hủ tiếu nước"}},
    
    {"antecedent": {"weather": "cold", "hungry_level": "very_hungry"},
     "consequent": {"meal_type": "full_meal", "cuisine": "korean", "price_range": "moderate",
                    "explain": "Trời lạnh, rất đói → Lẩu kim chi, canh jjigae, bulgogi"}},
    
    {"antecedent": {"weather": "cold", "hungry_level": "starving"},
     "consequent": {"meal_type": "full_meal", "cuisine": "korean", "price_range": "expensive",
                    "explain": "Trời lạnh, đói lả → Lẩu Hàn Quốc, samgyeopsal nướng"}},


    # WARM weather
    {"antecedent": {"weather": "warm", "hungry_level": "light"},
     "consequent": {"meal_type": "drinks", "cuisine": "vietnamese", "price_range": "cheap",
                    "explain": "Trời ấm, hơi đói → Trà sữa, sinh tố bơ, cà phê đen đá"}},
    
    {"antecedent": {"weather": "warm", "hungry_level": "hungry"},
     "consequent": {"meal_type": "fast_food", "cuisine": "vietnamese", "price_range": "cheap",
                    "explain": "Trời ấm, đói vừa → Bánh mì thịt, xôi gà, cơm tấm"}},
    
    {"antecedent": {"weather": "warm", "hungry_level": "very_hungry"},
     "consequent": {"meal_type": "full_meal", "cuisine": "vietnamese", "price_range": "moderate",
                    "explain": "Trời ấm, rất đói → Cơm tấm đặc biệt, bún thịt nướng"}},
    
    {"antecedent": {"weather": "warm", "hungry_level": "starving"},
     "consequent": {"meal_type": "full_meal", "cuisine": "western", "price_range": "moderate",
                    "explain": "Trời ấm, đói lả → Burger, pizza, pasta carbonara"}},


    # HOT weather
    {"antecedent": {"weather": "hot", "hungry_level": "light"},
     "consequent": {"meal_type": "dessert", "cuisine": "vietnamese", "price_range": "cheap",
                    "explain": "Trời nóng, hơi đói → Chè Thái, chè ba màu, kem chuối"}},
    
    {"antecedent": {"weather": "hot", "hungry_level": "hungry"},
     "consequent": {"meal_type": "healthy_meal", "cuisine": "vietnamese", "price_range": "cheap",
                    "explain": "Trời nóng, đói vừa → Gỏi cuốn tôm thịt, bún chả Hà Nội"}},
    
    {"antecedent": {"weather": "hot", "hungry_level": "very_hungry"},
     "consequent": {"meal_type": "full_meal", "cuisine": "japanese", "price_range": "moderate",
                    "explain": "Trời nóng, rất đói → Sushi cá hồi, sashimi, udon"}},
    
    {"antecedent": {"weather": "hot", "hungry_level": "starving"},
     "consequent": {"meal_type": "full_meal", "cuisine": "japanese", "price_range": "expensive",
                    "explain": "Trời nóng, đói lả → Donburi, sashimi bạch tuộc, lẩu Nhật"}},


    # ==================== BUDGET ====================
    {"antecedent": {"budget": "cheap", "hungry_level": "light"},
     "consequent": {"price_range": "cheap", "meal_type": "snack",
                    "explain": "Ít tiền, hơi đói → Bánh tráng trộn, bắp xào, ốc luộc"}},
    
    {"antecedent": {"budget": "cheap", "hungry_level": "hungry"},
     "consequent": {"price_range": "cheap", "meal_type": "fast_food",
                    "explain": "Ít tiền, đói vừa → Bánh mì, xôi mặn, cơm tấm 30k"}},
    
    {"antecedent": {"budget": "cheap", "hungry_level": "very_hungry"},
     "consequent": {"price_range": "cheap", "meal_type": "full_meal",
                    "explain": "Ít tiền, rất đói → Cơm phần bình dân, bún riêu, phở giá rẻ"}},
    
    {"antecedent": {"budget": "moderate", "hungry_level": "hungry"},
     "consequent": {"price_range": "moderate", "meal_type": "full_meal",
                    "explain": "Tiền vừa, đói vừa → Cơm cà ri Nhật, món Hàn tầm trung"}},
    
    {"antecedent": {"budget": "expensive", "hungry_level": "very_hungry"},
     "consequent": {"price_range": "expensive", "meal_type": "full_meal",
                    "explain": "Tiền nhiều, rất đói → Lẩu bò Mỹ, samgyeopsal, sườn nướng BBQ"}},


    # ==================== HEALTH GOAL ====================
    {"antecedent": {"health_goal": "diet", "hungry_level": "hungry"},
     "consequent": {"meal_type": "healthy_meal", "cuisine": "vietnamese", "price_range": "cheap",
                    "explain": "Ăn kiêng, đói vừa → Salad gà luộc, rau muống luộc, gỏi cuốn"}},
    
    {"antecedent": {"health_goal": "diet", "hungry_level": "very_hungry"},
     "consequent": {"meal_type": "healthy_meal", "cuisine": "japanese", "price_range": "moderate",
                    "explain": "Ăn kiêng, rất đói → Sushi gạo lứt, salad rong biển, miso soup"}},
    
    {"antecedent": {"health_goal": "balanced", "hungry_level": "hungry"},
     "consequent": {"meal_type": "full_meal", "cuisine": "vietnamese", "price_range": "moderate",
                    "explain": "Cân bằng → Cơm tấm đặc biệt, bún bò Huế đủ chất"}},
    
    {"antecedent": {"health_goal": "bulking", "hungry_level": "hungry"},
     "consequent": {"meal_type": "full_meal", "cuisine": "western", "price_range": "moderate",
                    "explain": "Tăng cơ → Steak bò, burger gà rán, cơm chiên Tây Ban Nha"}},
    
    {"antecedent": {"health_goal": "bulking", "hungry_level": "very_hungry"},
     "consequent": {"meal_type": "full_meal", "cuisine": "korean", "price_range": "moderate",
                    "explain": "Tăng cơ, rất đói → Bulgogi, galbi, cơm trộn thịt bò"}},


    # ==================== TIME AVAILABLE ====================
    {"antecedent": {"time_available": "very_short", "hungry_level": "hungry"},
     "consequent": {"time_estimate": "low", "meal_type": "fast_food",
                    "explain": "Rất ít thời gian (<15') → Bánh mì, xôi, burger"}},
    
    {"antecedent": {"time_available": "short", "hungry_level": "hungry"},
     "consequent": {"time_estimate": "low", "meal_type": "fast_food",
                    "explain": "Có 15-30' → Cơm tấm, phở, kimbap"}},
    
    {"antecedent": {"time_available": "medium", "hungry_level": "very_hungry"},
     "consequent": {"time_estimate": "medium", "meal_type": "full_meal",
                    "explain": "Có 30-60' → Cơm phần, ramen, donburi"}},


    # ==================== PLACE SUGGESTION===================
    {"antecedent": {"cuisine": "vietnamese", "meal_type": "full_meal", "price_range": "cheap"},
     "consequent": {"place_suggestion": "Cơm Bún, Phở House, Bún Quán, Cơm Corner",
                    "explain": "Quen thuộc, giá rẻ 30-50k"}},
    
    {"antecedent": {"cuisine": "vietnamese", "meal_type": "snack"},
     "consequent": {"place_suggestion": "Ốc Tiệm, Bánh Corner, Khoai Nhà hàng, Bắp Kitchen",
                    "explain": "Ốc, bánh tráng, bắp xào, bánh khọt"}},
    
    {"antecedent": {"cuisine": "vietnamese", "meal_type": "fast_food"},
     "consequent": {"place_suggestion": "Bánh Café, Xôi Express, Bánh Phở",
                    "explain": "Bánh mì, xôi, cơm nắm"}},
    
    {"antecedent": {"cuisine": "korean", "meal_type": "full_meal", "price_range": "moderate"},
     "consequent": {"place_suggestion": "Bulgogi House, Lẩu Tiệm, Gà House, Canh House",
                    "explain": "Lẩu kim chi, bulgogi, canh jjigae"}},
    
    {"antecedent": {"cuisine": "korean", "meal_type": "fast_food"},
     "consequent": {"place_suggestion": "Kimbap Tiệm, Tokbokki Nhà hàng",
                    "explain": "Kimbap, tokbokki, mì cay"}},
    
    {"antecedent": {"cuisine": "korean", "meal_type": "dessert"},
     "consequent": {"place_suggestion": "Hotteok Quán, Bingsu House",
                    "explain": "Hotteok, bingsu"}},
    
    {"antecedent": {"cuisine": "japanese", "meal_type": "full_meal", "price_range": "moderate"},
     "consequent": {"place_suggestion": "Sashimi House, Ramen Café, Udon House, Donburi Cơm",
                    "explain": "Sushi, sashimi, ramen, udon"}},
    
    {"antecedent": {"cuisine": "japanese", "meal_type": "healthy_meal"},
     "consequent": {"place_suggestion": "Sushi Tiệm, Miso Kitchen",
                    "explain": "Sushi gạo lứt, miso soup"}},
    
    {"antecedent": {"cuisine": "japanese", "meal_type": "dessert"},
     "consequent": {"place_suggestion": "Mochi Kitchen, Dorayaki Tiệm",
                    "explain": "Mochi, dorayaki, kem matcha"}},
    
    {"antecedent": {"cuisine": "western", "meal_type": "full_meal", "price_range": "moderate"},
     "consequent": {"place_suggestion": "Burger Corner, Pizza Quán, Salad Nhà hàng",
                    "explain": "Burger, pizza, pasta, salad"}},
    
    {"antecedent": {"cuisine": "western", "meal_type": "fast_food"},
     "consequent": {"place_suggestion": "Gà Corner, Wrap Bún, Hot Bún",
                    "explain": "Gà rán, wrap, hot dog"}},
    
    {"antecedent": {"cuisine": "western", "meal_type": "dessert"},
     "consequent": {"place_suggestion": "Cheesecake Kitchen, Kem Corner",
                    "explain": "Cheesecake, kem, cookie"}},
    
    {"antecedent": {"meal_type": "drinks"},
     "consequent": {"place_suggestion": "Trà House, Sinh Nhà hàng, Bạc Café",
                    "explain": "Trà sữa, sinh tố, cà phê"}},
    
    {"antecedent": {"meal_type": "dessert", "cuisine": "vietnamese"},
     "consequent": {"place_suggestion": "Chè Kitchen, Kem Nhà hàng, Bánh Corner",
                    "explain": "Chè, kem, bánh flan, pudding"}},
]



def infer_fuzzy(input_data):
    """
    Suy luận mờ với phương pháp CENTROID (trọng tâm)
    """
    

    meal_values = []      
    cuisine_values = []   
    price_values = []     
    time_values = []   
    place_values = []  
    explanation = ""
    max_explain_score = 0
    

    meal_map = {"snack": 1, "fast_food": 2, "drinks": 3, "healthy_meal": 4, "full_meal": 5, "dessert": 6}
    cuisine_map = {"vietnamese": 1, "korean": 2, "japanese": 3, "western": 4}
    price_map = {"cheap": 1, "moderate": 2, "expensive": 3}
    time_map = {"low": 1, "medium": 2, "high": 3}
    

    for rule in RULES:
        antecedent = rule.get("antecedent", {})
        consequent = rule.get("consequent", {})
        

        match_score = 1.0
        fuzzy_weights = {
            "weather": 1.5,
            "hungry_level": 1.5,
            "budget": 1.2,
            "time_available": 1.0,
            "health_goal": 1.0
        }
        
        for key, rule_value in antecedent.items():
            input_value = input_data.get(key)
            
            if input_value is None:
                match_score = 0
                break
                
            if input_value != rule_value:
                if key == "hungry_level":
                    levels = ["light", "hungry", "very_hungry", "starving"]
                    if input_value in levels and rule_value in levels:
                        distance = abs(levels.index(input_value) - levels.index(rule_value))
                        if distance == 1:
                            match_score *= 0.7
                        elif distance == 2:
                            match_score *= 0.3
                        else:
                            match_score = 0
                            break
                    else:
                        match_score = 0
                        break
                
                elif key == "time_available":
                    levels = ["very_short", "short", "medium", "long"]
                    if input_value in levels and rule_value in levels:
                        distance = abs(levels.index(input_value) - levels.index(rule_value))
                        if distance == 1:
                            match_score *= 0.7
                        elif distance == 2:
                            match_score *= 0.3
                        else:
                            match_score = 0
                            break
                    else:
                        match_score = 0
                        break
                
                elif key == "budget":
                    levels = ["cheap", "moderate", "expensive"]
                    if input_value in levels and rule_value in levels:
                        distance = abs(levels.index(input_value) - levels.index(rule_value))
                        if distance == 1:
                            match_score *= 0.6
                        else:
                            match_score = 0
                            break
                    else:
                        match_score = 0
                        break
                
                else:
                    match_score = 0
                    break
        
        if match_score <= 0:
            continue
        

        for key in antecedent.keys():
            match_score *= fuzzy_weights.get(key, 1.0)
        match_score = min(1.0, match_score)
        

        if "meal_type" in consequent:
            val = meal_map.get(consequent["meal_type"], 3)
            meal_values.append((val, match_score))
        
        if "cuisine" in consequent:
            val = cuisine_map.get(consequent["cuisine"], 1)
            cuisine_values.append((val, match_score))
        
        if "price_range" in consequent:
            val = price_map.get(consequent["price_range"], 2)
            price_values.append((val, match_score))
        
        if "time_estimate" in consequent:
            val = time_map.get(consequent["time_estimate"], 2)
            time_values.append((val, match_score))
        
        if "place_suggestion" in consequent:
            place_values.append((consequent["place_suggestion"], match_score))
        
        if "explain" in consequent and match_score > max_explain_score:
            max_explain_score = match_score
            explanation = consequent["explain"]
    
    
    if meal_values:
        total_weight = sum(w for _, w in meal_values)
        weighted_sum = sum(v * w for v, w in meal_values)
        centroid_meal = weighted_sum / total_weight

        best_meal = min(meal_map.items(), key=lambda x: abs(x[1] - centroid_meal))[0]
    else:
        best_meal = "full_meal"
    

    if cuisine_values:
        total_weight = sum(w for _, w in cuisine_values)
        weighted_sum = sum(v * w for v, w in cuisine_values)
        centroid_cuisine = weighted_sum / total_weight
        best_cuisine = min(cuisine_map.items(), key=lambda x: abs(x[1] - centroid_cuisine))[0]
    else:
        best_cuisine = "vietnamese"
    

    if price_values:
        total_weight = sum(w for _, w in price_values)
        weighted_sum = sum(v * w for v, w in price_values)
        centroid_price = weighted_sum / total_weight
        best_price = min(price_map.items(), key=lambda x: abs(x[1] - centroid_price))[0]
    else:
        budget_input = input_data.get("budget", "moderate")
        if budget_input == "cheap":
            best_price = "cheap"
        elif budget_input == "expensive":
            best_price = "expensive"
        else:
            best_price = "moderate"
    

    if time_values:
        total_weight = sum(w for _, w in time_values)
        weighted_sum = sum(v * w for v, w in time_values)
        centroid_time = weighted_sum / total_weight
        best_time = min(time_map.items(), key=lambda x: abs(x[1] - centroid_time))[0]
    else:
        time_input = input_data.get("time_available", "medium")
        time_map2 = {"very_short": "low", "short": "low", "medium": "medium", "long": "high"}
        best_time = time_map2.get(time_input, "medium")
    

    if place_values:
        place_counts = defaultdict(float)
        for place, weight in place_values:
            place_counts[place] += weight
        best_place = max(place_counts, key=place_counts.get)
    else:
        best_place = f"Quán {best_cuisine} gần UEH"
    

    calories_map = {
        "snack": "🔥 150-350 kcal - Ăn nhẹ, không lo tăng cân",
        "fast_food": "🔥 400-600 kcal - Nhanh gọn, đủ năng lượng",
        "full_meal": "🔥 600-900 kcal - No bụng, nhiều dinh dưỡng",
        "healthy_meal": "🔥 350-550 kcal - Cân bằng, tốt cho sức khỏe",
        "drinks": "🔥 100-250 kcal - Giải khát, thư giãn",
        "dessert": "🔥 200-400 kcal - Ngọt ngào, nạp đường"
    }
    calories_estimate = calories_map.get(best_meal, "🔥 400-700 kcal")
    

    if not explanation:
        explanation_templates = {
            "diet": f"Bạn đang ăn kiêng, hãy chọn {best_meal} {best_cuisine} ít calo.",
            "balanced": f"Để cân bằng dinh dưỡng, {best_meal} {best_cuisine} là lựa chọn phù hợp.",
            "bulking": f"Tăng cơ hiệu quả với {best_meal} {best_cuisine} giàu đạm."
        }
        health = input_data.get("health_goal", "balanced")
        explanation = explanation_templates.get(health, f"Dựa trên nhu cầu của bạn, chúng tôi gợi ý {best_meal} {best_cuisine}.")
    
    return {
        "meal_type": best_meal,
        "cuisine": best_cuisine,
        "price_range": best_price,
        "time_estimate": best_time,
        "place_suggestion": best_place,
        "calories_estimate": calories_estimate,
        "explain": explanation
    }


# ========== HÀM TIỆN ÍCH ==========
def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def predict_delivery_time(distance_km, weather_type):
    base_time = distance_km * 3
    if weather_type == 'cold':
        base_time *= 1.2
    elif weather_type == 'hot':
        base_time *= 1.1
    return int(base_time)

# ========== KHỞI TẠO SESSION STATE ==========
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'favorites' not in st.session_state:
    st.session_state.favorites = set()
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = defaultdict(int)
if 'recommendation' not in st.session_state:
    st.session_state.recommendation = None
if 'weather' not in st.session_state:
    st.session_state.weather = get_weather()
if 'campus_coords' not in st.session_state:
    st.session_state.campus_coords = UEH_CAMPUSES["A (59C Nguyễn Đình Chiểu, Q.3)"]["coords"]
if 'campus_name' not in st.session_state:
    st.session_state.campus_name = "A"
if 'campus_code' not in st.session_state:
    st.session_state.campus_code = "A"
if 'screen' not in st.session_state:
    st.session_state.screen = 'main'
if 'order_count' not in st.session_state:
    st.session_state.order_count = 0
if 'active_delivery' not in st.session_state:
    st.session_state.active_delivery = False
if 'current_restaurants' not in st.session_state:
    st.session_state.current_restaurants = []
if 'restaurants_data' not in st.session_state:
    st.session_state.restaurants_data = load_restaurants_from_csv()
if 'meal_plan' not in st.session_state:
    st.session_state.meal_plan = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False
if 'selected_campus' not in st.session_state:
    st.session_state.selected_campus = "A (59C Nguyễn Đình Chiểu, Q.3)"
if 'last_order_delivery_time' not in st.session_state:
    st.session_state.last_order_delivery_time = 30
if 'last_order_total' not in st.session_state:
    st.session_state.last_order_total = 0

# ========== HEADER ==========
if logo_base64:
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="margin-bottom: 15px;">
            <div style="background: #d4206e; display: inline-block; padding: 5px 25px; border-radius: 40px; border: 1px solid #ffd700;">
                <span style="color: #ffd700; font-weight: bold; font-size: 18px;">✨ Vừa vị - Thuận ví ✨</span>
            </div>
        </div>
        <img src="data:image/png;base64,{logo_base64}" style="width: 350px; max-width: 100%;">
    </div>
    """, unsafe_allow_html=True)
else:
    st.error("Không tìm thấy file snack-3.png trong thư mục!")

# ========== ẢNH TRANG TRÍ TRÊN ĐẦU (GIỐNG DƯỚI) ==========
st.markdown(f"""
<style>
    .header-decor {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: -400px;
        margin-bottom: -100px;
        pointer-events: none;
    }}
    .header-decor-left, .header-decor-right {{
        width: 250px;
        opacity: 0.9;
        animation: floatDecor 3s ease-in-out infinite;
    }}
    .header-decor-left {{
        transform: rotate(-5deg);
    }}
    .header-decor-right {{
        transform: rotate(5deg);
    }}
    @keyframes floatDecor {{
        0%, 100% {{ transform: translateY(0) rotate(0deg); }}
        50% {{ transform: translateY(-10px) rotate(5deg); }}
    }}
</style>
<div class="header-decor">
    <img src="data:image/png;base64,{decor_left}" class="header-decor-left">
    <img src="data:image/png;base64,{decor_right}" class="header-decor-right">
</div>
""", unsafe_allow_html=True)

# ========== TOP NAVIGATION ==========
st.markdown("---")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🏠 Trang chủ", use_container_width=True):
        st.session_state.screen = 'main'
        st.rerun()

with col2:
    if st.button("🔍 Tìm kiếm", use_container_width=True):
        st.session_state.screen = 'search'
        st.rerun()

with col3:
    cart_count = len(st.session_state.cart)
    btn_text = f"🛒 Giỏ hàng"
    if cart_count > 0:
        btn_text += f" ({cart_count})"
    if st.button(btn_text, use_container_width=True):
        if st.session_state.cart:
            st.session_state.screen = 'result'
            st.rerun()
        else:
            st.toast("🛍️ Giỏ hàng trống! Hãy thêm món từ danh sách nhà hàng.")

with col4:
    if st.button("🎯 Sở thích", use_container_width=True):
        st.session_state.screen = 'preferences'
        st.rerun()

with col5:
    if st.button("👤 Cá nhân", use_container_width=True):
        st.session_state.screen = 'profile'
        st.rerun()
# ========== MÀN HÌNH ĐANG GIAO HÀNG ==========
if st.session_state.active_delivery:
    st.markdown(f"""
    <div class="result-card">
        <div style="font-size: 3rem;">🚚</div>
        <h2>ĐANG GIAO HÀNG</h2>
        <div class="order-status">
            <p>Đơn hàng #{st.session_state.order_count}</p>
            <p>Shipper đang trên đường giao!</p>
            <p>Dự kiến giao trong {st.session_state.last_order_delivery_time} phút</p>
            <p>Tổng tiền: <strong>{st.session_state.last_order_total:,}đ</strong></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🏠 VỀ TRANG CHỦ", use_container_width=True):
        st.session_state.active_delivery = False
        st.session_state.screen = 'main'
        st.rerun()

# ========== MÀN HÌNH TÌM KIẾM ==========
elif st.session_state.screen == 'search':
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>🔍 TÌM KIẾM MÓN ĂN</h2>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    campus_search = st.selectbox(
        "🏫 Chọn cơ sở UEH", 
        list(UEH_CAMPUSES.keys()),
        index=list(UEH_CAMPUSES.keys()).index(st.session_state.selected_campus) if st.session_state.selected_campus in UEH_CAMPUSES else 0
    )
    st.session_state.selected_campus = campus_search
    
    search_keyword = st.text_input("🔎 Nhập tên món ăn hoặc tên quán", placeholder="Ví dụ: Phở, Cơm tấm, Bún bò...")
    
    col_search_btn, col_back_btn = st.columns(2)
    with col_search_btn:
        if st.button("🔍 TÌM KIẾM", use_container_width=True):
            if search_keyword.strip():
                keyword = search_keyword.strip().lower()
                campus_code = UEH_CAMPUSES[campus_search]["code"]
                campus_code_upper = campus_code.upper()

                restaurants_at_campus = [
                    r for r in st.session_state.restaurants_data
                    if campus_code_upper in [cs.upper() for cs in r.get('co_so', [])]
                ]

                # Thêm debug
                st.write(f"🔍 Tìm nhà hàng với mã: {campus_code_upper}")
                st.write(f"🔍 Số nhà hàng tìm được: {len(restaurants_at_campus)}")
                results = []
                for r in restaurants_at_campus:
                    if keyword in r['Mon_an'].lower() or keyword in r['Ten_quan'].lower():
                        campus_coords = UEH_CAMPUSES[campus_search]["coords"]
                        r['distance_km'] = haversine(campus_coords, (r['lat'], r['lng']))
                        r['delivery_time'] = predict_delivery_time(r['distance_km'], st.session_state.weather['weather_type'])
                        results.append(r)
                st.session_state.search_results = results
                st.session_state.search_performed = True
                st.rerun()
            else:
                st.warning("⚠️ Vui lòng nhập từ khóa tìm kiếm!")
    
    with col_back_btn:
        if st.button("🔙 QUAY LẠI", use_container_width=True):
            st.session_state.screen = 'main'
            st.session_state.search_performed = False
            st.rerun()
    
    if st.session_state.search_performed:
        if st.session_state.search_results:
            st.markdown(f"### 📍 Tìm thấy {len(st.session_state.search_results)} kết quả")
            for idx, rest in enumerate(st.session_state.search_results[:10]):
                with st.container():
                    # Map icons
                    meal_icon = {
                        "snack": "🍿",
                        "fast_food": "🍔",
                        "full_meal": "🍽️",
                        "healthy_meal": "🥗",
                        "drinks": "🥤",
                        "dessert": "🍰"
                    }.get(rest['Meal_type'], "🍜")
                    
                    cuisine_icon = {
                        "vietnamese": "🇻🇳",
                        "korean": "🇰🇷",
                        "japanese": "🇯🇵",
                        "western": "🇺🇸"
                    }.get(rest['Cuisine'], "🍽️")
                    
                    st.markdown(f"""
                    <div class="restaurant-card">
                        <strong>{idx+1}. {rest['Ten_quan']}</strong>
                        <span style="float: right;">{cuisine_icon} {rest['Cuisine'].upper()}</span><br>
                        🍜 {rest['Mon_an']} | ⭐ {rest['rating']}/5<br>
                        📍 {rest['Dia_chi']}<br>
                        ⏰ {rest['Thoi_gian_mo_cua']}<br>
                        <span class="info-label">{meal_icon} {rest['Meal_type'].replace('_', ' ').upper()}</span>
                        <span class="info-label">📏 {rest['distance_km']:.1f}km</span>
                        <span class="info-label">💰 {rest['Price']:,.0f}đ</span>
                        <span class="info-label">🚚 {rest['delivery_time']} phút</span>
                    </div>
                    """, unsafe_allow_html=True)
                    col_like, col_cart_search = st.columns(2)
                    with col_like:
                        if st.button(f"❤️ Thích", key=f"like_search_{rest['id']}"):
                            st.session_state.favorites.add(rest['Ten_quan'])
                            st.session_state.user_preferences[rest['Meal_type']] += 1
                            st.toast(f"✅ Đã thích {rest['Ten_quan']}!")
                    with col_cart_search:
                        if st.button(f"🛒 Thêm vào giỏ", key=f"cart_search_{rest['id']}"):
                            shipping = int(rest['distance_km'] * 5000 + 10000)
                            cart_item = {
                                'id': rest['id'],
                                'name': rest['Ten_quan'],
                                'mon_an': rest['Mon_an'],
                                'dia_chi': rest['Dia_chi'],
                                'price': rest['Price'],
                                'shipping_fee': shipping,
                                'qty': 1,
                                'restaurant': rest,
                                'total': rest['Price'] + shipping,
                                'delivery_time': rest['delivery_time']
                            }
                            st.session_state.cart.append(cart_item)
                            st.toast(f"✅ Đã thêm {rest['Ten_quan']} vào giỏ hàng!")
                    st.markdown("---")
        else:
            st.info("😢 Không tìm thấy món ăn hoặc quán nào phù hợp. Hãy thử từ khóa khác nhé!")

# ========== MÀN HÌNH SỞ THÍCH ==========
elif st.session_state.screen == 'preferences':
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>🎯 SỞ THÍCH CỦA BẠN</h2>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.user_preferences:
        st.markdown("### 📊 Thống kê món ăn đã thích:")
        for meal_type, count in sorted(st.session_state.user_preferences.items(), key=lambda x: -x[1]):
            st.markdown(f"- {meal_type}: đã thích {count} lần")
    else:
        st.info("💡 Chưa có dữ liệu. Hãy thích món ăn để tôi học sở thích của bạn!")
    
    if st.session_state.favorites:
        st.markdown("### ❤️ Món ăn đã thích:")
        for fav in list(st.session_state.favorites)[:10]:
            st.markdown(f"- {fav}")
    else:
        st.info("💡 Chưa có món nào được thích. Hãy nhấn nút ❤️ bên cạnh món ăn bạn ưa thích!")
    
    if st.button("🔙 QUAY LẠI TRANG CHỦ", use_container_width=True):
        st.session_state.screen = 'main'
        st.rerun()

# ========== MÀN HÌNH CÁ NHÂN ==========
elif st.session_state.screen == 'profile':
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>👤 CÁ NHÂN</h2>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #d4206e, #b81a5c); border-radius: 20px; padding: 1rem;">
        <p><strong>👤 Tên:</strong> Nguyễn Thị Thảo</p>
        <p><strong>📧 Email:</strong> thao.nguyen@ueh.edu.vn</p>
        <p><strong>📱 SĐT:</strong> 0909 123 456</p>
        <p><strong>📦 Số đơn đã đặt:</strong> {st.session_state.order_count}</p>
        <p><strong>❤️ Món yêu thích:</strong> {len(st.session_state.favorites)}</p>
        <p><strong>🧠 Loại món đã học:</strong> {len(st.session_state.user_preferences)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_clear, col_back_profile = st.columns(2)
    with col_clear:
        if st.button("🗑️ XÓA DỮ LIỆU", use_container_width=True):
            st.session_state.favorites.clear()
            st.session_state.user_preferences.clear()
            st.session_state.cart.clear()
            st.toast("✅ Đã xóa toàn bộ dữ liệu!")
            time.sleep(0.5)
            st.rerun()
    with col_back_profile:
        if st.button("🔙 QUAY LẠI", use_container_width=True):
            st.session_state.screen = 'main'
            st.rerun()

# ========== MÀN HÌNH CHÍNH ==========
elif st.session_state.screen == 'main':
    with st.container():
        st.markdown('<div class="fortune-card">', unsafe_allow_html=True)

        w = st.session_state.weather
        col_w1, col_w2 = st.columns([3, 1])
        with col_w1:
            st.markdown(f"**🌡️ THỜI TIẾT HÔM NAY:** {w['weather_desc']} - {w['temp']}°C")
        with col_w2:
            if st.button("🔄", key="refresh_weather"):
                st.session_state.weather = get_weather()
                st.rerun()

        st.markdown("**🏫 CƠ SỞ UEH**")
        campus = st.selectbox("Chọn cơ sở", list(UEH_CAMPUSES.keys()), label_visibility="collapsed")
        # Cập nhật ngay lập tức khi chọn cơ sở
        st.session_state.selected_campus = campus
        st.session_state.campus_coords = UEH_CAMPUSES[campus]["coords"]
        st.session_state.campus_code = UEH_CAMPUSES[campus]["code"]
        st.session_state.campus_name = campus.split(' ')[0]

        st.markdown("**🍚 MỨC ĐỘ ĐÓI**")
        hunger_val = st.slider("Độ đói", 0, 10, 5, label_visibility="collapsed")
        if hunger_val <= 3:
            hungry_level = "light"
            hunger_text = "😌 Hơi đói nhẹ"
        elif hunger_val <= 6:
            hungry_level = "hungry"
            hunger_text = "😋 Đói vừa"
        elif hunger_val <= 8:
            hungry_level = "very_hungry"
            hunger_text = "😫 Rất đói"
        else:
            hungry_level = "starving"
            hunger_text = "🤯 Đói cồn cào!"
        st.progress(hunger_val/10, text=hunger_text)

        st.markdown("**💰 NGÂN SÁCH (VNĐ)**")
        budget_val = st.number_input("Ngân sách", min_value=0, max_value=10000000, value=200000, step=50000, label_visibility="collapsed")
        if budget_val < 50000:
            budget_type = "cheap"
            budget_text = "🟢 Rẻ (<50k)"
        elif budget_val < 200000:
            budget_type = "moderate"
            budget_text = "🟡 Trung bình (50-200k)"
        else:
            budget_type = "expensive"
            budget_text = "🔴 Đắt (>200k)"
        st.caption(budget_text)

        st.markdown("**⏳ THỜI GIAN RẢNH (phút)**")
        time_minutes = st.slider("Thời gian", 5, 120, 30, 5, label_visibility="collapsed")
        if time_minutes <= 15:
            time_available = "very_short"
        elif time_minutes <= 30:
            time_available = "short"
        elif time_minutes <= 60:
            time_available = "medium"
        else:
            time_available = "long"

        st.markdown("**🎯 MỤC TIÊU SỨC KHỎE**")
        health_map = {"diet": "🥗 Giảm cân", "balanced": "⚖️ Cân bằng", "bulking": "💪 Tăng cơ"}
        health_goal = st.radio("Mục tiêu", list(health_map.keys()), format_func=lambda x: health_map[x], horizontal=True, label_visibility="collapsed")

        st.markdown('</div>', unsafe_allow_html=True)

        # Button gieo quẻ - DÙNG BUTTON BÌNH THƯỜNG
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🥢 LẮC QUẺ 🥢", use_container_width=True):
                # Lắc que
                shake_html = f"""
                <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; backdrop-filter: blur(10px); background: rgba(0,0,0,0.6); z-index: 9999; display: flex; justify-content: center; align-items: center; flex-direction: column;" id="shakeDiv">
                    <img src="data:image/png;base64,{shake_img_base64}" style="width: 350px; animation: shakeAnim 0.3s ease-in-out infinite;">
                    <div style="margin-top: 30px; color: #ffd700; font-size: 1.2rem; font-weight: bold; text-align: center;">
                        🥢 ĐANG LẮC QUẺ... 🥢<br>
                        ✨ Lộc đến nhà, cơm thêm bát ✨
                    </div>
                </div>
                <style>
                    @keyframes shakeAnim {{
                        0% {{ transform: translate(0,0) rotate(0deg); }}
                        25% {{ transform: translate(-12px,-8px) rotate(-8deg); }}
                        50% {{ transform: translate(12px,8px) rotate(8deg); }}
                        75% {{ transform: translate(-6px,6px) rotate(-5deg); }}
                        100% {{ transform: translate(0,0) rotate(0deg); }}
                    }}
                </style>
                <script>
                    setTimeout(function() {{
                        var div = document.getElementById('shakeDiv');
                        if(div) div.remove();
                    }}, 4500);
                </script>
                """
                st.markdown(shake_html, unsafe_allow_html=True)
                time.sleep(1.2)


                # Que bay lên
                que_html = f"""
                <div id="queDiv" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; backdrop-filter: blur(5px); background: rgba(0,0,0,0.5); z-index: 10000; display: flex; justify-content: center; align-items: center; flex-direction: column;">
                    <div style="text-align: center;">
                        <img src="data:image/png;base64,{que_img_base64}" style="width: 350px; animation: flyQue 0.6s ease-out forwards, gentleShake 0.5s ease-in-out 0.6s infinite;">
                </div>
                <style>
                    @keyframes flyQue {{
                        0% {{ transform: translateY(150px) scale(0.3); opacity: 0; }}
                        50% {{ transform: translateY(-30px) scale(1.5); opacity: 1; }}
                        100% {{ transform: translateY(0) scale(1); opacity: 1; }}
                    }}
                    @keyframes gentleShake {{
                        0% {{ transform: translate(0,0) rotate(0deg); }}
                        25% {{ transform: translate(-3px,-2px) rotate(-2deg); }}
                        50% {{ transform: translate(3px,2px) rotate(2deg); }}
                        75% {{ transform: translate(-2px,1px) rotate(-1deg); }}
                        100% {{ transform: translate(0,0) rotate(0deg); }}
                    }}
                    @keyframes textFade {{
                        0% {{ opacity: 0; transform: scale(0.8); }}
                        100% {{ opacity: 1; transform: scale(1); }}
                    }}
                </style>
                <script>
                    setTimeout(function() {{
                        var div = document.getElementById('queDiv');
                        if(div) div.remove();
                    }}, 3000);
                </script>
                """
                st.markdown(que_html, unsafe_allow_html=True)
                time.sleep(1.5)


                # Loading overlay
                loading_html = """
                <div id="finalOverlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, #d4206e, #b81a5c); z-index: 999999999; display: flex; justify-content: center; align-items: center; flex-direction: column;">
                    <div style="text-align: center; color: #ffd700;">
                        <div style="font-size: 5rem;">🥢</div>
                        <div style="margin-top: 20px; font-size: 1.8rem; font-weight: bold;">
                            ĐANG TÌM QUÁN NGON...
                        </div>
                        <div style="margin-top: 15px; font-size: 1.2rem;">
                            Lộc đến nhà, cơm thêm bát
                        </div>
                        <div style="margin-top: 10px; font-size: 1rem;">
                            ✨ Một chút xíu nữa thôi ✨
                        </div>
                    </div>
                </div>
                """
                st.markdown(loading_html, unsafe_allow_html=True)
                time.sleep(0.5)


                # Xử lý gợi ý
                input_data = {
                    "weather": st.session_state.weather['weather_type'],
                    "hungry_level": hungry_level,
                    "budget": budget_type,
                    "time_available": time_available,
                    "health_goal": health_goal
                }
                rec = infer_fuzzy(input_data)
                current_campus_key = st.session_state.selected_campus  # Lấy từ session_state
                campus_coords = UEH_CAMPUSES[current_campus_key]["coords"]
                campus_code = UEH_CAMPUSES[current_campus_key]["code"]
                campus_short = current_campus_key.split(' ')[0]
                st.write(f"🔍 DEBUG: Cơ sở bạn chọn = {current_campus_key}, Mã = {campus_code}")
                st.write(f"🔍 DEBUG: Số nhà hàng tại cơ sở {campus_code} = {len([r for r in st.session_state.restaurants_data if campus_code in r.get('co_so', [])])}")


                restaurants_at_campus = [
                    r for r in st.session_state.restaurants_data
                    if campus_code in r.get('co_so', [])
                ]


                if not restaurants_at_campus:
                    st.warning(f"⚠️ Không có nhà hàng nào tại cơ sở {campus_code}. Vui lòng chọn cơ sở khác!")
                    st.rerun()


                # Lọc theo tất cả: cuisine + meal_type + price_range
                suitable = [r for r in restaurants_at_campus 
                            if rec['cuisine'] == r.get('Cuisine', '') 
                            and rec['meal_type'] == r.get('Meal_type', '')
                            and rec['price_range'] == r.get('price_range', '')]

                # Nếu không có, bỏ price_range
                if not suitable:
                    suitable = [r for r in restaurants_at_campus 
                                if rec['cuisine'] == r.get('Cuisine', '') 
                                and rec['meal_type'] == r.get('Meal_type', '')]

                # Nếu vẫn không, bỏ meal_type
                if not suitable:
                    suitable = [r for r in restaurants_at_campus if rec['cuisine'] == r.get('Cuisine', '')]

                # Cuối cùng lấy 6 quán bất kỳ
                if not suitable:
                    suitable = restaurants_at_campus[:6]


                for r in suitable:
                    r['distance_km'] = haversine(campus_coords, (r['lat'], r['lng']))
                    r['delivery_time'] = predict_delivery_time(r['distance_km'], st.session_state.weather['weather_type'])


                suitable.sort(key=lambda x: x['distance_km'])


                st.session_state.recommendation = rec
                st.session_state.campus_coords = campus_coords
                st.session_state.campus_name = campus_short
                st.session_state.campus_code = campus_code
                st.session_state.current_restaurants = suitable[:6]
                st.session_state.screen = 'result'
                st.rerun()


# ========== MÀN HÌNH KẾT QUẢ ==========
elif st.session_state.screen == 'result':
    rec = st.session_state.recommendation
    
    st.markdown(f"""
    <div class="result-box-container">
        <div style="text-align: center;">
            <p style="color: #d4206e; font-weight: bold; letter-spacing: 2px;">🎋 QUẺ CỦA BẠN 🎋</p>
            <h1 class="mon-an-title">{rec['meal_type'].upper()}</h1>
            <div class="explain-text">
                <p>✨ {rec['explain']} ✨</p>
                <p style="font-size: 14px; color: #666;">Dựa trên thời tiết {st.session_state.weather['temp']}°C và mức độ đói của bạn.</p>
                <p style="font-size: 16px; color: #ffd700; margin-top: 10px;">{rec['calories_estimate']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔙 VỀ TRANG CHỦ"):
        st.session_state.screen = 'main'
        st.rerun()

    st.markdown("### 🗺️ BẢN ĐỒ & DANH SÁCH NHÀ HÀNG")
    
    col_map, col_list = st.columns(2, gap="medium")

    with col_map:
        st.markdown("#### 📍 BẢN ĐỒ VỊ TRÍ")
        if st.session_state.current_restaurants and st.session_state.campus_coords:
            center_lat = st.session_state.campus_coords[0]
            center_lng = st.session_state.campus_coords[1]
            m = folium.Map(location=[center_lat, center_lng], zoom_start=14, height=450)

            folium.Marker(
                [center_lat, center_lng],
                popup=f"<b>📍 Điểm đến: UEH {st.session_state.campus_name}</b>",
                icon=folium.Icon(color='green', icon='graduation-cap', prefix='fa')
            ).add_to(m)

            for rest in st.session_state.current_restaurants[:5]:
                popup_html = f"""
                <div style="min-width: 200px;">
                    <b>🏪 {rest['Ten_quan']}</b><br>
                    🍜 {rest['Mon_an']}<br>
                    📍 {rest['Dia_chi']}<br>
                    ⭐ {rest['rating']}/5<br>
                    💰 {rest['Price']:,.0f}đ<br>
                    📏 {rest['distance_km']:.1f}km<br>
                    🚚 Giao {rest['delivery_time']} phút
                </div>
                """
                folium.Marker(
                    [rest['lat'], rest['lng']],
                    popup=popup_html,
                    icon=folium.Icon(color='red', icon='cutlery', prefix='fa')
                ).add_to(m)

                route = get_route(rest['lat'], rest['lng'], center_lat, center_lng)
                if route:
                    folium.PolyLine(
                        route,
                        color='blue', weight=3, opacity=0.7,
                        popup=f"📏 {rest['distance_km']:.1f}km - 🚚 {rest['delivery_time']} phút (đường thực tế)"
                    ).add_to(m)
                else:
                    folium.PolyLine(
                        [[rest['lat'], rest['lng']], [center_lat, center_lng]],
                        color='blue', weight=2, opacity=0.6,
                        popup=f"📏 {rest['distance_km']:.1f}km - 🚚 {rest['delivery_time']} phút (ước lượng)"
                    ).add_to(m)

            st_folium(m, width="100%", height=450)

    with col_list:
        st.markdown("#### 🏪 DANH SÁCH NHÀ HÀNG")
        
        for idx, rest in enumerate(st.session_state.current_restaurants[:5]):
            with st.container():

                meal_icon = {
                    "snack": "🍿",
                    "fast_food": "🍔",
                    "full_meal": "🍽️",
                    "healthy_meal": "🥗",
                    "drinks": "🥤",
                    "dessert": "🍰"
                }.get(rest['Meal_type'], "🍜")
                
                cuisine_icon = {
                    "vietnamese": "🇻🇳",
                    "korean": "🇰🇷",
                    "japanese": "🇯🇵",
                    "western": "🇺🇸"
                }.get(rest['Cuisine'], "🍽️")
                
                st.markdown(f"""
                <div style="background: rgba(0,0,0,0.35); border-radius: 15px; padding: 12px; margin-bottom: 10px; border-left: 4px solid #ffd700;">
                    <strong style="color: #ffd700; font-size: 1rem;">{idx+1}. {rest['Ten_quan']}</strong>
                    <span style="float: right; font-size: 0.8rem;">{cuisine_icon} {rest['Cuisine'].upper()}</span><br>
                    <span style="font-size: 0.85rem;">🍜 {rest['Mon_an']} | ⭐ {rest['rating']}/5</span><br>
                    <span style="font-size: 0.75rem;">📍 {rest['Dia_chi'][:35]}...</span><br>
                    <span style="font-size: 0.75rem;">⏰ {rest['Thoi_gian_mo_cua']}</span><br>
                    <div style="margin-top: 8px;">
                        <span class="info-label">{meal_icon} {rest['Meal_type'].replace('_', ' ').upper()}</span>
                        <span class="info-label">📏 {rest['distance_km']:.1f}km</span>
                        <span class="info-label">💰 {rest['Price']:,.0f}đ</span>
                        <span class="info-label">🚚 {rest['delivery_time']} phút</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col_like, col_cart_list = st.columns(2)
                with col_like:
                    if st.button(f"❤️ Thích", key=f"like_result_{rest['id']}"):
                        st.session_state.favorites.add(rest['Ten_quan'])
                        st.session_state.user_preferences[rest['Meal_type']] += 1
                        st.toast(f"✅ Đã thích {rest['Ten_quan']}!")
                with col_cart_list:
                    if st.button(f"🛒 Thêm", key=f"cart_result_{rest['id']}"):
                        shipping = int(rest['distance_km'] * 5000 + 10000)
                        cart_item = {
                            'id': rest['id'],
                            'name': rest['Ten_quan'],
                            'mon_an': rest['Mon_an'],
                            'dia_chi': rest['Dia_chi'],
                            'price': rest['Price'],
                            'shipping_fee': shipping,
                            'qty': 1,
                            'restaurant': rest,
                            'total': rest['Price'] + shipping,
                            'delivery_time': rest['delivery_time']
                        }
                        st.session_state.cart.append(cart_item)
                        st.toast(f"✅ Đã thêm {rest['Ten_quan']} vào giỏ hàng!")

    st.divider()

    st.markdown("### 📅 DAILY MEAL PLANNER")
    if st.button("🍱 TẠO KẾ HOẠCH BỮA ĂN TRONG NGÀY", use_container_width=True):
        meals = ['Sáng', 'Trưa', 'Xế', 'Tối']
        plan = {}
        
        source_list = st.session_state.current_restaurants if st.session_state.current_restaurants else st.session_state.restaurants_data
        
        if source_list:
            if len(source_list) >= 4:
                selected_restaurants = random.sample(source_list, 4)
            else:
                selected_restaurants = source_list
            
            for i, meal in enumerate(meals):
                if i < len(selected_restaurants):
                    rest = selected_restaurants[i]
                else:
                    rest = random.choice(source_list)
                plan[meal] = {
                    'restaurant': rest['Ten_quan'],
                    'dish': rest['Mon_an'],
                    'price': rest['Price']
                }
        else:
            st.warning("Không có nhà hàng nào để lập kế hoạch!")
            plan = None
        
        st.session_state.meal_plan = plan

    if st.session_state.meal_plan:
        st.markdown('<div class="meal-planner-card">', unsafe_allow_html=True)
        for meal, info in st.session_state.meal_plan.items():
            st.markdown(f"**{meal}:** {info['restaurant']} - {info['dish']} (💰{info['price']:,.0f}đ)")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    if st.session_state.cart:
        st.markdown("### 🛒 GIỎ HÀNG CỦA BẠN")
        total_temp = 0

        for idx, item in enumerate(st.session_state.cart):
            with st.expander(f"📦 {item['name']} - {item['mon_an']} (x{item['qty']})", expanded=idx == 0):
                col_detail, col_map_cart = st.columns([1, 1])

                with col_detail:
                    st.markdown(f"""
                    <div style="background: rgba(0,0,0,0.3); border-radius: 20px; padding: 12px;">
                        <p><span class="info-label">🏪 QUÁN</span> {item['name']}</p>
                        <p><span class="info-label">🍜 MÓN</span> {item['mon_an']}</p>
                        <p><span class="info-label">📍 ĐỊA CHỈ</span> {item['dia_chi']}</p>
                        <p><span class="info-label">💰 GIÁ</span> {item['price']:,.0f}đ</p>
                        <p><span class="info-label">🚚 PHÍ SHIP</span> {item['shipping_fee']:,.0f}đ</p>
                        <p><span class="info-label">⭐ ĐÁNH GIÁ</span> {item['restaurant']['rating']}/5</p>
                        <p><span class="info-label">⏱️ GIAO HÀNG</span> {item['delivery_time']} phút</p>
                        <p><span class="info-label">📏 KHOẢNG CÁCH</span> {item['restaurant']['distance_km']:.1f}km</p>
                        <p><span class="info-label">🕐 GIỜ MỞ</span> {item['restaurant']['Thoi_gian_mo_cua']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    col_qty, col_update, col_remove = st.columns([2, 1, 1])
                    with col_qty:
                        new_qty = st.number_input(f"Số lượng", min_value=1, max_value=10, value=item['qty'], key=f"qty_{idx}")
                    with col_update:
                        if st.button(f"🔄 Cập nhật", key=f"update_{idx}"):
                            if new_qty != item['qty']:
                                item['qty'] = new_qty
                                item['total'] = item['price'] * new_qty + item['shipping_fee']
                                st.rerun()
                    with col_remove:
                        if st.button(f"❌ Xóa", key=f"remove_{idx}"):
                            st.session_state.cart.pop(idx)
                            st.rerun()

                with col_map_cart:
                    rest = item['restaurant']
                    start = (rest['lat'], rest['lng'])
                    end = st.session_state.campus_coords

                    m_cart = folium.Map(location=[(start[0] + end[0])/2, (start[1] + end[1])/2], zoom_start=14, height=250)

                    folium.Marker(
                        [start[0], start[1]],
                        popup=f"<b>🏪 {rest['Ten_quan']}</b><br>{rest['Dia_chi']}",
                        icon=folium.Icon(color='red', icon='cutlery', prefix='fa')
                    ).add_to(m_cart)

                    folium.Marker(
                        [end[0], end[1]],
                        popup=f"<b>🏫 Điểm đến: UEH {st.session_state.campus_name}</b>",
                        icon=folium.Icon(color='green', icon='graduation-cap', prefix='fa')
                    ).add_to(m_cart)

                    route = get_route(rest['lat'], rest['lng'], end[0], end[1])
                    if route:
                        folium.PolyLine(
                            route,
                            color='#d4206e', weight=3, opacity=0.7,
                            popup=f"🚚 {rest['distance_km']:.1f}km - {item['delivery_time']} phút"
                        ).add_to(m_cart)
                    else:
                        folium.PolyLine(
                            [start, end],
                            color='#d4206e', weight=2, opacity=0.6,
                            popup=f"🚚 {rest['distance_km']:.1f}km - {item['delivery_time']} phút"
                        ).add_to(m_cart)

                    st_folium(m_cart, width="100%", height=250)

                    st.markdown(f"""
                    <div style="background: rgba(0,0,0,0.3); border-radius: 15px; padding: 10px; margin-top: 10px;">
                        <p><span class="info-label">🗺️ CHỈ ĐƯỜNG</span></p>
                        <p style="font-size: 0.75rem;">📍 {rest['Ten_quan']} → UEH {st.session_state.campus_name}</p>
                        <p style="font-size: 0.75rem;">📏 {rest['distance_km']:.1f}km - ⏱️ {item['delivery_time']} phút</p>
                    </div>
                    """, unsafe_allow_html=True)

            total_temp += item['total']

        st.divider()
        st.markdown(f"<h3 style='text-align: right;'>TỔNG CỘNG: {total_temp:,.0f}đ</h3>", unsafe_allow_html=True)

        col_back, col_checkout = st.columns(2)
        with col_back:
            if st.button("🔙 QUAY LẠI", use_container_width=True):
                st.session_state.screen = 'main'
                st.rerun()
        with col_checkout:
            if st.button("✅ TIẾN HÀNH THANH TOÁN", use_container_width=True):
                st.session_state.screen = 'checkout'
                st.rerun()
    else:
        st.info("🛍️ Giỏ hàng trống. Hãy thêm món từ danh sách nhà hàng!")
        if st.button("🔙 QUAY LẠI", use_container_width=True):
            st.session_state.screen = 'main'
            st.rerun()

elif st.session_state.screen == 'checkout':
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>📋 XÁC NHẬN ĐƠN HÀNG</h2>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    total_all = 0

    st.markdown("### 🚚 CHI TIẾT ĐƠN HÀNG VÀ LỘ TRÌNH")

    for idx, item in enumerate(st.session_state.cart):
        with st.expander(f"{idx+1}. {item['name']} - {item['mon_an']} (x{item['qty']})", expanded=True):
            col_info, col_route = st.columns([1, 1])

            with col_info:
                st.markdown(f"""
                <div style="background: rgba(0,0,0,0.3); border-radius: 20px; padding: 12px;">
                    <h4 style="color: #ffd700;">🏪 THÔNG TIN QUÁN</h4>
                    <p><strong>📛 Tên quán:</strong> {item['name']}</p>
                    <p><strong>🍜 Món ăn:</strong> {item['mon_an']}</p>
                    <p><strong>📍 Địa chỉ:</strong> {item['dia_chi']}</p>
                    <p><strong>⭐ Đánh giá:</strong> {item['restaurant']['rating']}/5</p>
                    <p><strong>🕐 Giờ mở cửa:</strong> {item['restaurant']['Thoi_gian_mo_cua']}</p>
                    <hr style="border-color: #ffd700;">
                    <h4 style="color: #ffd700;">💰 CHI TIẾT GIÁ</h4>
                    <p><strong>Giá món:</strong> {item['price']:,.0f}đ</p>
                    <p><strong>Số lượng:</strong> x{item['qty']}</p>
                    <p><strong>Phí vận chuyển:</strong> {item['shipping_fee']:,.0f}đ</p>
                    <p><strong>⏱️ Thời gian giao:</strong> {item['delivery_time']} phút</p>
                    <p><strong>📏 Khoảng cách:</strong> {item['restaurant']['distance_km']:.1f}km</p>
                    <h3 style="color: #ffd700; text-align: right;">Thành tiền: {item['total']:,.0f}đ</h3>
                </div>
                """, unsafe_allow_html=True)

            with col_route:
                rest = item['restaurant']
                start = (rest['lat'], rest['lng'])
                end = st.session_state.campus_coords
                distance = rest['distance_km']
                delivery_time = item['delivery_time']

                m_route = folium.Map(location=[(start[0] + end[0])/2, (start[1] + end[1])/2], zoom_start=14)

                folium.Marker(
                    [start[0], start[1]],
                    popup=f"<b>🏪 ĐIỂM ĐI</b><br>{rest['Ten_quan']}<br>{rest['Dia_chi']}",
                    icon=folium.Icon(color='red', icon='play', prefix='fa')
                ).add_to(m_route)

                folium.Marker(
                    [end[0], end[1]],
                    popup=f"<b>🏫 ĐIỂM ĐẾN</b><br>UEH {st.session_state.campus_name}",
                    icon=folium.Icon(color='green', icon='flag-checkered', prefix='fa')
                ).add_to(m_route)

                route = get_route(rest['lat'], rest['lng'], end[0], end[1])
                if route:
                    folium.PolyLine(
                        route,
                        color='#d4206e', weight=4, opacity=0.8,
                        popup=f"🚚 {distance:.1f}km - {delivery_time} phút (đường thực tế)"
                    ).add_to(m_route)
                else:
                    folium.PolyLine(
                        [start, end],
                        color='#d4206e', weight=3, opacity=0.7,
                        popup=f"🚚 {distance:.1f}km - {delivery_time} phút (ước lượng)"
                    ).add_to(m_route)

                st_folium(m_route, width="100%", height=390)

                st.markdown(f"""
                <div style="background: rgba(0,0,0,0.3); border-radius: 20px; padding: 12px; margin-top: 10px;">
                    <p><span class="info-label">🗺️ CHỈ ĐƯỜNG CHI TIẾT</span></p>
                    <ol style="color: #ffd700; margin-left: 20px; font-size: 0.8rem;">
                        <li>📍 Xuất phát từ <strong>{rest['Ten_quan']}</strong> tại {rest['Dia_chi']}</li>
                        <li>🛵 Di chuyển theo đường chính khoảng {distance:.1f}km</li>
                        <li>➡️ Rẽ phải tại ngã tư gần nhất</li>
                        <li>➡️ Đi thẳng qua {max(1, int(distance * 2))} ngã tư</li>
                        <li>🏁 Điểm đến: <strong>UEH {st.session_state.campus_name}</strong></li>
                        <li>⏱️ Thời gian dự kiến: <strong>{delivery_time} phút</strong></li>
                    </ol>
                </div>
                """, unsafe_allow_html=True)

        total_all += item['total']
        st.divider()

    st.markdown(f"""
    <div class="result-card">
        <h3>📊 TỔNG KẾT ĐƠN HÀNG</h3>
        <div class="food-detail-box">
            <p><span class="info-label">📦 SỐ MÓN</span> {len(st.session_state.cart)}</p>
            <p><span class="info-label">💰 TỔNG TIỀN HÀNG</span> {total_all - sum([item['shipping_fee'] for item in st.session_state.cart]):,.0f}đ</p>
            <p><span class="info-label">🚚 TỔNG PHÍ SHIP</span> {sum([item['shipping_fee'] for item in st.session_state.cart]):,.0f}đ</p>
            <p><span class="info-label">⏱️ THỜI GIAN GIAO DỰ KIẾN</span> {max([item['delivery_time'] for item in st.session_state.cart])} phút</p>
            <hr style="border-color: #ffd700;">
            <h2 style="text-align: right; color: #ffd700;">TỔNG CỘNG: {total_all:,.0f}đ</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_back, col_confirm = st.columns(2)
    with col_back:
        if st.button("🔙 QUAY LẠI GIỎ HÀNG", use_container_width=True):
            st.session_state.screen = 'result'
            st.rerun()
    with col_confirm:
        if st.button("✅ XÁC NHẬN ĐẶT HÀNG", use_container_width=True):
            max_delivery = max([item['delivery_time'] for item in st.session_state.cart]) if st.session_state.cart else 30
            st.session_state.last_order_delivery_time = max_delivery
            total_amount = sum([item['total'] for item in st.session_state.cart])
            rounded_amount = math.ceil(total_amount / 1000) * 1000
            st.session_state.last_order_total = rounded_amount
            st.session_state.order_count += 1
            st.session_state.cart.clear()
            st.session_state.active_delivery = True
            st.session_state.screen = 'main'
            st.balloons()
            st.success(f"🎉 ĐẶT HÀNG THÀNH CÔNG!\n\n💰 Tổng tiền: {rounded_amount:,}đ\n⏱️ Dự kiến giao trong {max_delivery} phút\n\nCảm ơn bạn đã sử dụng Harmoni!")
            time.sleep(2)
            st.rerun()


st.markdown(f"""
<div class="moving-decor-container">
    <img src="data:image/png;base64,{decor_left}" class="moving-decor-item" style="transform: rotate(-5deg);">
    <img src="data:image/png;base64,{decor_right}" class="moving-decor-item" style="transform: rotate(5deg);">
</div>
<div class="footer">
    <p style="color: #ffd700 !important; margin:0;">✨ Harmoni - Dung dăng ăn khoẻ, xắc quẻ liền tay ✨ | #1 App for Food Recommendation and ordering</p>
</div>
""", unsafe_allow_html=True)