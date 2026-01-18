import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Olist BI Dashboard", layout="wide", page_icon="🚀")

# --- CSS STYLES ---
st.markdown("""
    <style>
    /* Bigger buttons for sidebar */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
    /* Green progress bar for match score */
    .stProgress > div > div > div > div {
        background-color: #00cc66;
    }
    </style>
""", unsafe_allow_html=True)


# --- DATA LOADING ---
@st.cache_data
def load_data():
    data = {}
    # File paths
    files = {
        'cust': "data/customer_segments.csv",
        'affinity': "data/segment_affinity.csv",
        'history': "data/customer_order_history.csv",
        'prod_names': "data/olist_products_dataset.csv",
        'prod_seg': "data/product_segments.csv",
        'trans': "data/product_category_name_translation.csv"
    }

    for key, path in files.items():
        if os.path.exists(path):
            if key == 'prod_names':
                # Only load necessary columns
                data[key] = pd.read_csv(path)[['product_id', 'product_category_name']]
            else:
                data[key] = pd.read_csv(path)

    return data


db = load_data()

# App state initialization
if 'page' not in st.session_state:
    st.session_state.page = 'customers'

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("Olist Analytics")
    st.markdown("---")

    # Navigation buttons
    if st.button("📊 DASHBOARD", type="primary" if st.session_state.page == 'dashboard' else "secondary"):
        st.session_state.page = 'dashboard'
        st.rerun()

    if st.button("👥 CLIENTS DB", type="primary" if st.session_state.page == 'customers' else "secondary"):
        st.session_state.page = 'customers'
        st.rerun()

# ==========================================
# VIEW 1: DASHBOARD (Executive View)
# ==========================================
if st.session_state.page == 'dashboard':
    if 'cust' not in db:
        st.error("Missing customer data. Please run the notebook first.")
        st.stop()

    # Ładujemy dane
    df = db['cust'].copy()

    # --- FIX: SPÓJNOŚĆ DANYCH ---
    # Usuwamy wiersze, które nie mają przypisanego segmentu (NaN)
    # To naprawia różnicę między 93350 a 93342
    df = df.dropna(subset=['customer_segment'])

    st.header("📊 Executive Dashboard")
    st.markdown("### High-Level Metrics")

    # 1. KPI SECTION (BIG NUMBERS)
    # Teraz len(df) pokaże dokładnie 93342 (tyle samo co na wykresach)
    total_customers = len(df)
    total_revenue = df['total_spend'].sum()
    avg_ticket = df['total_spend'].mean()

    # Obliczamy % powracających
    returning_count = len(df[df['n_orders'] > 1])
    returning_pct = (returning_count / total_customers) * 100

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Customers", f"{total_customers:,}".replace(",", " "))
    k2.metric("Total Revenue", f"{total_revenue / 1000000:.2f}M BRL", delta="Lifetime")
    k3.metric("Avg. Order Value", f"{avg_ticket:.2f} BRL")
    k4.metric("Returning Clients", f"{returning_pct:.2f}%", help="Clients with more than 1 order")

    st.markdown("---")

    # 2. BUSINESS IMPACT (PARETO PRINCIPLE)
    st.markdown("### 📉 Business Impact: Quantity vs. Quality")
    st.caption("Comparison of Customer Count vs. Revenue Generation by Segment.")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("1. Customer Distribution")
        # Wykres ilościowy
        cust_counts = df['customer_segment'].value_counts()
        st.bar_chart(cust_counts, color="#29b5e8")  # Blue

    with c2:
        st.subheader("2. Revenue Share")
        # Wykres wartościowy
        rev_share = df.groupby('customer_segment')['total_spend'].sum().sort_values(ascending=False)
        st.bar_chart(rev_share, color="#00cc66")  # Green

    # Automatyczny insight
    top_segment_rev = rev_share.index[0]
    top_segment_pct = (rev_share.iloc[0] / total_revenue) * 100
    st.info(
        f"💡 **Insight:** The segment **'{top_segment_rev}'** generates **{top_segment_pct:.1f}%** of total revenue.")

    st.markdown("---")

    # 3. RFM ANALYSIS (SCATTER PLOT)
    st.markdown("### 🎯 RFM Segmentation Matrix (Recency vs. Monetary)")
    st.caption("Visualizing customer clusters based on mathematical behavior.")

    st.markdown("""
    * **X-Axis (Recency):** Days since last purchase (Lower is better - client is active).
    * **Y-Axis (Monetary):** Total amount spent (Higher is better - client is valuable).
    * **Color:** Identified Customer Segment.
    """)

    st.scatter_chart(
        df,
        x='recency_days',
        y='total_spend',
        color='customer_segment',
        size='n_orders',
        height=500,
        use_container_width=True
    )

    # Tabela statystyk pod wykresem
    with st.expander("Show detailed segment statistics"):
        stats = df.groupby('customer_segment').agg({
            'total_spend': 'mean',
            'recency_days': 'mean',
            'n_orders': 'mean'
        }).reset_index()

        stats.columns = ['Segment', 'Avg Spend (Monetary)', 'Avg Days Ago (Recency)', 'Avg Orders (Frequency)']
        # Formatowanie liczb w tabeli
        st.dataframe(stats.style.format("{:.2f}", subset=['Avg Spend (Monetary)', 'Avg Days Ago (Recency)',
                                                          'Avg Orders (Frequency)']), use_container_width=True)

# ==========================================
# VIEW 2: CUSTOMER 360 VIEW (Updated)
# ==========================================
elif st.session_state.page == 'customers':
    df = db['cust']
    st.header("👥 360° Customer View")

    # --- FILTERS ---
    with st.expander("🔍 FILTERING (Click to expand)", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            all_segs = df['customer_segment'].unique()
            sel_segs = st.multiselect("Segment:", all_segs, default=all_segs)
        with c2:
            min_o, max_o = st.slider("Number of orders:", int(df['n_orders'].min()), int(df['n_orders'].max()), (1, 10))
        with c3:
            min_s, max_s = st.slider("Total Spend (BRL):", 0, 5000, (0, 5000))

    # Filter logic
    mask = (df['customer_segment'].isin(sel_segs)) & (df['n_orders'].between(min_o, max_o)) & (
        df['total_spend'].between(min_s, max_s))
    df_display = df[mask]

    st.info(f"Found **{len(df_display)}** clients. 👇 Click a row in the table below to see details.")

    # --- CLIENT TABLE ---
    event = st.dataframe(
        df_display[['customer_unique_id', 'customer_segment', 'n_orders', 'total_spend', 'recency_days']],
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    # --- CLIENT DETAILS SECTION ---
    if len(event.selection['rows']) > 0:
        idx = event.selection['rows'][0]
        client = df_display.iloc[idx]
        cid = client['customer_unique_id']
        seg = client['customer_segment']

        st.markdown("---")
        st.subheader(f"👤 Client Profile: ...{cid[-8:]}")

        # Key Metrics (Segment is now a metric!)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Segment", seg)  # <-- ZMIANA: Segment jako metryka
        k2.metric("Total Spend", f"{client['total_spend']:.2f} BRL")
        k3.metric("Order Count", client['n_orders'])
        k4.metric("Last Purchase", f"{int(client['recency_days'])} days ago")

        # --- ORDER HISTORY ---
        with st.expander("📜 ORDER HISTORY (Click to expand)"):
            if 'history' in db:
                his = db['history']
                client_his = his[his['customer_unique_id'] == cid]

                if not client_his.empty:
                    st.dataframe(
                        client_his[['order_purchase_timestamp', 'product_category_name', 'price']],
                        column_config={
                            "order_purchase_timestamp": "Date",
                            "product_category_name": "Category",
                            "price": st.column_config.NumberColumn("Price", format="%.2f BRL")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.warning("No historical data for this ID.")
            else:
                st.error("History file missing.")

        # --- RECOMMENDATION ENGINE ---
        st.write(f"### 🎯 Purchase Prediction for segment: {seg}")


        # Helper function for translation
        def translate_categories(df_input, col_name='product_category_name'):
            if 'trans' in db:
                df_trans = db['trans']
                df_merged = df_input.merge(df_trans, left_on=col_name, right_on='product_category_name', how='left')
                df_merged['final_name'] = df_merged['product_category_name_english'].fillna(df_merged[col_name])
            else:
                df_merged = df_input.copy()
                df_merged['final_name'] = df_merged[col_name]
            return df_merged['final_name'].astype(str).str.replace('_', ' ').str.title()


        # 1. MAIN CATEGORIES (Green box)
        if 'affinity' in db:
            df_aff = db['affinity']
            top_items = df_aff[df_aff['customer_segment'] == seg].sort_values('match_score', ascending=False).head(5)

            if 'prod_names' in db:
                top_items = top_items.merge(db['prod_names'], on='product_id', how='left')

            if 'product_category_name' in top_items.columns:
                # Translate and format
                clean_names = translate_categories(top_items, 'product_category_name').unique()
                cat_list = ", ".join(clean_names[:3])
                st.success(f"**Main Interests:** {cat_list}")
            else:
                st.info("Category names unavailable.")

        st.markdown("---")

        # 2. SPECIFIC PRODUCTS (Table with lottery)
        st.write("#### 🛍️ Suggested Products:")
        st.caption("Drawing 5 suggestions from bestseller list for this segment.")

        if os.path.exists("data/product_affinity_v2.csv"):
            df_reco_v2 = pd.read_csv("data/product_affinity_v2.csv")
            segment_products = df_reco_v2[df_reco_v2['customer_segment'] == seg].copy()

            if not segment_products.empty:
                # Lottery mechanism
                top_10 = segment_products.head(10)
                final_recs = top_10.sample(n=min(5, len(top_10)))
                final_recs = final_recs.sort_values('match_score', ascending=False)

                # Formatting display names
                final_recs['display_name'] = final_recs['display_name'].astype(str).str.replace('_', ' ').str.title()

                st.dataframe(
                    final_recs[['display_name', 'product_id', 'match_score']],
                    column_config={
                        "display_name": "Category / Product",
                        "product_id": "Product ID",
                        "match_score": st.column_config.ProgressColumn(
                            "Purchase Probability",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100,
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )

                if st.button("🔄 Shuffle Suggestions"):
                    st.rerun()
            else:
                st.warning("No specific products for this segment.")
        else:
            st.warning("Missing file: product_affinity_v2.csv")