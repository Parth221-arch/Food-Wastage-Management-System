import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go
st.set_page_config(
    page_title="Food Wastage Management",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)
import plotly.io as pio
pio.templates["custom_dark"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E0", family="Inter, sans-serif"),
        xaxis=dict(gridcolor="#1C2333", zerolinecolor="#1C2333"),
        yaxis=dict(gridcolor="#1C2333", zerolinecolor="#1C2333"),
    )
)
pio.templates.default = "custom_dark"
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}
.stApp {
    background: #0F1117;
}
h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #F0F4FF !important;
}
[data-testid="stSidebar"] {
    background: #090D14 !important;
    border-right: 1px solid #1C2333 !important;
}
div[data-testid="metric-container"] {
    background: #161B27;
    border: 1px solid #1C2A3A;
    border-top: 3px solid #10B981;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);
}
div[data-testid="metric-container"] label {
    color: #8892B0 !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 11px !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    color: #10B981 !important;
    font-size: 28px !important;
}
div[data-testid="stVerticalBlock"] > div[style*="border"] {
    background: #161B27 !important;
    border: 1px solid #1C2A3A !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2) !important;
    padding: 20px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(16,185,129,0.4) !important;
    opacity: 0.9 !important;
}
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    border: 1px solid #1C2A3A !important;
    overflow: hidden !important;
}
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: none !important;
}
hr {
    border-color: #1C2333 !important;
}
</style>
""", unsafe_allow_html=True)
DB_PASSWORD = ""
def get_conn():
    if "mysql" in st.secrets:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            ssl_disabled=False,
            ssl_verify_cert=False,
            ssl_verify_identity=False
        )
    else:
        return mysql.connector.connect(
            host="localhost", user="root",
            password=DB_PASSWORD, database="food_wastage"
        )
def run_query(sql):
    try:
        conn = get_conn()
        df = pd.read_sql(sql, conn)
        conn.close()
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)
CHART_COLORS = ["#10B981", "#06B6D4", "#8B5CF6", "#F59E0B", "#F43F5E", "#3B82F6"]
PIE_COLORS   = ["#10B981", "#06B6D4", "#8B5CF6", "#F59E0B", "#F43F5E", "#3B82F6"]
def hero(title, subtitle):
    st.title(title)
    st.markdown(f"**{subtitle}**")
    st.divider()
def page_home():
    hero("🏠 Welcome to FoodShare", "Connecting surplus food to those in need")
    st.markdown("""
    ### About the System
    FoodShare is a comprehensive food wastage management system designed to seamlessly connect food providers with receivers.
    **How it works:**
    - **Providers** list available surplus food
    - **Receivers** browse listings and make claims
    - **System** tracks claims, completion rates, and provides valuable insights
    Use the navigation menu on the left to explore the system!
    """)
    with st.container(border=True):
        st.info("💡 **Tip:** Check the **Insights** tab for auto-generated takeaways from the data.")
def page_receivers():
    hero("🤝 Receivers Directory", "Organizations receiving food donations across the network")
    df_rec, err = run_query("SELECT Receiver_ID, Name, Type, City FROM receivers")
    if err:
        st.error(err)
    else:
        col1, col2 = st.columns(2)
        with col1:
            cities = ["All"] + sorted(df_rec["City"].dropna().unique().tolist())
            city_s = st.selectbox("📍 Filter by City", cities, key="rec_city")
        with col2:
            types = ["All"] + sorted(df_rec["Type"].dropna().unique().tolist())
            type_s = st.selectbox("🤝 Filter by Type", types, key="rec_type")
        df_f = df_rec.copy()
        if city_s != "All": df_f = df_f[df_f["City"] == city_s]
        if type_s != "All": df_f = df_f[df_f["Type"] == type_s]
        st.success(f"📋 Receivers Found: {len(df_f)}")
        col_a, col_b = st.columns(2)
        for idx, (_, row) in enumerate(df_f.head(30).iterrows()):
            name = str(row["Name"])
            target_col = col_a if idx % 2 == 0 else col_b
            with target_col:
                with st.container(border=True):
                    st.markdown(f"### {name}")
                    st.markdown(f"📍 **{row['City']}**")
                    st.info(f"Type: {row['Type']}")
def page_claims():
    hero("📦 Claims Tracking", "Monitor the status and details of food donation claims")
    df, err = run_query("""
        SELECT c.Claim_ID, f.Food_Name, r.Name AS Receiver, c.Status, DATE(c.Timestamp) AS Date
        FROM claims c
        JOIN foodlistings f ON c.Food_ID = f.Food_ID
        JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
        ORDER BY c.Timestamp DESC
    """)
    if err:
        st.error(err)
    else:
        st.metric("Total Claims", len(df))
        st.dataframe(df, use_container_width=True, hide_index=True)
def page_insights():
    hero("💡 Key Insights", "Auto-generated takeaways from your food wastage data")
    df_status, _  = run_query("SELECT Status, COUNT(*) AS Total FROM claims GROUP BY Status ORDER BY Total DESC")
    df_ptype, _   = run_query("SELECT Provider_Type, COUNT(*) AS Total FROM foodlistings GROUP BY Provider_Type ORDER BY Total DESC LIMIT 1")
    df_totcl, _   = run_query("SELECT COUNT(*) AS v FROM claims")
    df_comp, _    = run_query("SELECT COUNT(*) AS v FROM claims WHERE Status='Completed'")
    total = int(df_totcl["v"][0]) if not df_totcl.empty else 1
    comp = int(df_comp["v"][0]) if not df_comp.empty else 0
    comp_pct = round(comp / total * 100, 1)
    top_ptype = df_ptype["Provider_Type"].values[0] if not df_ptype.empty else "N/A"
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### ✅ Completion Rate")
            st.markdown(f"**{comp_pct}%** of all claims were successfully completed.")
    with col2:
        with st.container(border=True):
            st.markdown("### 🏪 Top Provider")
            st.markdown(f"**{top_ptype}s** contribute the most food listings.")
    df_meal, _ = run_query("""SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total FROM foodlistings f
                              JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY f.Meal_Type ORDER BY Total DESC LIMIT 1""")
    top_meal = df_meal["Meal_Type"].values[0] if not df_meal.empty else "N/A"
    with st.container(border=True):
        st.markdown("### 🍽️ Most Claimed Meal")
        st.markdown(f"**{top_meal}** is the most frequently claimed meal type across the network.")
def page_dashboard():
    hero("🥗 Food Wastage Management System", "Real-time overview of food donations, claims, and distribution across the network")
    kpi_sql = {
        "providers": "SELECT COUNT(*) AS v FROM providers",
        "receivers": "SELECT COUNT(*) AS v FROM receivers",
        "food":      "SELECT SUM(Quantity) AS v FROM foodlistings",
        "claims":    "SELECT COUNT(*) AS v FROM claims",
        "completed": "SELECT COUNT(*) AS v FROM claims WHERE Status='Completed'",
        "cities":    "SELECT COUNT(DISTINCT City) AS v FROM providers",
    }
    kpi_vals = {}
    for key, sql in kpi_sql.items():
        df, err = run_query(sql)
        kpi_vals[key] = int(df["v"][0]) if (not df.empty and df["v"][0] is not None) else 0
    cols = st.columns(6)
    cards = [
        ("🏪 Providers", kpi_vals['providers']),
        ("🤝 Receivers", kpi_vals['receivers']),
        ("🍱 Food Units", kpi_vals['food']),
        ("📋 Claims", kpi_vals['claims']),
        ("✅ Completed", kpi_vals['completed']),
        ("🌆 Cities", kpi_vals['cities']),
    ]
    for col, (label, val) in zip(cols, cards):
        col.metric(label, f"{val:,}")
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("Claims by Status")
            df, err = run_query("SELECT Status, COUNT(*) AS Total FROM claims GROUP BY Status")
            if err:
                st.error(err)
            else:
                fig = px.pie(df, names="Status", values="Total", hole=0.6, color="Status",
                             color_discrete_map={"Completed":"#10B981","Pending":"#F59E0B","Cancelled":"#F43F5E"})
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")
    with col2:
        with st.container(border=True):
            st.subheader("Food by Provider Type")
            df, err = run_query("SELECT Provider_Type, COUNT(*) AS Total FROM foodlistings GROUP BY Provider_Type ORDER BY Total DESC")
            if err:
                st.error(err)
            else:
                fig = px.bar(df, x="Total", y="Provider_Type", orientation="h",
                             color="Provider_Type", color_discrete_sequence=CHART_COLORS)
                fig.update_layout(showlegend=False)
                fig.update_layout(yaxis=dict(categoryorder="total ascending"))
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")
    col3, col4 = st.columns(2)
    with col3:
        with st.container(border=True):
            st.subheader("Top 5 Cities by Listings")
            df, err = run_query("SELECT Food_Location AS City, COUNT(*) AS Listings FROM foodlistings GROUP BY Food_Location ORDER BY Listings DESC LIMIT 5")
            if err:
                st.error(err)
            else:
                fig = px.bar(df, x="Listings", y="City", orientation="h",
                             color="Listings", color_continuous_scale=["#064E3B","#10B981","#06B6D4"])
                fig.update_layout(coloraxis_showscale=False)
                fig.update_layout(yaxis=dict(categoryorder="total ascending"))
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")
    with col4:
        with st.container(border=True):
            st.subheader("Meal Type Distribution")
            df, err = run_query("SELECT Meal_Type, COUNT(*) AS Total FROM foodlistings GROUP BY Meal_Type")
            if err:
                st.error(err)
            else:
                fig = px.pie(df, names="Meal_Type", values="Total", hole=0.55, color_discrete_sequence=PIE_COLORS)
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")
def page_sql_queries():
    hero("📋 SQL Queries", "All 15 analysis queries with live results from MySQL — click to expand and explore")
    queries = [
        ("Q1 — Providers per City",
         "SELECT City, COUNT(*) AS Total_Providers FROM providers GROUP BY City ORDER BY Total_Providers DESC",
         "Number of food providers in each city"),
        ("Q2 — Provider Type with Most Listings",
         "SELECT Provider_Type, COUNT(*) AS Total_Listings FROM foodlistings GROUP BY Provider_Type ORDER BY Total_Listings DESC",
         "Which provider type contributes the most food listings"),
        ("Q3 — Top Receivers by Claims",
         """SELECT r.Name, r.Type, r.City, COUNT(c.Claim_ID) AS Total_Claims
            FROM receivers r JOIN claims c ON r.Receiver_ID = c.Receiver_ID
            GROUP BY r.Receiver_ID, r.Name, r.Type, r.City
            ORDER BY Total_Claims DESC LIMIT 10""",
         "Top 10 receivers who claimed the most food"),
        ("Q4 — Total Food Quantity",
         "SELECT SUM(Quantity) AS Total_Available, AVG(Quantity) AS Avg_Per_Listing, MAX(Quantity) AS Max_Quantity FROM foodlistings",
         "Overall food quantity stats across all listings"),
        ("Q5 — Cities with Most Listings",
         "SELECT Food_Location AS City, COUNT(*) AS Total_Listings FROM foodlistings GROUP BY Food_Location ORDER BY Total_Listings DESC LIMIT 10",
         "Top 10 cities with the highest food listings"),
        ("Q6 — Most Common Food Types",
         "SELECT Food_Type, COUNT(*) AS Total FROM foodlistings GROUP BY Food_Type ORDER BY Total DESC",
         "Distribution of Vegetarian, Non-Vegetarian, Vegan listings"),
        ("Q7 — Most Claimed Food Items",
         """SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims
            FROM foodlistings f JOIN claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Food_ID, f.Food_Name ORDER BY Total_Claims DESC LIMIT 10""",
         "Top 10 most claimed food items"),
        ("Q8 — Providers with Most Completed Claims",
         """SELECT p.Name, p.City, COUNT(c.Claim_ID) AS Successful_Claims
            FROM providers p
            JOIN foodlistings f ON p.Provider_ID = f.Provider_ID
            JOIN claims c ON f.Food_ID = c.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY p.Provider_ID, p.Name, p.City
            ORDER BY Successful_Claims DESC LIMIT 10""",
         "Top 10 providers with most completed claims"),
        ("Q9 — Claim Status Percentage",
         """SELECT Status, COUNT(*) AS Total,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
            FROM claims GROUP BY Status""",
         "Breakdown of Completed vs Pending vs Cancelled"),
        ("Q10 — Avg Quantity per Receiver",
         """SELECT r.Name, ROUND(AVG(f.Quantity), 2) AS Avg_Quantity
            FROM receivers r
            JOIN claims c ON r.Receiver_ID = c.Receiver_ID
            JOIN foodlistings f ON c.Food_ID = f.Food_ID
            GROUP BY r.Receiver_ID, r.Name
            ORDER BY Avg_Quantity DESC LIMIT 10""",
         "Average food quantity claimed per receiver"),
        ("Q11 — Most Claimed Meal Type",
         """SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
            FROM foodlistings f JOIN claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Meal_Type ORDER BY Total_Claims DESC""",
         "Which meal type — Breakfast, Lunch, Dinner, or Snacks — is claimed most"),
        ("Q12 — Total Food Donated per Provider",
         """SELECT p.Name, p.City, SUM(f.Quantity) AS Total_Donated
            FROM providers p JOIN foodlistings f ON p.Provider_ID = f.Provider_ID
            GROUP BY p.Provider_ID, p.Name, p.City
            ORDER BY Total_Donated DESC LIMIT 10""",
         "Total quantity donated by each provider"),
        ("Q13 — City with Most Claims",
         """SELECT p.City, COUNT(c.Claim_ID) AS Total_Claims
            FROM providers p
            JOIN foodlistings f ON p.Provider_ID = f.Provider_ID
            JOIN claims c ON f.Food_ID = c.Food_ID
            GROUP BY p.City ORDER BY Total_Claims DESC LIMIT 10""",
         "Which city has the highest food demand"),
        ("Q14 — Provider Contact Info",
         "SELECT Name, Type, City, Contact FROM providers ORDER BY City LIMIT 20",
         "Contact information of food providers"),
        ("Q15 — Food Expiring in 30 Days",
         """SELECT Food_Name, Quantity, Expiry_Date, Food_Location, Food_Type
            FROM foodlistings
            WHERE Expiry_Date >= CURDATE()
            AND Expiry_Date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
            ORDER BY Expiry_Date ASC LIMIT 15""",
         "Food items expiring within the next 30 days"),
    ]
    for title, sql, desc in queries:
        with st.expander(f"🔹 {title}"):
            st.caption(f"📌 {desc}")
            df, err = run_query(sql)
            if err:
                st.error(f"SQL Error: {err}")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.caption(f"✦ {len(df)} row(s) returned")
def page_filter_explore():
    hero("🔍 Filter & Explore", "Filter food listings by city, food type, meal type, and provider type")
    df_all, err = run_query("SELECT Food_ID, Food_Name, Quantity, Expiry_Date, Provider_Type, Food_Location, Food_Type, Meal_Type FROM foodlistings")
    if err:
        st.error(err)
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            cities = ["All"] + sorted(df_all["Food_Location"].dropna().unique().tolist())
            city_f = st.selectbox("📍 City", cities)
        with col2:
            ftypes = ["All"] + sorted(df_all["Food_Type"].dropna().unique().tolist())
            ftype_f = st.selectbox("🥦 Food Type", ftypes)
        with col3:
            mtypes = ["All"] + sorted(df_all["Meal_Type"].dropna().unique().tolist())
            mtype_f = st.selectbox("🍽️ Meal Type", mtypes)
        with col4:
            ptypes = ["All"] + sorted(df_all["Provider_Type"].dropna().unique().tolist())
            ptype_f = st.selectbox("🏪 Provider Type", ptypes)
        df_f = df_all.copy()
        if city_f  != "All": df_f = df_f[df_f["Food_Location"] == city_f]
        if ftype_f != "All": df_f = df_f[df_f["Food_Type"]     == ftype_f]
        if mtype_f != "All": df_f = df_f[df_f["Meal_Type"]     == mtype_f]
        if ptype_f != "All": df_f = df_f[df_f["Provider_Type"] == ptype_f]
        st.markdown("<br>", unsafe_allow_html=True)
        avg_qty = round(df_f["Quantity"].mean(), 1) if not df_f.empty else 0
        total_qty = int(df_f["Quantity"].sum()) if not df_f.empty else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("📊 Results", len(df_f))
        c2.metric("📦 Total Qty", f"{total_qty:,}")
        c3.metric("📈 Avg Qty", avg_qty)
        st.dataframe(df_f, use_container_width=True, hide_index=True)
def page_provider_contacts():
    hero("📞 Provider Contacts", "Find and contact food providers in any city — browse the directory with smart filters")
    df_prov, err = run_query("SELECT Provider_ID, Name, Type, Address, City, Contact FROM providers")
    if err:
        st.error(err)
    else:
        col1, col2 = st.columns(2)
        with col1:
            cities = ["All"] + sorted(df_prov["City"].dropna().unique().tolist())
            city_s = st.selectbox("📍 Filter by City", cities)
        with col2:
            types = ["All"] + sorted(df_prov["Type"].dropna().unique().tolist())
            type_s = st.selectbox("🏪 Filter by Type", types)
        df_f = df_prov.copy()
        if city_s != "All": df_f = df_f[df_f["City"] == city_s]
        if type_s != "All": df_f = df_f[df_f["Type"] == type_s]
        st.success(f"📋 Providers Found: {len(df_f)}")
        col_a, col_b = st.columns(2)
        for idx, (_, row) in enumerate(df_f.head(30).iterrows()):
            addr = str(row["Address"])
            addr = addr[:55] + "..." if len(addr) > 55 else addr
            name = str(row["Name"])
            target_col = col_a if idx % 2 == 0 else col_b
            with target_col:
                with st.container(border=True):
                    st.markdown(f"### {name}")
                    st.markdown(f"📍 **{row['City']}**")
                    st.markdown(f"📞 `{row['Contact']}`")
                    st.caption(f"{addr}")
                    st.info(f"Type: {row['Type']}")
def page_crud_operations():
    hero("✏️ CRUD Operations", "Add, update, and delete food listings directly in the MySQL database")
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Listing", "✏️ Update Listing", "🗑️ Delete Listing", "👁️ View All"])
    with tab1:
        st.subheader("Add New Food Listing")
        c1, c2 = st.columns(2)
        with c1:
            food_name     = st.text_input("Food Name")
            quantity      = st.number_input("Quantity", min_value=1, value=10)
            expiry_date   = st.date_input("Expiry Date")
            provider_id   = st.number_input("Provider ID", min_value=1, value=1)
        with c2:
            provider_type = st.selectbox("Provider Type", ["Restaurant","Grocery Store","Supermarket","Catering Service"])
            food_location = st.text_input("City / Location")
            food_type     = st.selectbox("Food Type", ["Vegetarian","Non-Vegetarian","Vegan"])
            meal_type     = st.selectbox("Meal Type", ["Breakfast","Lunch","Dinner","Snacks"])
        if st.button("➕ Add Food Listing"):
            if food_name.strip() and food_location.strip():
                try:
                    conn = get_conn()
                    cur  = conn.cursor()
                    cur.execute("""
                        INSERT INTO foodlistings
                        (Food_Name, Quantity, Expiry_Date, Provider_ID,
                         Provider_Type, Food_Location, Food_Type, Meal_Type)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (food_name, int(quantity), str(expiry_date),
                          int(provider_id), provider_type, food_location, food_type, meal_type))
                    conn.commit()
                    cur.close(); conn.close()
                    st.success(f"✅ '{food_name}' added successfully!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.warning("⚠️ Please fill in Food Name and Location.")
    with tab2:
        st.subheader("Update Food Listing")
        food_id_upd = st.number_input("Enter Food ID to Update", min_value=1, value=1)
        df_check, _ = run_query(f"SELECT * FROM foodlistings WHERE Food_ID = {food_id_upd}")
        if not df_check.empty:
            st.dataframe(df_check, use_container_width=True, hide_index=True)
            new_qty  = st.number_input("New Quantity", min_value=1, value=int(df_check["Quantity"].values[0]))
            new_name = st.text_input("New Food Name", value=str(df_check["Food_Name"].values[0]))
            if st.button("✏️ Update"):
                try:
                    conn = get_conn()
                    cur  = conn.cursor()
                    cur.execute("UPDATE foodlistings SET Quantity=%s, Food_Name=%s WHERE Food_ID=%s",
                                (new_qty, new_name, food_id_upd))
                    conn.commit()
                    cur.close(); conn.close()
                    st.success(f"✅ Food ID {food_id_upd} updated!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.info("No listing found with that Food ID.")
    with tab3:
        st.subheader("Delete Food Listing")
        food_id_del = st.number_input("Enter Food ID to Delete", min_value=1, value=1)
        df_del, _   = run_query(f"SELECT * FROM foodlistings WHERE Food_ID = {food_id_del}")
        if not df_del.empty:
            st.dataframe(df_del, use_container_width=True, hide_index=True)
            st.warning("⚠️ This will also delete all claims linked to this food item.")
            if st.button("🗑️ Confirm Delete"):
                try:
                    conn = get_conn()
                    cur  = conn.cursor()
                    cur.execute("DELETE FROM claims WHERE Food_ID=%s", (food_id_del,))
                    cur.execute("DELETE FROM foodlistings WHERE Food_ID=%s", (food_id_del,))
                    conn.commit()
                    cur.close(); conn.close()
                    st.success(f"✅ Food ID {food_id_del} deleted!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.info("No listing found with that Food ID.")
    with tab4:
        st.subheader("All Food Listings")
        df_view, err = run_query("SELECT * FROM foodlistings ORDER BY Food_ID DESC LIMIT 50")
        if err:
            st.error(err)
        else:
            st.info(f"📋 Showing: {len(df_view)} latest records")
            st.dataframe(df_view, use_container_width=True, hide_index=True)
def page_eda_charts():
    hero("📊 EDA & Charts", "Exploratory data analysis with interactive visualizations — discover patterns and insights")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("Food Type vs Meal Type")
            df, err = run_query("SELECT Food_Type, Meal_Type, COUNT(*) AS Total FROM foodlistings GROUP BY Food_Type, Meal_Type")
            if err:
                st.error(err)
            else:
                df_pivot = df.pivot(index="Food_Type", columns="Meal_Type", values="Total").fillna(0)
                fig = px.imshow(df_pivot, color_continuous_scale=["#f0f2f6","#064E3B","#10B981","#06B6D4"], text_auto=True)
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")
    with col2:
        with st.container(border=True):
            st.subheader("Claims Over Time")
            df, err = run_query("SELECT DATE(Timestamp) AS Date, COUNT(*) AS Claims FROM claims GROUP BY DATE(Timestamp) ORDER BY Date")
            if err:
                st.error(err)
            else:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df["Date"], y=df["Claims"], mode='lines',
                    line=dict(color="#10B981", width=2.5, shape='spline'),
                    fill='tozeroy', fillcolor='rgba(16,185,129,0.08)'
                ))
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")
    col3, col4 = st.columns(2)
    with col3:
        with st.container(border=True):
            st.subheader("Quantity Distribution")
            df, err = run_query("SELECT Quantity FROM foodlistings")
            if err:
                st.error(err)
            else:
                fig = px.histogram(df, x="Quantity", nbins=30, color_discrete_sequence=["#06B6D4"])
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")
    with col4:
        with st.container(border=True):
            st.subheader("Receiver Type Distribution")
            df, err = run_query("SELECT Type, COUNT(*) AS Total FROM receivers GROUP BY Type ORDER BY Total DESC")
            if err:
                st.error(err)
            else:
                fig = px.bar(df, x="Type", y="Total", color="Type",
                             color_discrete_sequence=["#8B5CF6","#F59E0B","#10B981","#F43F5E","#06B6D4"])
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")
    with st.container(border=True):
        st.subheader("Top 10 Providers by Total Food Donated")
        df, err = run_query("""
            SELECT p.Name, SUM(f.Quantity) AS Total_Donated
            FROM providers p JOIN foodlistings f ON p.Provider_ID = f.Provider_ID
            GROUP BY p.Provider_ID, p.Name ORDER BY Total_Donated DESC LIMIT 10
        """)
        if err:
            st.error(err)
        else:
            fig = px.bar(df, x="Total_Donated", y="Name", orientation="h",
                         color="Total_Donated", color_continuous_scale=["#064E3B","#10B981","#06B6D4","#8B5CF6"])
            fig.update_layout(coloraxis_showscale=False, height=400)
            fig.update_layout(yaxis=dict(categoryorder="total ascending"))
            st.plotly_chart(fig, use_container_width=True, theme="streamlit")
    with st.container(border=True):
        st.subheader("Food Type Distribution by City")
        df, err = run_query("""
            SELECT Food_Location AS City, Food_Type, COUNT(*) AS Total
            FROM foodlistings GROUP BY Food_Location, Food_Type ORDER BY Total DESC LIMIT 40
        """)
        if err:
            st.error(err)
        else:
            fig = px.bar(df, x="City", y="Total", color="Food_Type",
                         color_discrete_map={"Vegetarian":"#10B981","Non-Vegetarian":"#F59E0B","Vegan":"#8B5CF6"},
                         barmode="group")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True, theme="streamlit")
def page_sustainability_impact():
    hero("🌍 Sustainability Impact", "See the real-world environmental impact of your food rescue efforts")
    df_saved, err = run_query("""
        SELECT SUM(f.Quantity) AS Total_Saved 
        FROM claims c JOIN foodlistings f ON c.Food_ID = f.Food_ID 
        WHERE c.Status = 'Completed'
    """)
    if err:
        st.error(err)
        return
    total_saved = int(df_saved["Total_Saved"][0]) if not df_saved.empty and df_saved["Total_Saved"][0] else 0
    co2_saved = total_saved * 2.5  
    water_saved = total_saved * 1000 
    col1, col2, col3 = st.columns(3)
    col1.metric("🍱 Total Food Rescued", f"{total_saved:,} kg")
    col2.metric("☁️ CO₂ Emissions Prevented", f"{co2_saved:,.1f} kg")
    col3.metric("💧 Water Conserved", f"{water_saved:,} Liters")
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader("🏆 Top Donors Wall of Fame")
        st.caption("Providers making the biggest environmental impact")
        df_top, err = run_query("""
            SELECT p.Name, p.City, SUM(f.Quantity) AS Impact_Score
            FROM providers p 
            JOIN foodlistings f ON p.Provider_ID = f.Provider_ID
            JOIN claims c ON f.Food_ID = c.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY p.Provider_ID, p.Name, p.City
            ORDER BY Impact_Score DESC LIMIT 5
        """)
        if err:
            st.error(err)
        else:
            medals = ["🥇", "🥈", "🥉", "🏅", "🏅"]
            for idx, row in df_top.iterrows():
                medal = medals[idx] if idx < len(medals) else "🏅"
                st.markdown(f"**{medal} {row['Name']}** ({row['City']}) — **{row['Impact_Score']} kg** rescued")
def page_ai_predictions():
    hero("🤖 AI Demand Forecasting & Risk", "Predictive analytics for future food demand and spoilage risk")
    st.info("Using historical claim data to forecast network demand.")
    with st.container(border=True):
        st.subheader("📈 30-Day Demand Forecast")
        df_trend, err = run_query("""
            SELECT DATE(Timestamp) AS Date, COUNT(*) AS Claims 
            FROM claims 
            GROUP BY DATE(Timestamp) ORDER BY Date
        """)
        if not err and not df_trend.empty:
            df_trend['SMA'] = df_trend['Claims'].rolling(window=3, min_periods=1).mean()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_trend['Date'], y=df_trend['Claims'], mode='lines+markers', name='Actual Claims', line=dict(color='#8B5CF6')))
            fig.add_trace(go.Scatter(x=df_trend['Date'], y=df_trend['SMA'], mode='lines', name='AI Trend (SMA)', line=dict(color='#10B981', dash='dash')))
            st.plotly_chart(fig, use_container_width=True, theme="streamlit")
        else:
            st.warning("Not enough data to generate forecast.")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("⚠️ High-Risk Spoilage Cities")
            st.caption("Cities with high food listings but low claim completion rates")
            df_risk, err = run_query("""
                SELECT f.Food_Location AS City, 
                       COUNT(DISTINCT f.Food_ID) AS Total_Listings,
                       SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) AS Completed_Claims
                FROM foodlistings f
                LEFT JOIN claims c ON f.Food_ID = c.Food_ID
                GROUP BY f.Food_Location
                HAVING Total_Listings > 0
                ORDER BY (Completed_Claims / Total_Listings) ASC, Total_Listings DESC
                LIMIT 5
            """)
            if not err and not df_risk.empty:
                for idx, row in df_risk.iterrows():
                    rate = (row['Completed_Claims'] / row['Total_Listings']) * 100
                    st.error(f"📍 **{row['City']}** — Only {rate:.1f}% claim rate")
            else:
                st.success("No high-risk cities detected!")
    with col2:
        with st.container(border=True):
            st.subheader("🔥 High Demand Zones")
            st.caption("Cities where food claims happen the fastest")
            df_hot, err = run_query("""
                SELECT p.City, COUNT(c.Claim_ID) AS Total_Claims
                FROM providers p
                JOIN foodlistings f ON p.Provider_ID = f.Provider_ID
                JOIN claims c ON f.Food_ID = c.Food_ID
                GROUP BY p.City
                ORDER BY Total_Claims DESC LIMIT 5
            """)
            if not err and not df_hot.empty:
                for idx, row in df_hot.iterrows():
                    st.success(f"🚀 **{row['City']}** — {row['Total_Claims']} claims")
def page_reports():
    hero("📄 Executive Reports", "Generate and download professional CSV reports")
    st.markdown("Download full system snapshots for external auditing and reporting.")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("📦 All Food Claims")
            st.caption("Export the complete history of food claims.")
            df_claims, _ = run_query("SELECT * FROM claims ORDER BY Timestamp DESC")
            if not df_claims.empty:
                csv = df_claims.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Download Claims CSV", data=csv, file_name="foodshare_claims.csv", mime="text/csv")
    with col2:
        with st.container(border=True):
            st.subheader("🏪 Provider Directory")
            st.caption("Export the contact information for all registered providers.")
            df_prov, _ = run_query("SELECT * FROM providers ORDER BY Name ASC")
            if not df_prov.empty:
                csv = df_prov.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Download Providers CSV", data=csv, file_name="foodshare_providers.csv", mime="text/csv")
st.sidebar.markdown("### 🍱 FoodShare")
st.sidebar.caption("Waste Management System")
st.sidebar.divider()
pg_home = st.Page(page_home, title="Home", icon="🏠")
pg_dashboard = st.Page(page_dashboard, title="Dashboard", icon="📊")
pg_filter = st.Page(page_filter_explore, title="Browse Food", icon="🔍")
pg_crud = st.Page(page_crud_operations, title="Food Listings", icon="🍱")
pg_claims = st.Page(page_claims, title="Claims", icon="📦")
pg_contacts = st.Page(page_provider_contacts, title="Providers", icon="🏢")
pg_receivers = st.Page(page_receivers, title="Receivers", icon="🤝")
pg_insights = st.Page(page_insights, title="Insights", icon="💡")
pg_eda = st.Page(page_eda_charts, title="Analytics", icon="📈")
pg_sql = st.Page(page_sql_queries, title="SQL Insights", icon="🧠")
pg_sustainability = st.Page(page_sustainability_impact, title="Sustainability", icon="🌍")
pg_ai = st.Page(page_ai_predictions, title="AI Forecasting", icon="🤖")
pg_reports = st.Page(page_reports, title="Reports Export", icon="📄")
pg = st.navigation({
    "OVERVIEW": [pg_home, pg_dashboard],
    "FOOD": [pg_filter, pg_crud],
    "OPERATIONS": [pg_claims, pg_contacts, pg_receivers],
    "INSIGHTS": [pg_insights, pg_eda, pg_sql],
    "PRO EVALUATION": [pg_sustainability, pg_ai, pg_reports]
})
pg.run()
