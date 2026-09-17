import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Support Ticket System",
    page_icon="🎫",
    layout="wide"
)

st.title("🎫 AI Support Ticket System")
st.write("Ask natural-language questions about support tickets.")

# Health check
try:
    health = requests.get(f"{API_URL}/health", timeout=5).json()

    col1, col2 = st.columns(2)

    with col1:
        st.metric("System Status", health["status"])

    with col2:
        st.metric("Tickets Loaded", health["tickets_loaded"])

except Exception:
    st.error("Cannot connect to FastAPI. Make sure Uvicorn is running.")

st.divider()

# Question input
question = st.text_input(
    "Ask a question",
    placeholder="Example: How many open tickets are there?"
)

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            response = requests.post(
                f"{API_URL}/query",
                json={"question": question},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                st.subheader("Answer")
                st.success(data["answer"])

                st.subheader("Result")

                result = data["result"]

                if isinstance(result, (dict, list)):
                    st.json(result)
                else:
                    st.write(result)

            else:
                st.error(f"API Error: {response.text}")

        except Exception as e:
            st.error(f"Could not connect to API: {e}")

st.divider()

# Anomalies
st.subheader("🚨 Anomaly Detection")

if st.button("Detect Anomalies"):
    try:
        response = requests.get(
            f"{API_URL}/anomalies",
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            summary = data["summary"]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Long Resolution Anomalies",
                    summary["total_long_resolution_anomalies"]
                )

            with col2:
                st.metric(
                    "Old High-Priority Tickets",
                    summary["total_old_high_priority_anomalies"]
                )

            with col3:
                st.metric(
                    "Total Anomalies",
                    summary["total_anomalies"]
                )

            st.subheader("Long Resolution Anomalies")
            st.dataframe(
                data["long_resolution_anomalies"],
                use_container_width=True
            )

            st.subheader("Old High-Priority Tickets")
            st.dataframe(
                data["old_high_priority_anomalies"],
                use_container_width=True
            )

        else:
            st.error(f"API Error: {response.text}")

    except Exception as e:
        st.error(f"Could not connect to API: {e}")