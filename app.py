import sqlite3
import pandas as pd
import streamlit as st
import hashlib
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="SmartCart India", layout="wide")

# --- DATABASE SETUP (SQLite) ---
conn = sqlite3.connect("smartcart_india.db", check_same_thread=False)
cursor = conn.cursor()

# Users Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
""")

# Orders Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        items TEXT,
        total_amount INTEGER,
        full_name TEXT,
        phone TEXT,
        address TEXT,
        city TEXT,
        pincode TEXT,
        payment_mode TEXT,
        order_date TEXT
    )
""")
conn.commit()

# Helper Functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                       (username, hash_password(password)))
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                   (username, hash_password(password)))
    return cursor.fetchone()

def create_order(username, items, total_amount, full_name, phone, address, city, pincode, payment_mode):
    order_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    cursor.execute("""
        INSERT INTO orders (username, items, total_amount, full_name, phone, address, city, pincode, payment_mode, order_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, items, total_amount, full_name, phone, address, city, pincode, payment_mode, order_date))
    conn.commit()

def get_user_orders(username):
    cursor.execute("""
        SELECT order_id, items, total_amount, full_name, phone, address, city, pincode, payment_mode, order_date 
        FROM orders WHERE username = ? ORDER BY order_id DESC
    """, (username,))
    return cursor.fetchall()

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if "cart" not in st.session_state:
    st.session_state.cart = []

# --- PRODUCTS DATASET ---
@st.cache_data
def load_products():
    products = [
        {"ID": 101, "Name": "Logitech G-Pro Wireless Mouse", "Category": "Electronics", "Price": 1499, "Rating": 4.8, "Tags": "Gaming", "Image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500&q=80"},
        {"ID": 102, "Name": "Keychron RGB Mechanical Keyboard", "Category": "Electronics", "Price": 3499, "Rating": 4.9, "Tags": "Coding", "Image": "https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?w=500&q=80"},
        {"ID": 103, "Name": "Asus Aluminum Laptop Stand", "Category": "Electronics", "Price": 999, "Rating": 4.5, "Tags": "Desk Setup", "Image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500&q=80"},
        {"ID": 104, "Name": "SanDisk 1TB Portable SSD", "Category": "Electronics", "Price": 6499, "Rating": 4.8, "Tags": "Storage", "Image": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=500&q=80"},
        {"ID": 105, "Name": "Mi 20000mAh Power Bank", "Category": "Electronics", "Price": 1899, "Rating": 4.6, "Tags": "Travel", "Image": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=500&q=80"},
        {"ID": 106, "Name": "Logitech 1080p HD Webcam", "Category": "Electronics", "Price": 2499, "Rating": 4.4, "Tags": "Camera", "Image": "https://images.unsplash.com/photo-1587826080692-f439cd0b70da?w=500&q=80"},
        {"ID": 107, "Name": "Sony WH-1000XM4 Headphones", "Category": "Audio", "Price": 14999, "Rating": 4.9, "Tags": "ANC Audio", "Image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80"},
        {"ID": 108, "Name": "boAt Airdopes 441 TWS", "Category": "Audio", "Price": 1299, "Rating": 4.4, "Tags": "Earbuds", "Image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&q=80"},
        {"ID": 109, "Name": "Samsung Galaxy Watch 6", "Category": "Audio", "Price": 12499, "Rating": 4.7, "Tags": "Smartwatch", "Image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80"},
        {"ID": 110, "Name": "JBL Flip 6 Bluetooth Speaker", "Category": "Audio", "Price": 7999, "Rating": 4.8, "Tags": "Speaker", "Image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500&q=80"},
        {"ID": 111, "Name": "Noise ColorFit Smartwatch", "Category": "Audio", "Price": 1599, "Rating": 4.3, "Tags": "Fitness", "Image": "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500&q=80"},
        {"ID": 112, "Name": "Blue Yeti USB Microphone", "Category": "Audio", "Price": 8499, "Rating": 4.7, "Tags": "Streaming", "Image": "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=500&q=80"},
        {"ID": 113, "Name": "Nike Air Zoom Running Shoes", "Category": "Footwear", "Price": 4299, "Rating": 4.8, "Tags": "Running", "Image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80"},
        {"ID": 114, "Name": "Adidas Ultraboost Sneakers", "Category": "Footwear", "Price": 5499, "Rating": 4.7, "Tags": "Casual", "Image": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500&q=80"},
        {"ID": 115, "Name": "Puma White Sneakers", "Category": "Footwear", "Price": 2799, "Rating": 4.5, "Tags": "Fashion", "Image": "https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?w=500&q=80"},
        {"ID": 116, "Name": "Woodland Trekking Boots", "Category": "Footwear", "Price": 3899, "Rating": 4.6, "Tags": "Outdoor", "Image": "https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=500&q=80"},
        {"ID": 117, "Name": "Converse Canvas Shoes", "Category": "Footwear", "Price": 2199, "Rating": 4.6, "Tags": "College", "Image": "https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=500&q=80"},
        {"ID": 118, "Name": "Skechers Walking Shoes", "Category": "Footwear", "Price": 2499, "Rating": 4.4, "Tags": "Comfort", "Image": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=500&q=80"},
        {"ID": 119, "Name": "Wildcraft Laptop Backpack", "Category": "Fashion", "Price": 1699, "Rating": 4.6, "Tags": "Bag", "Image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&q=80"},
        {"ID": 120, "Name": "Puma Gym Duffel Bag", "Category": "Fashion", "Price": 1199, "Rating": 4.4, "Tags": "Gym", "Image": "https://images.unsplash.com/photo-1547949003-9792a18a2601?w=500&q=80"},
        {"ID": 121, "Name": "Ray-Ban Aviator Sunglasses", "Category": "Fashion", "Price": 3299, "Rating": 4.7, "Tags": "Glasses", "Image": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=500&q=80"},
        {"ID": 122, "Name": "Levi's Denim Jacket", "Category": "Fashion", "Price": 2899, "Rating": 4.8, "Tags": "Jacket", "Image": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=500&q=80"},
        {"ID": 123, "Name": "Titan Leather Watch", "Category": "Fashion", "Price": 2599, "Rating": 4.6, "Tags": "Watch", "Image": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500&q=80"},
        {"ID": 124, "Name": "Tommy Hilfiger Wallet", "Category": "Fashion", "Price": 1399, "Rating": 4.5, "Tags": "Wallet", "Image": "https://images.unsplash.com/photo-1627123424574-724758594e93?w=500&q=80"},
        {"ID": 125, "Name": "Wipro LED Study Lamp", "Category": "Lifestyle", "Price": 899, "Rating": 4.5, "Tags": "Lamp", "Image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500&q=80"},
        {"ID": 126, "Name": "Milton Thermosteel Flask", "Category": "Lifestyle", "Price": 799, "Rating": 4.7, "Tags": "Bottle", "Image": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500&q=80"},
        {"ID": 127, "Name": "Nescafe Coffee Maker", "Category": "Lifestyle", "Price": 1999, "Rating": 4.6, "Tags": "Coffee", "Image": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=500&q=80"},
        {"ID": 128, "Name": "Boldfit Yoga Mat", "Category": "Lifestyle", "Price": 699, "Rating": 4.4, "Tags": "Workout", "Image": "https://images.unsplash.com/photo-1592432678016-e910b452f9a2?w=500&q=80"},
        {"ID": 129, "Name": "Casio Scientific Calculator", "Category": "Lifestyle", "Price": 950, "Rating": 4.9, "Tags": "Study", "Image": "https://images.unsplash.com/photo-1587145820266-a5951ee6f620?w=500&q=80"},
        {"ID": 130, "Name": "Ergonomic Office Chair", "Category": "Lifestyle", "Price": 5999, "Rating": 4.7, "Tags": "Chair", "Image": "https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?w=500&q=80"}
    ]
    return pd.DataFrame(products)

df = load_products()

# --- AUTHENTICATION SCREEN ---
if not st.session_state.logged_in:
    st.title("🛒 SmartCart India: E-Commerce Portal")
    st.write("B.Sc. Computer Science Project — Product Recommendation & Order System")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 User Login", "📝 New Registration"])
        
        with tab1:
            st.subheader("Login to Your Account")
            user = st.text_input("Username", key="login_user")
            pw = st.text_input("Password", type="password", key="login_pw")
            if st.button("Login", use_container_width=True):
                if login_user(user, pw):
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.rerun()
                else:
                    st.error("Invalid Username or Password!")

        with tab2:
            st.subheader("Create New Account")
            new_user = st.text_input("Choose Username", key="reg_user")
            new_pw = st.text_input("Choose Password", type="password", key="reg_pw")
            if st.button("Register Account", use_container_width=True):
                if new_user and new_pw:
                    if register_user(new_user, new_pw):
                        st.success("Account created successfully! Ab Login tab se login karein.")
                    else:
                        st.error("Yeh Username pehle se maujood hai.")
                else:
                    st.warning("Username aur Password dono bharna zaroori hai.")

# --- MAIN APP ---
else:
    st.sidebar.title(f"👤 Hi, {st.session_state.username}")
    
    cart_count = sum(item["qty"] for item in st.session_state.cart)
    cart_total = sum(item["price"] * item["qty"] for item in st.session_state.cart)
    
    st.sidebar.info(f"🛒 **Cart:** {cart_count} items | **Total:** ₹{cart_total:,}")
    
    page = st.sidebar.radio(
        "Navigation", 
        [
            "🛍️ Shop & Recommendations", 
            f"🛒 My Cart & Checkout ({cart_count})", 
            "📦 My Orders (Database)"
        ]
    )
    
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.cart = []
        st.rerun()

    if page.startswith("🛍️"):
        st.title("🛍️ SmartCart Product Catalog")
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎯 Filters")
        search_query = st.sidebar.text_input("🔍 Search Product")
        selected_cat = st.sidebar.selectbox("Category", ["All"] + list(df["Category"].unique()))
        budget = st.sidebar.slider("Max Budget (₹)", 500, 15000, 15000, step=500)
        min_rating = st.sidebar.slider("Min Rating", 4.0, 5.0, 4.3, step=0.1)

        filtered = df[(df["Price"] <= budget) & (df["Rating"] >= min_rating)]
        if selected_cat != "All":
            filtered = filtered[filtered["Category"] == selected_cat]
        if search_query:
            filtered = filtered[filtered["Name"].str.contains(search_query, case=False)]

        filtered = filtered.sort_values(by="Rating", ascending=False)
        st.subheader(f"Showing {len(filtered)} Products")

        if filtered.empty:
            st.warning("Koi product nahi mila. Filter adjust karein.")
        else:
            cols = st.columns(3)
            for idx, (_, row) in enumerate(filtered.iterrows()):
                with cols[idx % 3]:
                    st.image(row['Image'], use_container_width=True)
                    st.subheader(row['Name'])
                    st.write(f"Category: {row['Category']} | ⭐ {row['Rating']}")
                    st.markdown(f"### ₹{row['Price']:,}")
                    
                    if st.button(f"Add to Cart", key=f"add_{row['ID']}", use_container_width=True):
                        found = False
                        for item in st.session_state.cart:
                            if item["id"] == row["ID"]:
                                item["qty"] += 1
                                found = True
                                break
                        if not found:
                            st.session_state.cart.append({
                                "id": row["ID"],
                                "name": row["Name"],
                                "price": int(row["Price"]),
                                "image": row["Image"],
                                "qty": 1
                            })
                        st.success("Added to cart!")
                        st.rerun()

    elif page.startswith("🛒"):
        st.title("🛒 Shopping Cart & Checkout")
        
        if not st.session_state.cart:
            st.info("Aapka cart khali hai.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Cart Items")
                for i, item in enumerate(st.session_state.cart):
                    st.write(f"**{item['name']}** - ₹{item['price']} x {item['qty']} = ₹{item['price']*item['qty']}")
                    if st.button("Remove", key=f"rem_{item['id']}"):
                        st.session_state.cart.pop(i)
                        st.rerun()
                st.markdown(f"### Total Amount: ₹{cart_total:,}")

            with col2:
                st.subheader("Delivery Address & Payment")
                with st.form("checkout"):
                    full_name = st.text_input("Full Name")
                    phone = st.text_input("Phone Number", max_chars=10)
                    address = st.text_area("Address")
                    city = st.text_input("City")
                    pincode = st.text_input("PIN Code", max_chars=6)
                    payment_mode = st.selectbox("Payment", ["COD", "UPI", "Card"])
                    
                    if st.form_submit_button("Place Order", use_container_width=True):
                        if full_name and phone and address and city and pincode:
                            items_summary = ", ".join([f"{i['name']} (x{i['qty']})" for i in st.session_state.cart])
                            create_order(st.session_state.username, items_summary, cart_total, full_name, phone, address, city, pincode, payment_mode)
                            st.session_state.cart = []
                            st.success("Order Placed Successfully!")
                        else:
                            st.error("Saare details bharein!")

    elif page.startswith("📦"):
        st.title("📦 Order History")
        orders = get_user_orders(st.session_state.username)
        if not orders:
            st.info("Koi order nahi hai.")
        else:
            for o in orders:
                st.write(f"**Order ID:** {o[0]} | **Items:** {o[1]} | **Total:** ₹{o[2]} | **Date:** {o[9]}")
                st.write(f"**Address:** {o[3]}, {o[4]} - {o[5]}, {o[6]} ({o[7]}) | **Payment:** {o[8]}")
                st.markdown("---")