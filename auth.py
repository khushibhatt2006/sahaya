import streamlit as st
import os
import re
from db import get_user, add_user, update_profile

def login():
    st.title("🔑 Login to Sahaya")
    st.markdown("### Welcome back! Helping hands start here 🤎")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Username", placeholder="e.g. donor1", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary", use_container_width=True):
            user = get_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.role = user["role"]
                st.session_state.full_name = user["full_name"]
                st.session_state.phone = user.get("phone", "")
                st.session_state.email = user.get("email", "")
                st.session_state.address = user.get("address", "")
                st.session_state.profile_pic = user.get("profile_pic", "default")
                
                st.success(f"Welcome back, {user['full_name']}! 🤎")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Wrong username or password")

import streamlit as st
import os

import re  # Add this at the top of auth.py if not already there

def register():
    st.title("💌 Create New Account")
    st.markdown("### Connecting Hearts,Sharing Resources💌")

    st.subheader("Your Details")

    full_name = st.text_input("Full Name *", placeholder="e.g. Priya Sharma", key="reg_name")
    username = st.text_input("Choose Username *", placeholder="e.g. priya123", key="reg_username")
    password = st.text_input("Choose Password *", type="password", key="reg_password")
    phone = st.text_input("Phone Number *", placeholder="9876543210", key="reg_phone")
    email = st.text_input("Email ID", placeholder="example@gmail.com", key="reg_email")
    role = st.selectbox("I want to be a *", ["donor", "receiver"], key="reg_role")

    st.markdown("---")

    if st.button("🚀 Register Now", type="primary", use_container_width=True):
        # ====================== VALIDATION RULES ======================
        errors = []

        if not full_name.strip():
            errors.append("❌ Full Name is required")
        elif len(full_name.strip()) < 3:
            errors.append("❌ Full Name must be at least 3 characters")

        if not username.strip():
            errors.append("❌ Username is required")
        elif len(username.strip()) < 4:
            errors.append("❌ Username must be at least 4 characters")
        elif not username.strip().isalnum():
            errors.append("❌ Username can only contain letters and numbers")

        if not password.strip():
            errors.append("❌ Password is required")
        elif len(password.strip()) < 6:
            errors.append("❌ Password must be at least 6 characters")

        # Phone validation (only numbers, 10 digits)
        if not phone.strip():
            errors.append("❌ Phone Number is required")
        elif not phone.strip().isdigit():
            errors.append("❌ Phone Number should contain only digits")
        elif len(phone.strip()) != 10:
            errors.append("❌ Phone Number must be exactly 10 digits")

        # Email validation (optional but proper format)
        if email.strip():
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email.strip()):
                errors.append("❌ Please enter a valid email address")

        if errors:
            for error in errors:
                st.error(error)
            return

        # ====================== REGISTER USER ======================
        if add_user(username, password, full_name, role, phone, email):
            update_profile(username, full_name, phone, email, "")
            st.success("🎉 Account created successfully!")
            st.balloons()
            st.info("You can now go to the Login tab and sign in.")
        else:
            st.error("❌ Username already taken. Please choose another username.")