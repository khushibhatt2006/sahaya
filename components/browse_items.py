import streamlit as st
import os
import pandas as pd
from db import get_donations, get_requests, add_request, record_payment, add_feedback

def show_browse(username):
   
    st.markdown("### Find what you need from your community ❤️")

    st.markdown("""
    <style>
        .request-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            border: 1px solid #e0e0e0;
            margin-bottom: 16px;
        }
        .pay-box {
            background: #FFF8F0;
            border: 3px solid #FF6B9D;
            border-radius: 12px;
            padding: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🛍️ Browse Donations", "📋 My Requests", "Feedback🤝"])

    # ====================== BROWSE DONATIONS ======================
    with tab1:
        df = get_donations()
        if df.empty:
            st.info("No donations available right now.")
            return

        st.subheader("Filter Donations")
        col1, col2 = st.columns([3, 2])
        with col1:
            search = st.text_input("🔍 Search Title or Description", placeholder="e.g. Java Book", key="search")
        with col2:
            categories = ["All Categories", "books", "food", "medicine", "clothes", "utensils"]
            category = st.selectbox("Category", categories, index=0, key="category_filter")

        filtered = df.copy()
        if search:
            filtered = filtered[filtered['title'].str.contains(search, case=False, na=False) |
                              filtered.get('description', '').str.contains(search, case=False, na=False)]
        if category != "All Categories":
            filtered = filtered[filtered['category'] == category]

        if filtered.empty:
            st.warning("No donations found.")
        else:
            for _, row in filtered.iterrows():
                with st.container():
                    st.markdown('<div class="request-card">', unsafe_allow_html=True)
                    
                    col_img, col_info, col_action = st.columns([1.2, 4, 1.8])
                    
                    with col_img:
                        if row.get('image_path') and os.path.exists(str(row.get('image_path'))):
                            st.image(row['image_path'], width=120)
                        else:
                            st.markdown("📦")

                    with col_info:
                        emoji = {"books":"📚","food":"🍛","medicine":"💊","clothes":"👕","utensils":"🍽️"}.get(row.get('category',''), "📦")
                        st.subheader(f"{emoji} {row.get('title')}")
                        st.caption(f"By: {row.get('donor_username')} • {row.get('created_at','')[:10]}")
                        desc = row.get('description','')
                        st.write(desc[:180] + "..." if len(desc) > 180 else desc)
                        
                        if row.get('token_amount', 0) > 0:
                            st.info(f"💝 Token of Love: ₹{row['token_amount']}")
                        else:
                            st.success("✅ Free Item")

                    with col_action:
                        is_book = row.get('category') == 'books' and row.get('token_amount', 0) > 0
                        btn_text = "Request & Pay ❤️" if is_book else "Request for Free 🎁"

                        if st.button(btn_text, key=f"req_{row['id']}", use_container_width=True):
                            st.session_state.current_donation_id = row['id']
                            st.session_state.current_title = row.get('title')
                            st.session_state.current_amount = row.get('token_amount', 0)
                            st.session_state.is_free = not is_book
                            st.rerun()

                        if st.session_state.get('current_donation_id') == row['id']:
                            st.markdown('<div class="pay-box">', unsafe_allow_html=True)
                            st.markdown("### 💳 Confirm Payment")
                            st.write(f"**Item:** {st.session_state.current_title}")

                            if st.session_state.get('is_free'):
                                st.success("🎉 This item is Free!")
                                if st.button("✅ Confirm Request", type="primary", use_container_width=True):
                                    add_request(username, row['id'], row.get('category',''), row.get('title',''))
                                    st.success("✅ Request Confirmed!")
                                    st.balloons()
                                    st.session_state.just_completed = True
                                    st.session_state.completed_title = row.get('title')
                                    st.session_state.completed_donation_id = row['id']
                                    st.session_state.current_donation_id = None
                                    st.rerun()
                            else:
                                st.write(f"**Amount:** ₹{st.session_state.current_amount}")
                                st.markdown("**Scan QR Code**")
                                for ext in ["jpg", "jpeg", "png"]:
                                    if os.path.exists(f"qrcode.{ext}"):
                                        st.image(f"qrcode.{ext}", width=200)
                                        break
                                if st.button("✅ I have Paid - Confirm", type="primary", use_container_width=True):
                                    record_payment(row['id'], username, st.session_state.current_amount)
                                    add_request(username, row['id'], row.get('category',''), row.get('title',''))
                                    st.success("🎉 Payment Confirmed!")
                                    st.balloons()
                                    st.session_state.just_completed = True
                                    st.session_state.completed_title = row.get('title')
                                    st.session_state.completed_donation_id = row['id']
                                    st.session_state.current_donation_id = None
                                    st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)

    # ====================== MY REQUESTS ======================
    with tab2:
        st.subheader("📋 My Requests")
        reqs = get_requests()
        my_reqs = reqs[reqs['receiver_username'] == username] if not reqs.empty and 'receiver_username' in reqs.columns else pd.DataFrame()

        if my_reqs.empty:
            st.info("You have not requested any item yet.")
        else:
            for _, r in my_reqs.iterrows():
                status = r.get('status', 'pending')
                badge = "🟡 Pending" if status == 'pending' else "🟢 Approved" if status == 'approved' else "💰 Paid"
                st.markdown(f"""
                <div class="request-card">
                    <h4>{r.get('title')}</h4>
                    <p><strong>Status:</strong> {badge}</p>
                    <small>Requested: {r.get('created_at','')}</small>
                </div>
                """, unsafe_allow_html=True)

    # ====================== MY ACTIVITY (Feedback + Proof Photo) ======================
    with tab3:
        st.subheader("Feedback📋")

        if st.session_state.get('just_completed'):
            st.success(f"🎉 Request for **{st.session_state.completed_title}** completed successfully!")
            st.balloons()

            st.subheader("Rate this Donation & Upload Proof")

            stars = st.radio("How would you rate this item?", 
                           ["★", "★★", "★★★", "★★★★", "★★★★★"], 
                           index=None, horizontal=True, key="star_rating")
            rating = len(stars) if stars else 0

            feedback_text = st.text_area("Your Feedback (Optional)", 
                                       placeholder="The item was in excellent condition...", 
                                       key="fb_text", height=100)

            st.markdown("**📸 Upload Proof Photo (Optional)**")
            proof_file = st.file_uploader("Choose photo of the received item", 
                                        type=["jpg", "jpeg", "png"], 
                                        key="proof_uploader")

            proof_image_path = ""
            if proof_file:
                os.makedirs("proofs", exist_ok=True)
                proof_image_path = f"proofs/{username}_{proof_file.name}"
                with open(proof_image_path, "wb") as f:
                    f.write(proof_file.getbuffer())
                st.image(proof_file, width=280, caption="Proof Preview")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Submit Feedback & Proof", type="primary", use_container_width=True):
                    if rating == 0:
                        st.warning("Please select a rating")
                    else:
                        donation_id = st.session_state.get('completed_donation_id', 0)
                        add_feedback(
                            receiver_username=username,
                            donation_id=donation_id,
                            title=st.session_state.get('completed_title', 'Item'),
                            rating=rating,
                            feedback_text=feedback_text if feedback_text else "No additional comment",
                            proof_image_path=proof_image_path
                        )
                        st.success("Thank you! Feedback and proof uploaded successfully ❤️")
                        st.balloons()
                        for k in ['just_completed', 'completed_title', 'completed_donation_id']:
                            if k in st.session_state:
                                del st.session_state[k]
                        st.rerun()
           
            with col2:
                if st.button("Skip for now", use_container_width=True):
                    for k in ['just_completed', 'completed_title', 'completed_donation_id']:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.rerun()
        else:
            st.info("After completing a request and payment, your feedback & proof upload option will appear here.")
   
