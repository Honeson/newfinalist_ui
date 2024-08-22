import streamlit as st
import requests
import uuid
from datetime import datetime
import plotly.graph_objects as go
import numpy as np
import time
# Page configuration
st.set_page_config(page_title="Equitech Financial Analyst", page_icon="📊", layout="wide")

# Custom CSS to remove top padding/margin
st.markdown(
    """
    <style>
    /* Remove the top padding/margin */
    .block-container {
        padding-top: 0px;
        margin-top: -25px; /* Adjust this value as needed */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Custom CSS for a professional financial theme
st.markdown("""
<style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #1E1E1E;
        color: #E0E0E0;
    }
    .main {
        background-color: #2B2B2B;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stTextInput > div > div > input {
        background-color: #3C3C3C;
        color: #E0E0E0;
        border: 1px solid #555;
        border-radius: 5px;
        padding: 10px 15px;
        font-size: 16px;
    }
    .stButton > button {
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s;
        background-color: #007bff;
        color: white;
        border: none;
    }
    .stButton > button:hover {
        background-color: #0056b3;
    }
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        width: 80%;
        word-wrap: break-word;
    }
    .chat-message.user {
        background-color: #1C3B4C;
        color: #E0E0E0;
        margin-left: auto;
    }
    .chat-message.bot {
        background-color: #3C3C3C;
        color: #E0E0E0;
        margin-right: auto;
    }
    .chat-message p {
        margin: 0;
        line-height: 1.4;
    }
    .sidebar .sidebar-content {
        background-color: #343a40;
        color: #f8f9fa;
    }
    .sidebar .sidebar-content .stButton > button {
        background-color: #28a745;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .sidebar .sidebar-content .stButton > button:hover {
        background-color: #218838;
    }
            
    .top-right-text {
        position: absolute;
        top: 10px; 
        right: 10px; 
        font-weight: bold;
        font-size: 18px; 
    }
    .text-green {
        color: green; 
    }
    .text-red {
        color: red;
    }
    .text-green-bold {
        color: green; 
        font-size: 22px;
    }
</style>
""", unsafe_allow_html=True)

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())
if 'chat_histories' not in st.session_state:
    st.session_state['chat_histories'] = [{'id': st.session_state['session_id'], 'history': [], 'timestamp': datetime.now()}]
if 'current_document' not in st.session_state:
    st.session_state['current_document'] = None

# Header
st.title("📊 Equitech Financial Analyst")


with st.sidebar:

    st.image("static/logo.svg", width=150)
    
    st.markdown(
    f'<span class="text-green-bold">Get deep insights into the financials of top companies</span>',
    unsafe_allow_html=True
    )
    # Sidebar company selection
    st.sidebar.title("Select a Company")
    company_selection = st.sidebar.selectbox('',
        ["Nvidia", "MINISO", "Apple"]
    )
    company_key = company_selection.lower()

    # Define image mapping for each company
    image_map = {
        "nvidia": "static/nvidia.png",
        "miniso": "static/miniso.jpg",
        "apple": "static/apple.jpeg"
    }

    # Display the image based on company selection
    st.image(image_map.get(company_key, "static/default_hero.jpg"))
    #st.image("static/hero.jpg")

    st.subheader("Recent Analyses")
    for i, chat in enumerate(reversed(st.session_state['chat_histories'][-5:])):
        with st.expander(f"{chat['timestamp'].strftime('%Y-%m-%d %H:%M')} - {len(chat['history'])} queries"):
            st.write(f"Document: {chat.get('document', 'Unknown')}")
            st.write(f"Queries: {len(chat['history'])}")
            if chat['id'] == st.session_state['session_id']:
                st.info("Current Analysis")





# Unique session ID for each user session
session_id = str(uuid.uuid4())

# Chat history placeholder
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Function to display chat messages
def display_chat():
    for msg, is_user in st.session_state["chat_history"]:
        if is_user:
            st.markdown(f'<div class="chat-message user"><p>👤 {msg}</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message bot"><p>🤖 {msg["text"]}</p></div>', unsafe_allow_html=True)
            
            # Display source information
            with st.expander("View Source Information"):
                for source in msg["source_documents"]:
                    st.markdown(f"""
                    <div class="source-info">
                        <p><strong>File:</strong> {source['filename']}</p>
                        <p><strong>Page:</strong> {source['page_number']}</p>
                        <p><strong>Content:</strong> {source['page_content']}</p>
                    </div>
                    """, unsafe_allow_html=True)

# Dynamic text to reflect selected company
st.markdown(
    f'<div class="top-right-text">'
    f'<span class="text-green">Currently Analyzing: </span>'
    f'<span class="text-red">{company_selection}</span>'
    f'</div>',
    unsafe_allow_html=True
)


# Display chat messages
display_chat()

# Input form - always visible
user_input = st.text_input("Ask a financial question:", key="user_input")

if st.button("Analyze"):
    if user_input:
        st.session_state["chat_history"].append((user_input, True))
        with st.spinner("Preparing Your Response..."):
            response = requests.post(
                "https://newfinalist.onrender.com/ask",
                json={"question": user_input, "session_id": session_id, "company": company_key}
            )
            print(f"Frontend POST request with company: {company_key}")
            if response.status_code == 200:
                answer_data = response.json()["answer"]
                st.session_state["chat_history"].append((
                    {
                        "text": answer_data["answer"],
                        "source_documents": answer_data["source_documents"]
                    }, 
                    False
                ))
            else:
                st.error("Something went wrong. Please try again.")
        
        # Clear the input field after submitting
        st.session_state.user_input
        st.rerun()

if user_input:
    # Clear session button
    if st.button("Clear Session"):
        requests.post("https://newfinalist.onrender.com/ask", json={"session_id": session_id})
        st.session_state["chat_history"].clear()
        st.rerun()

st.write(' ')
st.subheader("Key Financial Insights")
st.write(' ')



# Custom CSS for button styling
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        background-color: #f8f9fa;
        color: #007bff;
        font-weight: bold;
        padding: 10px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #e9ecef;
    }
    </style>
    """, unsafe_allow_html=True)

# Session state to track the clicked metric
if 'clicked_metric' not in st.session_state:
    st.session_state.clicked_metric = None

# Create 8 buttons in a 2-row, 4-column layout
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Revenue"):
        st.session_state.clicked_metric = "revenue"
    if st.button("ROE"):
        st.session_state.clicked_metric = "roe"

with col2:
    if st.button("Net Income"):
        st.session_state.clicked_metric = "net_income"
    if st.button("Free Cash Flow"):
        st.session_state.clicked_metric = "free_cash_flow"

with col3:
    if st.button("EPS"):
        st.session_state.clicked_metric = "eps"
    if st.button("Debt to Equity"):
        st.session_state.clicked_metric = "debt_to_equity"

with col4:
    if st.button("Operating Margin"):
        st.session_state.clicked_metric = "operating_margin"
    if st.button("P/E Ratio"):
        st.session_state.clicked_metric = "pe_ratio"

# Get the clicked metric
metric_value = st.session_state.clicked_metric

# Display metrics in a 3-column layout
one, two, three = st.columns(3)

# First Column Metrics
with one:
    if metric_value == "revenue":
        st.metric("", "$16.68B", "+41%")
    elif metric_value == "net_income":
        st.metric("", "$4.02B", "+768%")
    elif metric_value == "eps":
        st.metric("", "$1.62", "+765%")
    elif metric_value == "operating_margin":
        st.metric("", "45%", "+5%")
    elif metric_value == "roe":
        st.metric("", "30%", "+3%")
    elif metric_value == "free_cash_flow":
        st.metric("", "$5.20B", "+150%")
    elif metric_value == "debt_to_equity":
        st.metric("", "0.5", "-10%")
    elif metric_value == "pe_ratio":
        st.metric("", "25", "+5%")
    else:
        st.write("")

# Second Column Metrics
with two:
    if metric_value == "revenue":
        st.metric("", "$4.02B", "+768%")
    elif metric_value == "net_income":
        st.metric("", "$1.62", "+765%")
    elif metric_value == "eps":
        st.metric("", "$16.68B", "+41%")
    elif metric_value == "operating_margin":
        st.metric("", "45%", "+5%")
    elif metric_value == "roe":
        st.metric("", "30%", "+3%")
    elif metric_value == "free_cash_flow":
        st.metric("", "$5.20B", "+150%")
    elif metric_value == "debt_to_equity":
        st.metric("", "0.5", "-10%")
    elif metric_value == "pe_ratio":
        st.metric("", "25", "+5%")
    else:
        st.write("")

# Third Column Metrics
with three:
    if metric_value == "revenue":
        st.metric("", "$1.62", "+765%")
    elif metric_value == "net_income":
        st.metric("", "$16.68B", "+41%")
    elif metric_value == "eps":
        st.metric("", "$4.02B", "+768%")
    elif metric_value == "operating_margin":
        st.metric("", "45%", "+5%")
    elif metric_value == "roe":
        st.metric("", "30%", "+3%")
    elif metric_value == "free_cash_flow":
        st.metric("", "$5.20B", "+150%")
    elif metric_value == "debt_to_equity":
        st.metric("", "0.5", "-10%")
    elif metric_value == "pe_ratio":
        st.metric("", "25", "+5%")
    else:
        st.write("")

st.markdown("---")

# Create a figure
fig = go.Figure()

# Define the data for the chart
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Add the trace to the figure
line = fig.add_trace(go.Scatter(x=x, y=y))

# Set the layout of the chart
fig.update_layout(
    xaxis_title="X",
    yaxis_title="Y",
    height=300,
    margin=dict(l=20, r=20, t=30, b=20)
)

# Create a function to update the chart
def update_chart():
    global x, y
    x = np.linspace(0, 10, 100)
    y = np.sin(x + np.pi * 2 * (time.time() % 1))
    line.data[0].x = x
    line.data[0].y = y
    return fig


st.plotly_chart(update_chart(), use_container_width=True, key="animated_chart")

# Footer
st.markdown("---")
st.write("🌐 Connected to: Equitech Ventures Financial Analysis Bot")
st.markdown(
    f'<span class="text-red">ℹ️ Pro Tips:</span>',
    unsafe_allow_html=True
    )
st.write("- Select a Company from the sidebar to start a new analysis.")
st.write("- Ask specific questions about financial metrics, trends, or comparisons.")
#st.caption("Powered by Equitech Ventures | © 2024")
st.markdown(
    f'<span class="text-green-bold">Powered by Equitech Ventures | © 2024</span>',
    unsafe_allow_html=True
    )

