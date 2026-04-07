import streamlit as st
import pandas as pd
import os
import plotly.express as px
from db import (
    get_donations, get_requests, get_payments, get_users, get_feedback,
    update_request_status, update_user_role, deactivate_user, delete_donation, add_donation
)

def show_admin_panel():
    st.markdown("### Managing Kindness with ❤️ | Community Fund & Operations")

    donations = get_donations()
    requests = get_requests()
    payments = get_payments()
    users = get_users()
    feedback_df = get_feedback()

    # Top Metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1: st.metric("Total Donations", len(donations))
    with col2: st.metric("Total Requests", len(requests))
    with col3: 
        total_fund = int(pd.to_numeric(payments['amount'], errors='coerce').sum()) if not payments.empty else 0
        st.metric("💰 Community Fund", f"₹{total_fund}")
    with col4: 
        urgent = len(donations[donations['description'].str.contains("Urgent", case=False, na=False)]) if not donations.empty else 0
        st.metric("🚨 Urgent", urgent)
    with col5: st.metric("👥 Active Users", len(users))
    with col6: st.metric("💬 Feedback", len(feedback_df))

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Overview & Fund", 
        "📦 All Donations", 
        "📋 Requests & Payments", 
        "👥 Users", 
        "💬 Feedback", 
        "🌟 Community Donations",   # New Tab for Admin to upload photos
        "⚙️ Settings"
    ])

    # ====================== OVERVIEW & FUND ======================
    with tab1:
        st.subheader("Community Fund Overview")
        col_a, col_b, col_c = st.columns(3)
        with col_a: st.metric("Total Collected", f"₹{total_fund}")
        with col_b: 
            avg = int(payments['amount'].mean()) if not payments.empty else 0
            st.metric("Average Token", f"₹{avg}")
        with col_c: st.metric("Total Payments", len(payments))

        if not payments.empty:
            payments_copy = payments.copy()
            payments_copy['paid_at'] = pd.to_datetime(payments_copy['paid_at'], errors='coerce')
            daily = payments_copy.groupby(payments_copy['paid_at'].dt.strftime('%Y-%m-%d'))['amount'].sum().reset_index()
            daily.columns = ['Date', 'Amount']

            fig = px.bar(daily, x='Date', y='Amount', title="Daily Community Fund Collection", 
                        text='Amount', color_discrete_sequence=['#9B1C2C'])
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        # Donut Chart - Wine Red Theme
        if not donations.empty:
            st.subheader("Donations by Category")
            cat_count = donations['category'].value_counts().reset_index()
            cat_count.columns = ['Category', 'Count']
            
            fig_pie = px.pie(
                cat_count, 
                names='Category', 
                values='Count', 
                hole=0.45,
                title="Donations by Category",
                color_discrete_sequence=['#9B1C2C', '#C41E3A', '#E63946', '#FF6B6B', '#FF8C8C']
            )
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

    # ====================== ALL DONATIONS ======================
    with tab2:
        st.subheader("All Donations")
        if not donations.empty:
            search = st.text_input("🔍 Search Donations", placeholder="Title, Donor or Description")
            filtered = donations.copy()
            if search:
                filtered = filtered[filtered['title'].str.contains(search, case=False, na=False) |
                                  filtered['donor_username'].str.contains(search, case=False, na=False)]

            for _, row in filtered.iterrows():
                urgent_tag = " 🚨 URGENT" if "Urgent" in str(row.get('description', '')) else ""
                st.markdown(f"""
                <div style="background: white; padding: 18px; border-radius: 12px; 
                           box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #e0e0e0; 
                           margin-bottom: 16px;">
                    <h4>{row['title']} {urgent_tag}</h4>
                    <p><strong>By:</strong> {row.get('donor_username')} • {row.get('created_at','')[:10]}</p>
                    <p><strong>Category:</strong> {row.get('category','').upper()} | Token: ₹{row.get('token_amount',0)}</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button("🗑️ Delete", key=f"del_{row['id']}"):
                    delete_donation(row['id'])
                    st.rerun()
        else:
            st.info("No donations yet.")

    # ====================== REQUESTS & PAYMENTS ======================
    with tab3:
        st.subheader("Pending Requests")
        pending = requests[requests['status'] == 'pending'] if not requests.empty else pd.DataFrame()
        if not pending.empty:
            for _, req in pending.iterrows():
                st.markdown(f"""
                <div style="background: white; padding: 18px; border-radius: 12px; 
                           box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #e0e0e0; 
                           margin-bottom: 16px;">
                    <h4>{req.get('title')}</h4>
                    <p><strong>Requested by:</strong> {req.get('receiver_username')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✅ Approve", key=f"app_{req['id']}", use_container_width=True):
                        update_request_status(req['id'], 'approved')
                        st.success("Approved!")
                        st.rerun()
                with col_b:
                    if st.button("❌ Reject", key=f"rej_{req['id']}", use_container_width=True):
                        update_request_status(req['id'], 'rejected')
                        st.error("Rejected!")
                        st.rerun()
        else:
            st.success("All requests processed!")

        st.subheader("All Payments")
        if not payments.empty:
            payment_view = payments.merge(donations[['id', 'title']], left_on='donation_id', right_on='id', how='left')
            st.dataframe(payment_view[['receiver_username', 'amount', 'paid_at', 'title']], use_container_width=True)

    # ====================== USERS ======================
    with tab4:
        st.subheader("👥 User Management")
        if not users.empty:
            for _, u in users.iterrows():
                status = "✅ Active" if u.get('is_active', True) else "⛔ Inactive"
                st.markdown(f"""
                <div style="background: white; padding: 18px; border-radius: 12px; 
                           box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #e0e0e0; 
                           margin-bottom: 16px;">
                    <h4>{u['full_name']} (@{u['username']})</h4>
                    <p><strong>Role:</strong> {u['role'].upper()} | <strong>Status:</strong> {status}</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    new_role = st.selectbox("Change Role", ["admin", "donor", "receiver"], 
                                          index=["admin","donor","receiver"].index(u['role']), 
                                          key=f"role_{u['id']}")
                with col2:
                    if st.button("Update Role", key=f"upd_{u['id']}", use_container_width=True):
                        update_user_role(u['id'], new_role)
                        st.success("Role updated")
                        st.rerun()
                with col3:
                    if u.get('is_active', True):
                        if st.button("🚫 Deactivate", key=f"deact_{u['id']}", use_container_width=True):
                            deactivate_user(u['id'])
                            st.warning("User deactivated")
                            st.rerun()

    # ====================== FEEDBACK ======================
    with tab5:
        st.subheader("💬 All Feedbacks from Receivers")
        if feedback_df.empty:
            st.info("No feedback received yet.")
        else:
            for _, fb in feedback_df.iterrows():
                stars = "⭐" * int(fb.get('rating', 0)) if pd.notna(fb.get('rating')) else "No rating"
                st.markdown(f"""
                <div style="background: white; padding: 18px; border-radius: 12px; 
                           box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #e0e0e0; 
                           margin-bottom: 16px;">
                    <h4>{fb.get('title', 'Item')}</h4>
                    <p><strong>From:</strong> {fb.get('receiver_username')} &nbsp;&nbsp; <strong>Rating:</strong> {stars}</p>
                    <p style="font-style: italic;">"{fb.get('feedback_text', 'No comment')}</p>
                    <small>Submitted on: {fb.get('created_at', '')}</small>
                </div>
                """, unsafe_allow_html=True)

                if fb.get('proof_image_path') and os.path.exists(str(fb.get('proof_image_path'))):
                    st.image(fb['proof_image_path'], width=320, caption="Proof Photo")
                else:
                    st.caption("No proof photo uploaded")
                st.markdown("---")

    # ====================== 🌟 COMMUNITY DONATIONS TAB ======================
    with tab6:
        st.subheader("🌟 Community Donations")
        st.caption("Upload proof photos of donations made by Sahaya Team. These will be visible to all users.")

        st.markdown("### Add New Community Donation with Photo")

        col1, col2 = st.columns(2)
        with col1:
            comm_category = st.selectbox("Category *", 
                                       ["📚 Books", "🍛 Food", "💊 Medicine", "👕 Clothes", "🍽️ Utensils"], 
                                       key="comm_category")
            comm_title = st.text_input("Title / Item Name *", placeholder="e.g. 50 School Notebooks", key="comm_title")
            comm_desc = st.text_area("Description *", placeholder="These notebooks were donated by Sahaya team for underprivileged students...", key="comm_desc", height=100)
        
        with col2:
            comm_quantity = st.number_input("Quantity *", min_value=1, value=1, key="comm_qty")
            comm_image = st.file_uploader("Upload Proof Photo *", type=["jpg", "jpeg", "png"], key="comm_image")

        if st.button("🌟 Post Community Donation", type="primary", use_container_width=True):
            if not comm_title or not comm_desc or not comm_image:
                st.error("Please fill all fields and upload a photo")
            else:
                os.makedirs("uploads", exist_ok=True)
                image_path = f"uploads/community_{comm_image.name}"
                with open(image_path, "wb") as f:
                    f.write(comm_image.getbuffer())

                add_donation(
                    donor_username="Sahaya Community",
                    category=comm_category.split()[-1].lower(),
                    title=comm_title.strip(),
                    description=comm_desc.strip() + "\n\n🌟 Donated by Sahaya Community Team",
                    quantity=comm_quantity,
                    token_amount=0,
                    donor_note="Community Initiative",
                    image_path=image_path
                )
                st.success("🌟 Community donation with photo posted successfully!")
                st.balloons()
                st.rerun()

        st.markdown("---")
        st.subheader("All Community Donations")
        community_dons = donations[donations['donor_username'] == "Sahaya Community"]
        if community_dons.empty:
            st.info("No community donations yet.")
        else:
            for _, row in community_dons.iterrows():
                if row.get('image_path') and os.path.exists(str(row.get('image_path'))):
                    st.image(row['image_path'], width=300)
                st.write(f"**{row['title']}** — {row['quantity']} pcs")
                st.caption(row['description'])
                st.markdown("---")

    # ====================== SETTINGS ======================
    with tab7:
        st.info("**Community UPI ID:** totekrishnali0026-2@oksbi")
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()