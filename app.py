import streamlit as st
import streamlit.components.v1 as components
import requests
import uuid
from datetime import datetime
import plotly.graph_objects as go
import numpy as np
import time
# Page configuration
st.set_page_config(page_title="Equitech Financial Analyst", page_icon="📊", layout="wide")
chat_html = """
<flowise-fullchatbot></flowise-fullchatbot>
<script type="module">
    import Chatbot from "https://cdn.jsdelivr.net/npm/flowise-embed/dist/web.js"
    Chatbot.initFull({
        chatflowid: "1a43e953-914a-4ff0-b471-62e9ed7a4ebf",
        apiHost: "http://localhost:3000",
    })
</script>
"""



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
            
     .custom-subheader {
        text-align: right; 
        color: green;    
        margin-bottom: 10px;  
    }
</style>
""", unsafe_allow_html=True)

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())
if 'chat_histories' not in st.session_state:
    st.session_state['chat_histories'] = [{'id': st.session_state['session_id'], 'history': [], 'timestamp': datetime.now()}]
if 'current_document' not in st.session_state:
    st.session_state['current_document'] = None

if 'clicked_metric' not in st.session_state:
    st.session_state.clicked_metric = None

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



st.markdown('<p class="custom-subheader">Key Financial Insights</p>', unsafe_allow_html=True)



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


def get_financial_data(metric: str, company: str):
    try:
        response = requests.post(
            "http://127.0.0.1:8000/get-financial-data",
            json={"company": company, "metric": metric}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch financial data: {str(e)}")
        return None

def plot_metric_chart(year_metrics: dict, title: str, currency: str):
    years = list(year_metrics.keys())
    values = list(year_metrics.values())
    fig = go.Figure(data=go.Bar(x=years, y=values, name=title))
    fig.update_layout(
        title=f"{title} ({currency})",
        xaxis_title="Year",
        yaxis_title=f"Value ({currency})",
        height=415,
    )
    return fig


metrics = {
    "Revenue": "revenue",
    "Net Income": "net_income",
    "EPS": "eps",
    "Operating Margin": "operating_margin",
    "ROE": "roe",
    "Free Cash Flow": "free_cash_flow",
    "Debt to Equity": "debt_to_equity",
    "P/E Ratio": "pe_ratio"
}

# Create metric buttons
cols = st.columns(4)
for i, (display_name, metric_key) in enumerate(metrics.items()):
    if cols[i % 4].button(display_name):
        st.session_state.clicked_metric = metric_key

c1, c2 = st.columns(2)


with c1: st.markdown(f'<span class="text-red">Financial metric clicked: </span>',unsafe_allow_html=True)
with c2: st.markdown(f'<span class="text-green-bold">{st.session_state.clicked_metric}</span>',unsafe_allow_html=True)

if st.session_state.clicked_metric:
    with st.spinner(f'Fetching {st.session_state.clicked_metric} data...'):
        financial_data = get_financial_data(st.session_state.clicked_metric, company_key)
    
    
    if financial_data:
        year_metrics = financial_data['year_metrics']
        currency = financial_data['currency']
        comment = financial_data['comment']
        
        # Convert years to integers and sort
        sorted_years = sorted(map(int, year_metrics.keys()))
        
        # Display latest value and YoY change
        latest_year = sorted_years[-1]
        latest_value = year_metrics[str(latest_year)]
        previous_year = sorted_years[-2] if len(sorted_years) > 1 else latest_year
        previous_value = year_metrics.get(str(previous_year), latest_value)
        
        yoy_change = ((latest_value - previous_value) / previous_value * 100) if previous_value != 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                f"Latest Value ({latest_year})", 
                f"{currency} {latest_value:,.0f}", 
                f"{yoy_change:.1f}%"
            )
        
        # Convert year_metrics to use integer keys for plotting
        int_year_metrics = {int(year): value for year, value in year_metrics.items()}
        
        # Plot chart
        m1, m2 = st.columns(2)

        with m1:
            st.plotly_chart(
                plot_metric_chart(int_year_metrics, f'{company_key} {st.session_state.clicked_metric}', currency), 
                use_container_width=True
            )
        
        with m2:
            # Display comment with expander
            with st.expander("View Details"):
                st.write(financial_data)
    else:
        st.error(f"Unable to retrieve data for {st.session_state.clicked_metric}. Please try another metric or check the backend.")
else:
    st.info("Please select a metric to view financial data.")


me1, me2 = st.columns(2)

with me2:
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
                    "http://127.0.0.1:8000/ask",
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
            requests.post("http://127.0.0.1:8000/clear_session", json={"session_id": session_id})
            st.session_state["chat_history"].clear()
            st.rerun()

    st.write(' ')

with me1:
    ###   Footer
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





