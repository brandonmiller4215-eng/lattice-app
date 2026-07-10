import streamlit as st
import pandas as pd
import base64
from PIL import Image
import io

# 1. Page & Layout Optimization
st.set_page_config(
    page_title="Lattice: Local Exchange Loop", 
    page_icon="🕸️", 
    layout="centered"
)

# 2. State Initialization (With Image Placeholder Capability)
if "local_inventory" not in st.session_state:
    st.session_state.local_inventory = [
        {"id": 0, "seller": "Oak Street Collective", "item": "Organic Tomatoes", "category": "Food", "qty": 15, "price": 3.50, "zip": "78201", "image": None},
        {"id": 1, "seller": "Elena's Textiles", "item": "Handmade Wool Blanket", "category": "Goods", "qty": 3, "price": 65.00, "zip": "78201", "image": None},
        {"id": 2, "seller": "Community Tool Library", "item": "Rototiller Rental", "category": "Tools", "qty": 1, "price": 10.00, "zip": "78212", "image": None},
        {"id": 3, "seller": "Mendoza Farm", "item": "Free-Range Eggs (Dozen)", "category": "Food", "qty": 12, "price": 5.00, "zip": "78212", "image": None},
    ]

if "retained_capital" not in st.session_state:
    st.session_state.retained_capital = 0.0

# NEW FEATURE: Spatial Distance Grid (Calculates distance between neighbor nodes without tracking)
ZIP_PROXIMITY_MATRIX = {
    "78201": {"78201": 0.0, "78212": 2.1, "78207": 3.5, "78209": 4.8},
    "78212": {"78201": 2.1, "78212": 0.0, "78207": 2.8, "78209": 3.1},
    "78207": {"78201": 3.5, "78212": 2.8, "78207": 0.0, "78209": 5.9},
    "78209": {"78201": 4.8, "78212": 3.1, "78207": 5.9, "78209": 0.0},
}

def calculate_distance(user_zip, item_zip):
    """Safely extracts pre-computed distance from the matrix mesh."""
    if user_zip == item_zip:
        return 0.0
    if user_zip in ZIP_PROXIMITY_MATRIX and item_zip in ZIP_PROXIMITY_MATRIX[user_zip]:
        return ZIP_PROXIMITY_MATRIX[user_zip][item_zip]
    # Fallback default if nodes belong to different regional grids
    return "Out of Grid"

# Helper function to compress and convert images to Base64 text strings
def process_uploaded_image(uploaded_file):
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image.thumbnail((300, 300)) 
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=70)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    return None

# 3. Main Interface Header
st.title("🕸️ Lattice Core Prototype")
st.markdown("A decentralized framework for independent local supply chains.")
st.markdown("---")

# 4. Interface Modes
view_mode = st.radio(
    "Select System Action:", 
    ["Find Local Needs", "Register Local Supply"], 
    horizontal=True
)

st.markdown("---")

# 5. Controller Logic: Find Local Needs (Consumer View)
if view_mode == "Find Local Needs":
    st.subheader("🔍 Local Network Query")
    
    # 📍 Location Coordinates
    user_zip = st.text_input("Enter Your Current ZIP Code Location", value="78201", max_chars=5).strip()
    
    # Search Filter Row
    col_search, col_cat = st.columns(2)
    with col_search:
        search_query = st.text_input("Search items by keyword...", value="").strip().lower()
    with col_cat:
        category_filter = st.selectbox("Category Filter", ["All", "Food", "Goods", "Tools", "Services"])
    
    # 🧮 Execute Multi-Layer Filtering Algorithm
    current_items = st.session_state.local_inventory
    filtered_items = []
    
    # Process all available nodes globally and attach distance values dynamically
    for item in current_items:
        dist = calculate_distance(user_zip, item["zip"])
        
        # Filter 1: Max range constraint (hides options too far away from the local loop)
        if dist != "Out of Grid" and dist <= 10.0:
            item_copy = item.copy()
            item_copy["distance"] = dist
            filtered_items.append(item_copy)
            
    # Filter 2: Category Match
    if category_filter != "All":
        filtered_items = [i for i in filtered_items if i["category"] == category_filter]
        
    # Filter 3: Text Keyword Search
    if search_query:
        filtered_items = [
            i for i in filtered_items 
            if search_query in i["item"].lower() or search_query in i["seller"].lower()
        ]
        
    # Sort items dynamically: closest resources rank highest!
    filtered_items = sorted(filtered_items, key=lambda x: x["distance"] if isinstance(x["distance"], float) else 999)
    
    # Display Results
    if not filtered_items:
        st.info("No matching local supply nodes found within range of your location configuration.")
    else:
        st.write(f"### Matching Options ({len(filtered_items)} found):")
        
        for item in filtered_items:
            with st.container():
                col_img, col_info, col_action = st.columns(3)
                
                with col_img:
                    if item.get("image"):
                        st.image(item["image"], use_column_width=True)
                    else:
                        st.markdown("🖼️\n*(No Image)*")
                
                with col_info:
                    st.markdown(f"#### **{item['item']}**")
                    st.markdown(f"*By: {item['seller']}*")
                    
                    # Visually highlight distance tags so users see proximity immediately
                    if item["distance"] == 0.0:
                        st.markdown("📍 **Distance:** `Right in your immediate ZIP!`")
                    else:
                        st.markdown(f"📍 **Distance:** `{item['distance']} miles away`")
                        
                    st.markdown(f"Category: `{item['category']}` | **Price:** ${item['price']:.2f}")
                
                with col_action:
                    st.write(f"Available: {item['qty']}") 
                    if item["qty"] <= 0:
                        st.button("Sold Out", key=f"dead_{item['id']}", disabled=True)
                    else:
                        if st.button(f"Acquire", key=f"buy_{item['id']}"):
                            # Update master copy state
                            for original_item in st.session_state.local_inventory:
                                if original_item["id"] == item["id"]:
                                    original_item["qty"] -= 1
                            st.session_state.retained_capital += item["price"]
                            st.success(f"Acquired!")
                            st.rerun()
                st.markdown("---")

# 6. Controller Logic: Register Local Supply (Seller View)
elif view_mode == "Register Local Supply":
    st.subheader("🌾 Broadcast New Production Capacity")
    
    with st.form("inventory_form", clear_on_submit=True):
        new_seller = st.text_input("Seller / Collective Name").strip()
        new_item = st.text_input("Resource or Skill Provided").strip()
        new_cat = st.selectbox("Classification", ["Food", "Goods", "Tools", "Services"])
        new_qty = st.number_input("Available Stock Quantity", min_value=1, value=5, step=1)
        new_price = st.number_input("Resource Value ($ per unit)", min_value=0.01, value=1.00, step=0.50)
        new_zip = st.text_input("Local ZIP Coordinates", value="78201", max_chars=5).strip()
        
        uploaded_img = st.file_uploader("Upload or Snap a Photo of Your Item", type=["jpg", "jpeg", "png"], accept_multiple_files=False, help="Max file size: 2MB")
        
        submit_btn = st.form_submit_button("Broadcast to Grid")
        
        if submit_btn:
            if not new_seller or not new_item or not new_zip:
                st.error("All structural data fields must be populated to authorize registration.")
            else:
                base64_image = process_uploaded_image(uploaded_img)
                
                next_id = len(st.session_state.local_inventory)
                st.session_state.local_inventory.append({
                    "id": next_id,
                    "seller": new_seller,
                    "item": new_item,
                    "category": new_cat,
                    "qty": int(new_qty),
                    "price": float(new_price),
                    "zip": new_zip,
                    "image": base64_image
                })
                st.success(f"Successfully broadcasted {new_item} with visual verification.")
                st.rerun()

# 7. Metrics Sidebar Tracker
st.sidebar.subheader("📉 Network Resilience Metrics")
st.sidebar.metric(
    label="Capital Diverted from Corporate Hubs", 
    value=f"${st.session_state.retained_capital:.2f}"
        )
