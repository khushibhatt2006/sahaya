import streamlit as st
from datetime import date
import os
from db import add_donation
import time

def show_donation_form(username):
    
    st.markdown("### Share what you have – someone needs it! ❤️")

    # ====================== LOCATION ======================
    st.subheader("📍 Your Location")
    col1, col2 = st.columns(2)
    with col1:
        states = ["Select State", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
                 "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", 
                 "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", 
                 "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
                 "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi", "Jammu and Kashmir", "Ladakh"]
        donor_state = st.selectbox("State *", states, index=0, key="donor_state_select")

    with col2:
        city_list = ["Select City"]
        if donor_state == "Andhra Pradesh":
            city_list += ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Rajahmundry", "Tirupati", "Other"]
        elif donor_state == "Arunachal Pradesh":
            city_list += ["Itanagar", "Tawang", "Pasighat", "Other"]
        elif donor_state == "Assam":
            city_list += ["Guwahati", "Silchar", "Dibrugarh", "Jorhat", "Nagaon", "Tezpur", "Other"]
        elif donor_state == "Bihar":
            city_list += ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia", "Darbhanga", "Other"]
        elif donor_state == "Chhattisgarh":
            city_list += ["Raipur", "Bhilai", "Bilaspur", "Korba", "Durg", "Other"]
        elif donor_state == "Goa":
            city_list += ["Panaji", "Margao", "Vasco da Gama", "Other"]
        elif donor_state == "Gujarat":
            city_list += ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Junagadh", "Gandhinagar", "Other"]
        elif donor_state == "Haryana":
            city_list += ["Gurugram", "Faridabad", "Panipat", "Ambala", "Karnal", "Other"]
        elif donor_state == "Himachal Pradesh":
            city_list += ["Shimla", "Manali", "Dharamshala", "Kullu", "Other"]
        elif donor_state == "Jharkhand":
            city_list += ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Other"]
        elif donor_state == "Karnataka":
            city_list += ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi", "Davanagere", "Other"]
        elif donor_state == "Kerala":
            city_list += ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Alappuzha", "Other"]
        elif donor_state == "Madhya Pradesh":
            city_list += ["Bhopal", "Indore", "Jabalpur", "Gwalior", "Ujjain", "Other"]
        elif donor_state == "Maharashtra":
            city_list += ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Solapur", "Kolhapur", "Thane", 
                         "Pimpri-Chinchwad", "Amravati", "Nanded", "Akola", "Jalgaon", "Other"]
        elif donor_state == "Manipur":
            city_list += ["Imphal", "Other"]
        elif donor_state == "Meghalaya":
            city_list += ["Shillong", "Other"]
        elif donor_state == "Mizoram":
            city_list += ["Aizawl", "Other"]
        elif donor_state == "Nagaland":
            city_list += ["Kohima", "Dimapur", "Other"]
        elif donor_state == "Odisha":
            city_list += ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Other"]
        elif donor_state == "Punjab":
            city_list += ["Chandigarh", "Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Other"]
        elif donor_state == "Rajasthan":
            city_list += ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner", "Other"]
        elif donor_state == "Sikkim":
            city_list += ["Gangtok", "Other"]
        elif donor_state == "Tamil Nadu":
            city_list += ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Erode", "Other"]
        elif donor_state == "Telangana":
            city_list += ["Hyderabad", "Warangal", "Nizamabad", "Other"]
        elif donor_state == "Tripura":
            city_list += ["Agartala", "Other"]
        elif donor_state == "Uttar Pradesh":
            city_list += ["Lucknow", "Kanpur", "Varanasi", "Agra", "Meerut", "Allahabad", "Ghaziabad", "Noida", "Other"]
        elif donor_state == "Uttarakhand":
            city_list += ["Dehradun", "Haridwar", "Nainital", "Other"]
        elif donor_state == "West Bengal":
            city_list += ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri", "Other"]
        elif donor_state == "Delhi":
            city_list += ["Delhi", "New Delhi", "Other"]
        elif donor_state == "Jammu and Kashmir":
            city_list += ["Srinagar", "Jammu", "Other"]
        elif donor_state == "Ladakh":
            city_list += ["Leh", "Kargil", "Other"]
        else:
            city_list += ["Other"]

        donor_city = st.selectbox("City *", city_list, index=0, key="donor_city_select")

    # ====================== DONATION DETAILS ======================
    st.markdown("---")
    category = st.selectbox(
        "Select Category to Donate *",
        ["Select Category", "📚 Books", "🍛 Food", "💊 Medicine", "👕 Clothes", "🍽️ Utensils"],
        index=0,
        key="donation_category"
    )

    title = st.text_input("Title / Item Name *", placeholder="e.g. Ikigai Book or Rice 5kg", key="title_key")
    description = st.text_area("Description *", placeholder="Write a short description about the item...", key="desc_key")
    quantity = st.number_input("Quantity *", min_value=1, value=1, key="qty_key")

    extra_info = ""

    if category != "Select Category":
        if "Books" in category:
            author = st.text_input("Author Name (optional)", key="author_key")
            condition = st.selectbox("Condition", ["Select Condition", "New", "Like New", "Good", "Fair", "Used"], index=0, key="condition_key")
            if author:
                extra_info += f"Author: {author}\n"
            if condition != "Select Condition":
                extra_info += f"Condition: {condition}"

        elif "Food" in category:
            expiry = st.date_input("Expiry Date", value=date.today(), key="expiry_key")
            food_type = st.selectbox("Food Type", ["Select Type", "Cooked Meal", "Raw Grains", "Packaged", "Fruits & Vegetables"], index=0, key="food_type_key")
            is_urgent = st.checkbox("🚨 Mark as Urgent Delivery", key="urgent_key")
            if food_type != "Select Type":
                extra_info += f"Expiry Date: {expiry}\nFood Type: {food_type}"
            if is_urgent:
                extra_info += "\nPriority: Urgent"

        elif "Medicine" in category:
            expiry = st.date_input("Expiry Date", value=date.today(), key="expiry_key")
            med_type = st.selectbox("Medicine Type", ["Select Type", "Tablets", "Syrup", "Ointment", "Others"], index=0, key="med_type_key")
            prescription = st.checkbox("Prescription Required", key="prescription_key")
            if med_type != "Select Type":
                extra_info += f"Expiry Date: {expiry}\nType: {med_type}"
            if prescription:
                extra_info += "\nPrescription Needed: Yes"

        elif "Clothes" in category:
            size = st.selectbox("Size", ["Select Size", "XS", "S", "M", "L", "XL", "XXL", "Kids"], index=0, key="size_key")
            gender = st.selectbox("For", ["Select", "Men", "Women", "Kids", "Unisex"], index=0, key="gender_key")
            condition = st.selectbox("Condition", ["Select Condition", "New", "Good", "Fair", "Used"], index=0, key="condition_key")
            if size != "Select Size":
                extra_info += f"Size: {size}\n"
            if gender != "Select":
                extra_info += f"For: {gender}\n"
            if condition != "Select Condition":
                extra_info += f"Condition: {condition}"

        elif "Utensils" in category:
            material = st.selectbox("Material", ["Select Material", "Stainless Steel", "Plastic", "Glass", "Ceramic"], index=0, key="material_key")
            condition = st.selectbox("Condition", ["Select Condition", "New", "Good", "Fair", "Used"], index=0, key="condition_key")
            if material != "Select Material":
                extra_info += f"Material: {material}\n"
            if condition != "Select Condition":
                extra_info += f"Condition: {condition}"

    # Token of Love - Only for Books (Min ₹10, Max ₹50)
    st.markdown("---")
    token_amount = 0
    if category != "Select Category" and "Books" in category:
        st.subheader("💝 Token of Love")
        st.caption("A small contribution from the receiver as a token of gratitude (₹10 - ₹50)")
        token_amount = st.number_input("Token Amount (₹)", min_value=10, max_value=50, value=20, step=5, key="token_key")
    else:
        st.caption("💝 Token of Love is only available for Books")

    donor_note = st.text_area("💌 Small Note for the Receiver (Optional)", 
                             placeholder="Hope this helps someone in need...", key="note_key")

    # Image Upload at the bottom
    st.markdown("---")
    st.subheader("📸 Upload Photo of Item (Optional)")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"], key="donation_image")

    image_path = ""
    if uploaded_file:
        os.makedirs("uploads", exist_ok=True)
        image_path = f"uploads/{username}_{uploaded_file.name}"
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("✅ Photo uploaded successfully!")

    # Submit Button
    if st.button("Donate Now ❤️", type="primary", use_container_width=True):
        if not title or not title.strip():
            st.error("❌ Please enter Title / Item Name")
            return
        if category == "Select Category":
            st.error("❌ Please select a Category")
            return
        if donor_state == "Select State" or donor_city == "Select City":
            st.error("❌ Please select your State and City")
            return

        final_description = description.strip()
        if extra_info:
            final_description += "\n\n--- Extra Details ---\n" + extra_info

        location_info = f"Location: {donor_city}, {donor_state}"
        final_description = location_info + "\n\n" + final_description

        add_donation(
            donor_username=username,
            category=category.split()[-1].lower(),
            title=title.strip(),
            description=final_description,
            quantity=quantity,
            token_amount=token_amount,
            donor_note=donor_note,
            image_path=image_path
        )
        # Fixed Success Message
        st.success("🎉 Thank you! Your donation has been posted successfully!")
        st.rerun()
        st.balloons()
        time.sleep(20)      # Holds the message for 10 seconds
        st.rerun()
    
        
        # Optional badge message
        if (st.session_state.get('total_donated', 0) + 1) % 10 == 0:
            st.success(f"🎊 Congratulations! You earned a new badge for {st.session_state.get('total_donated', 0) + 1} donations!")

