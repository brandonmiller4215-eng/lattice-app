import streamlit as st
import pandas as pd
import base64
from PIL import Image
import io
import datetime

# 1. Page & Layout Optimization
st.set_page_config(
    page_title="Lattice: Local Exchange Loop", 
    page_icon="🕸️", 
    layout="centered"
)

# 2. State & Memory Hub Initialization
if "local_inventory" not in st.session_state:
    st.session_state.local_inventory = [
        {"id": 0, "seller": "Oak Street Collective", "item": "Organic Tomatoes", "category": "Food", "qty": 15, "price": 3.50, "zip": "78201", "image": None},
        {"id": 1, "seller": "Elena's Textiles", "item": "Handmade Wool Blanket", "category": "Goods", "qty": 3, "price": 65.00, "zip": "78201", "image": None},
        {"id": 2, "seller": "Community Tool Library", "item": "Rototiller Rental", "category": "Tools", "qty": 1, "price": 10.00, "zip": "78212", "image": None},
        {"id": 3, "seller": "Mendoza Farm", "item": "Free-Range Eggs (Dozen)", "category": "Food", "qty": 12, "price": 5.00, "zip": "78212", "image": None},
    ]

if "retained_capital" not in st.session_state:
    st.session_state.retained_capital = 0.0

# NEW FEATURE: Volatile In-Memory Message Mesh (Stored in RAM, never writes to disk)
if "secure_message_wall" not in st.session_state:
    st.session_state.secure_message_wall = [
        {"zip": "78201", "alias": "AnonNode_1", "text": "Leaving seeds at the community box on Main St at noon.", "time": "10:15"},
        {"zip": "78212", "alias": "ToolShare_Alpha", "text": "Rototiller is cleaned, sanitized, and ready for pickup.", "time": "09:30"}
    ]

# Spatial Distance Matrix
ZIP_PROXIMITY_MATRIX = {
    "78201": {"78201": 0.0, "78212": 2.1, "78207": 3.5, "78209": 4.8},
    "78212": {"78201": 2.1, "78212": 0.0, "78207": 2.8, "78209": 3.1},
    "78207": {"78201": 3.5, "78212": 2.8, "78207": 0.0, "78209": 5.9},
    "78209": {"78201": 4.8, "78212": 3.1, "78207": 5.9, "78209": 0.0},
}

def calculate_distance(user_zip, item_zip):
    if user_zip == item_zip:
        return 0.0
    if user_zip in ZIP_PROXIMITY_MATRIX and item_zip in ZIP_PROXIMITY_MATRIX[user_zip]:
        return ZIP_PROXIMITY_MATRIX[user_zip][item_zip]
    return "Out of Grid"

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
    ["Find Local Needs", "Register Local Supply", "Secure Community Wall"], 
    horizontal=True
)

st.markdown("---")

# 5. Controller Logic: Find Local Needs
if view_mode == "Find Local Needs":
    st.subheader("🔍 Local Network Query")
    user_zip = st.text_input("Enter Your Current ZIP Code Location", value="78201", max_chars=5).strip()
    
    col_search, col_cat = st.columns(2)
    with col_search:
        search_query = st.text_input("Search items by keyword...", value="").strip().lower()
    with col_cat:
        category_filter = st.selectbox("Category Filter", ["All", "Food", "Goods", "Tools", "Services"])
    
    current_items = st.session_state.local_inventory
    filtered_items = []
    
    for item in current_items:
        dist = calculate_distance(user_zip, item["zip"])
        if dist != "Out of Grid" and dist <= 10.0:
            item_copy = item.copy()
            item_copy["distance"] = dist
            filtered_items.append(item_copy)
            
    if category_filter != "All":
        filtered_items = [i for i in filtered_items if i["category"] == category_filter]
        
    if search_query:
        filtered_items = [
            i for i in filtered_items 
            if search_query in i["item"].lower() or search_query in i["seller"].lower()
        ]
        
    filtered_items = sorted(filtered_items, key=lambda x: x["distance"] if isinstance(x["distance"], float) else 999)
    
    if not filtered_items:
        st.info("No matching local supply nodes found within range.")
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
                            for original_item in st.session_state.local_inventory:
                                if original_item["id"] == item["id"]:
                                    original_item["qty"] -= 1
                            st.session_state.retained_capital += item["price"]
                            st.success(f"Acquired!")
                            st.rerun()
                st.markdown("---")

# 6. Controller Logic: Register Local Supply
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
                st.error("All structural data fields must be populated.")
            else:
                base64_image = process_uploaded_image(uploaded_img)
                next_id = len(st.session_state.local_inventory)
                st.session_state.local_inventory.append({
                    "id": next_id, "seller": new_seller, "item": new_item, "category": new_cat,
                    "qty": int(new_qty), "price": float(new_price), "zip": new_zip, "image": base64_image
                })
                st.success(f"Successfully broadcasted {new_item}.")
                st.rerun()

# 7. NEW CONTROLLER LOGIC: Secure Community Wall (Untraceable Routing Mesh)
elif view_mode == "Secure Community Wall":
    st.subheader("💬 Untraceable Neighborhood Broadcast Wall")
    st.markdown("🔒 *Messages exist solely in temporary server RAM. No storage disks or user profile data logged.*")
    
    user_zip = st.text_input("Enter Your Location ZIP to Filter Local Transmissions", value="78201", max_chars=5).strip()
    
    # Message Dispatch Form
    with st.form("message_form", clear_on_submit=True):
        col_alias, col_txt = st.columns([1, 3])
        with col_alias:
            msg_alias = st.text_input("Temporary Alias", value="AnonNode", max_chars=15).strip()
        with col_txt:
            msg_text = st.text_input("Type Secure Message Payload (e.g., meetup coordinates, drop-offs)...", max_chars=140).strip()
        
        broadcast_msg_btn = st.form_submit_button("Transmit Packet")
        
        if broadcast_msg_btn:
            if not msg_text or not user_zip:
                st.error("Cannot broadcast an empty message packet.")
            else:
                current_time = datetime.datetime.now().strftime("%H:%M")
                new_packet = {
                    "zip": user_zip,
                    "alias": msg_alias if msg_alias else "AnonNode",
                    "text": msg_text,
                    "time": current_time
                }
                # Inject new packet directly into the front of the RAM queue
                st.session_state.secure_message_wall.insert(0, new_packet)
                
                # AUTOMATIC ROLLING SCRUBBER: Retain only the last 15 local packets to purge old trails
                if len(st.session_state.secure_message_wall) > 15:
                    st.session_state.secure_message_wall = st.session_state.secure_message_wall[:15]
                    
                st.success("Packet transmitted to local loop coordinates.")
                st.rerun()
                
    # Render Relevant Location Packets
    st.write("---")
    st.write(f"### Live Signals Decoded Near ZIP {user_zip}:")
    
    wall_packets = st.session_state.secure_message_wall
    visible_packets = 0
    
    for pkt in wall_packets:
        dist = calculate_distance(user_zip, pkt["zip"])
