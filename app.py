import streamlit as st
import requests
from typing import Dict, Any

# --- Configuration ---
API_URL = "http://localhost:8000/search"

# --- Utility Functions ---
def format_price(price: float) -> str:
    if price is None:
        return "N/A"
    if price >= 1e7:
        return f"₹{price / 1e7:.2f} Cr"
    elif price >= 1e5:
        return f"₹{price / 1e5:.2f} Lac"
    else:
        return f"₹{price:,.0f}"

def send_search_request(query: str) -> Dict[str, Any]:
    try:
        response = requests.post(API_URL, json={"user_query": query})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return {}

def normalize_property(prop: dict) -> dict:
    return {
        "project_name": prop.get("project_name") or prop.get("projectId") or "Unknown Project",
        "bhk_type": prop.get("bhk_type", "N/A"),
        "price": prop.get("price") or prop.get("min_price"),
        "carpet_area": prop.get("carpet_area") or prop.get("carpetArea"),
        "status": (prop.get("status") or "N/A").replace("_", " ").title(),
        "possession": (prop.get("possession_date") or prop.get("possessionDate") or "N/A").split(" ")[0],
        "address": prop.get("fullAddress") or prop.get("full_address") or "Not available"
    }

def render_property_card(property_data: dict, highlight_best=False):
    prop = normalize_property(property_data)
    header = f"{prop['project_name']} - {prop['bhk_type']}"
    if highlight_best:
        header += " ⭐ Best Match"
    st.markdown(f"#### {header}")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Price", format_price(prop['price']))
        st.markdown(f"**Area:** {prop['carpet_area'] if prop['carpet_area'] else 'N/A'} sq.ft")
    with col2:
        st.markdown(f"**Status:** `{prop['status']}`")
        st.markdown(f"**Possession:** {prop['possession']}")

    st.caption(f"**Address:** {prop['address']}")
    st.markdown("---")

def render_best_summary(property_data: dict):
    prop = normalize_property(property_data)
    points = [
        f"Project: {prop['project_name']}",
        f"BHK Type: {prop['bhk_type']}",
        f"Price: {format_price(prop['price'])}",
        f"Area: {prop['carpet_area'] if prop['carpet_area'] else 'N/A'} sq.ft",
        f"Status: {prop['status']} | Possession: {prop['possession']}"
    ]
    st.markdown("### 5-Point Summary (Best Match)")
    for idx, p in enumerate(points, start=1):
        st.markdown(f"{idx}. {p}")
    st.markdown("---")

# --- Streamlit UI ---
st.set_page_config(page_title="AI Property Discovery Chatbot", layout="wide")
st.title("AI Property Discovery Chatbot")
st.markdown("Ask about your Dream Property, I here to search Best value for Money property")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message.get("role", "assistant")):
        msg_type = message.get("type")
        if msg_type == "summary":
            st.markdown("### Assistant Summary")
            st.info(message.get("content", "No summary provided."))
        elif msg_type == "results":
            props = message.get("properties", [])
            if props:
                render_best_summary(props[0])
                for idx, prop in enumerate(props):
                    render_property_card(prop, highlight_best=(idx == 0))
            else:
                st.warning("No matching properties found.")
        else:
            st.markdown(message.get("content", ""))

# Handle user input
if prompt := st.chat_input("What property are you looking for?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Searching..."):
        response_data = send_search_request(prompt)

    if response_data:
        st.session_state.messages.append({
            "role": "assistant",
            "type": "summary",
            "content": response_data.get("summary", "No summary provided.")
        })
        st.session_state.messages.append({
            "role": "assistant",
            "type": "results",
            "properties": response_data.get("properties", [])
        })

    st.rerun()
