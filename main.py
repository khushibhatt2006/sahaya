import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import init_db, create_default_data
from auth import login, register
from components.donation_form import show_donation_form
from components.browse_items import show_browse
from components.admin_panel import show_admin_panel
from components.community_gallery import show_community_gallery

st.set_page_config(
    page_title="Sahaya - Community of Kindness",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f8f4ed 0%, #f0e6d9 100%); }
    .main-header {
        font-family: 'Playfair Display', 'Georgia', serif !important;
        color: #3f2a1e !important;
        text-align: center !important;
        font-size: 4.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.05rem !important;
    }
    .tagline {
        font-family: 'Georgia', serif !important;
        color: #6b5c4a !important;
        text-align: center !important;
        font-size: 1.60rem !important;
        font-style: italic !important;
        margin-top: -30px !important;
    }
    header {visibility: hidden;}

.block-container {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

if "db_init" not in st.session_state:
    init_db()
    create_default_data()
    st.session_state.db_init = True

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ====================== SIDEBAR ======================
st.sidebar.markdown("### 🌟 **Sahaya**")
st.sidebar.markdown("**Community of Kindness**")

if not st.session_state.logged_in:
    st.sidebar.info("Please login or register to continue")
else:
    st.sidebar.success(f"Hi, {st.session_state.get('full_name', 'User')}! 👋")
    st.sidebar.write(f"**Role:** {st.session_state.get('role', '').capitalize()}")

    # Edit Profile Button (Restored)
    if st.sidebar.button("👤 Edit Profile", use_container_width=True):
        st.session_state.show_profile_edit = True
        st.rerun()

    if st.sidebar.button("Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Edit Profile Form
    if st.session_state.get('show_profile_edit'):
        st.sidebar.markdown("---")
        st.sidebar.subheader("👤 Edit Profile")
        with st.sidebar.form(key="edit_profile_form"):
            full_name = st.text_input("Full Name", value=st.session_state.get('full_name', ''))
            phone = st.text_input("Phone Number", value=st.session_state.get('phone', ''))
            email = st.text_input("Email ID", value=st.session_state.get('email', ''))
            address = st.text_area("Address", value=st.session_state.get('address', ''))
            submitted = st.form_submit_button("💾 Save Changes", type="primary")
            cancel = st.form_submit_button("Cancel")
            if submitted:
                from db import update_profile
                update_profile(st.session_state.username, full_name, phone, email, address)
                st.session_state.full_name = full_name
                st.session_state.phone = phone
                st.session_state.email = email
                st.session_state.address = address
                st.success("✅ Profile updated successfully!")
                st.session_state.show_profile_edit = False
                st.rerun()
            if cancel:
                st.session_state.show_profile_edit = False
                st.rerun()

# ====================== MAIN CONTENT ======================
if not st.session_state.logged_in:
    st.markdown('<p class="main-header">SAHAYA</p>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">From Giving to Living</p>', unsafe_allow_html=True)

    # Three Tabs on Home Page
    tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Register", "🌟 Community Proofs"])

    with tab1: 
        login()
    with tab2: 
        register()
    with tab3:
        show_community_gallery()   # Community photos here

else:
    # Role-based pages for logged-in users
    if st.session_state.role == "donor":
        st.markdown('<h1 class="section-title">🎁 Give with Love</h1>', unsafe_allow_html=True)
        show_donation_form(st.session_state.username)
        
    elif st.session_state.role == "receiver":
        st.markdown('<h1 class="section-title">🔎 Discover Kindness</h1>', unsafe_allow_html=True)
        show_browse(st.session_state.username)
        
    elif st.session_state.role == "admin":
        st.markdown('<h1 class="section-title">🛠️ Admin Dashboard</h1>', unsafe_allow_html=True)
        show_admin_panel()
