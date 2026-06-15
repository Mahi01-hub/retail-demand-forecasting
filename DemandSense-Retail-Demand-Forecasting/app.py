import streamlit as st
from streamlit_lottie import st_lottie
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go
import joblib
import numpy as np

# ---------------- PAGE CONFIG ----------------
model = joblib.load(
    "retail_demand_forecasting_model.pkl"
)
st.set_page_config(
    page_title="AI Retail Demand Forecasting",
    page_icon="🛒",
    layout="wide"
)

# ---------------- BACKGROUND ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg,
        #0f172a,
        #1e293b,
        #0f172a,
        #334155);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
    color: white;
}

@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

.metric-card {
    background-color: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "predicted_sales" not in st.session_state:
    st.session_state.predicted_sales = None

if "inventory_risk" not in st.session_state:
    st.session_state.inventory_risk = None

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- LOTTIE FUNCTION ----------------
def load_lottieurl(url):
    r = requests.get(url)

    if r.status_code != 200:
        return None

    return r.json()

lottie_ai = load_lottieurl(
    "https://assets5.lottiefiles.com/packages/lf20_kyu7xb1v.json"
)

# ---------------- HEADER ----------------
col1, col2 = st.columns([4,1])

with col1:
    st.title("🛒 AI Retail Demand Forecasting System")
    st.write(
        "Predict future sales and optimize inventory using AI."
    )

with col2:
    current_time = datetime.now().strftime(
        "%d %b %Y\n%I:%M:%S %p"
    )
    st.info(f"🕒 {current_time}")

# ---------------- LOTTIE ----------------
if lottie_ai:
    _, col, _ = st.columns([1,2,1])

    with col:
        st_lottie(
            lottie_ai,
            height=250
        )

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Controls")

store = st.sidebar.number_input(
    "🏬 Store Number",
    min_value=1,
    max_value=45,
    value=1
)

dept = st.sidebar.number_input(
    "📦 Department Number",
    min_value=1,
    value=1
)

holiday = st.sidebar.selectbox(
    "🎉 Is Holiday?",
    ["No", "Yes"]
)

temperature = st.sidebar.slider(
    "🌡️ Temperature",
    0.0,
    100.0,
    70.0
)

if st.sidebar.button("🚀 Predict Sales"):

    holiday_value = 1 if holiday == "Yes" else 0

    input_data = np.array([
        [store, dept, holiday_value]
    ])

    predicted_sales = model.predict(
        input_data
    )[0]

    if predicted_sales > 30000:
        inventory_risk = "High"

    elif predicted_sales > 15000:
        inventory_risk = "Medium"

    else:
        inventory_risk = "Low"

    st.session_state.predicted_sales = predicted_sales
    st.session_state.inventory_risk = inventory_risk

    # Save history
    st.session_state.history.append({
        "Store": store,
        "Department": dept,
        "Holiday": holiday,
        "Temperature": temperature,
        "Predicted Sales": predicted_sales,
        "Risk": inventory_risk
    })

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard",
    "📈 Analytics",
    "🤖 AI Insights",
    "📄 Reports",
    "🕒 History",
    "📖 About"
])

# ---------------- DASHBOARD ----------------
with tab1:

    if st.session_state.predicted_sales is not None:

        predicted_sales = st.session_state.predicted_sales
        inventory_risk = st.session_state.inventory_risk

        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "💰 Predicted Sales",
                f"${predicted_sales:,.0f}",
                "+12%"
            )

        with col2:
            st.metric(
                "📦 Inventory Risk",
                inventory_risk
            )

        with col3:
            st.metric(
                "🏬 Store",
                store
            )

        with col4:
            st.metric(
                "🌡️ Temperature",
                f"{temperature}°F"
            )

        st.subheader("🤖 AI Recommendation")

        if predicted_sales > 30000:

            st.error(
                "🔴 High demand expected. Increase Inventory."
            )

        elif predicted_sales > 15000:

            st.warning(
                "🟡 Moderate demand expected. Maintain Inventory."
            )

        else:

            st.success(
                "🟢 Lower demand expected. Reduce Inventory."
            )

        # Gauge Meter
        st.subheader("📦 Inventory Risk Meter")

        if inventory_risk == "Low":
            risk_score = 30

        elif inventory_risk == "Medium":
            risk_score = 65

        else:
            risk_score = 90

        fig = go.Figure(go.Indicator(

            mode="gauge+number",

            value=risk_score,

            title={
                'text': "Demand Risk Level"
            },

            gauge={

                'axis': {
                    'range': [0, 100]
                },

                'bar': {
                    'color': "cyan"
                },

                'steps': [

                    {
                        'range': [0, 40],
                        'color': "green"
                    },

                    {
                        'range': [40, 75],
                        'color': "yellow"
                    },

                    {
                        'range': [75, 100],
                        'color': "red"
                    }
                ]
            }
        ))

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "⬅️ Enter details from the sidebar and click 'Predict Sales'."
        )

# ---------------- ANALYTICS ----------------
with tab2:

    if st.session_state.predicted_sales is not None:

        predicted_sales = st.session_state.predicted_sales

        sales_data = pd.DataFrame({
            "Week": [
                "Week 1",
                "Week 2",
                "Week 3",
                "Prediction"
            ],

            "Sales": [
                predicted_sales - 4000,
                predicted_sales - 2500,
                predicted_sales - 1000,
                predicted_sales
            ]
        })

        st.subheader("📈 Sales Trend")

        st.line_chart(
            sales_data.set_index(
                "Week"
            )
        )

        st.subheader(
            "📊 Department Performance"
        )

        bar_data = pd.DataFrame({

            "Department": [
                "Dept A",
                "Dept B",
                "Dept C",
                "Current"
            ],

            "Sales": [
                18000,
                22000,
                24000,
                predicted_sales
            ]
        })

        st.bar_chart(
            bar_data.set_index(
                "Department"
            )
        )

        st.subheader(
            "🥧 Demand Distribution"
        )

        pie_data = pd.DataFrame({

            "Category": [
                "High",
                "Medium",
                "Low"
            ],

            "Percentage": [
                40,
                35,
                25
            ]
        })

        fig = px.pie(
            pie_data,
            names="Category",
            values="Percentage",
            hole=0.4
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ---------------- INSIGHTS ----------------
with tab3:

    if st.session_state.predicted_sales is not None:

        predicted_sales = st.session_state.predicted_sales

        insights = []

        if holiday == "Yes":

            insights.append(
                "🎉 Holiday detected: Demand may increase."
            )

        if temperature > 80:

            insights.append(
                "🌡️ High temperature may affect seasonal products."
            )

        if predicted_sales > 30000:

            insights.append(
                "📈 Demand surge expected."
            )

        insights.append(
            f"💰 Expected sales: ${predicted_sales:,.0f}"
        )

        insights.append(
            f"📦 Inventory Risk: {inventory_risk}"
        )

        for i in insights:

            st.info(i)

# ---------------- REPORTS ----------------
with tab4:

    if st.session_state.predicted_sales is not None:

        
        report = pd.DataFrame({

            "Store": [store],
            "Department": [dept],
            "Holiday": [holiday],
            "Temperature": [temperature],
            "Predicted Sales": [st.session_state.predicted_sales],
            "Risk": [st.session_state.inventory_risk]
        })

        st.dataframe(report)

        csv = report.to_csv(
            index=False
        )

        st.download_button(
            label="📄 Download Report",
            data=csv,
            file_name="sales_report.csv",
            mime="text/csv"
        )
# ---------------- HISTORY ----------------
with tab5:

    st.subheader("🕒 Prediction History")

    if st.session_state.history:

        history_df = pd.DataFrame(
            st.session_state.history
        )

        st.dataframe(
            history_df,
            use_container_width=True
        )

        csv = history_df.to_csv(index=False)

        st.download_button(
            "📥 Download History",
            csv,
            file_name="prediction_history.csv",
            mime="text/csv"
        )

    else:

        st.info(
            "No predictions made yet."
        )


# ---------------- ABOUT ----------------
with tab6:

    st.subheader("📖 About This Project")

    st.markdown("""
### 🎯 Objective
Predict future retail sales and provide inventory recommendations using AI.

### 🛠 Technologies Used
- Python
- Streamlit
- Pandas
- Plotly
- Lottie Animations

### 📊 Dataset
Walmart Sales Forecasting Dataset

### ✨ Features
- Sales Prediction
- AI Inventory Recommendations
- Interactive Analytics Dashboard
- Prediction History Tracking
- Downloadable Reports
- Demand Risk Gauge Meter
""")
