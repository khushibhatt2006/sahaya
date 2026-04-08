import streamlit as st
import os
import pandas as pd
from db import get_donations

def show_community_gallery():
    st.title("🌟 Community Gallery")
    st.markdown("### Proof of Donations by Sahaya Team")
    st.caption("These are real proof photos of donations made by the Sahaya Team / Nagar Palika")

    df = get_donations()
    community_df = df[df['donor_username'] == "Sahaya Community"] if not df.empty else pd.DataFrame()

    if community_df.empty:
        st.info("No community donation proofs uploaded yet.")
    else:
        for _, row in community_df.iterrows():
            st.markdown("---")
            if row.get('image_path') and os.path.exists(str(row.get('image_path'))):
                st.image(row['image_path'], use_container_width=True)
            else:
                st.markdown("🌟 No photo available")
            
            st.subheader(row.get('title', 'Community Donation Proof'))
            st.write(row.get('description', 'No description provided'))
            st.caption(f"Posted on: {row.get('created_at', '')[:16]}")
            st.success("✅ Verified by Sahaya Community")
            # ====================== BACK TO HOME BUTTON (Strong Scroll to Top) ======================
    st.markdown("---")
    
    if st.button("⬅️ Back to Home", type="secondary", use_container_width=True):
        # Strong JavaScript to force scroll to the very top
        scroll_js = '''
        <script>
            window.scrollTo({
                top: 0,
                left: 0,
                behavior: 'instant'
            });
            // Also try scrolling the main container
            document.querySelector('.main').scrollTop = 0;
        </script>
        '''
        st.components.v1.html(scroll_js, height=0)
        st.rerun()

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
