import streamlit as st
import pandas as pd
import plotly.express as px
from chat_parser import ChatParser
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Set page configuration with dark theme
st.set_page_config(
    page_title="WhatsApp Chat Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
        /* Main container */
        .main {
            background-color: #1a1a1a;
            padding: 2rem;
        }
        
        /* Headers */
        h1 {
            color: #4CAF50 !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            font-weight: 700 !important;
            padding-bottom: 1rem !important;
            border-bottom: 2px solid #4CAF50 !important;
            margin-bottom: 2rem !important;
        }
        
        h2 {
            color: #81c784 !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            font-weight: 600 !important;
            margin-top: 2rem !important;
        }
        
        /* Metric containers */
        div[data-testid="stMetricValue"] {
            font-size: 2rem !important;
            color: #4CAF50 !important;
        }
        
        div[data-testid="stMetricLabel"] {
            font-weight: 600 !important;
        }
        
        /* Cards */
        div[data-testid="column"] > div {
            background-color: #2d2d2d;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        
        /* Selectbox */
        div[data-testid="stSelectbox"] select {
            background-color: #2d2d2d !important;
            color: white !important;
            border: 1px solid #4CAF50 !important;
            border-radius: 5px !important;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .stPlotlyChart {
            animation: fadeIn 0.6s ease-in;
        }
    </style>
""", unsafe_allow_html=True)

# Modern color scheme
COLORS = {
    'primary': '#4CAF50',
    'secondary': '#81c784',
    'background': '#1a1a1a',
    'text': '#ffffff',
    'accent': '#69f0ae'
}

def create_modern_chart_theme():
    return {
        'template': 'plotly_dark',
        'margin': {'t': 30, 'r': 10, 'l': 10, 'b': 10},
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': COLORS['text'], 'family': 'Segoe UI'},
        'xaxis': dict(
            gridcolor='#333333',
            linecolor='#333333',
            showgrid=True
        ),
        'yaxis': dict(
            gridcolor='#333333',
            linecolor='#333333',
            showgrid=True
        ),
        'showlegend': True,
        'legend': dict(
            font=dict(color=COLORS['text']),
            bgcolor='rgba(0,0,0,0)'
        )
    }

def load_data():
    chat_file = '_chat.txt'
    if not os.path.exists(chat_file):
        st.error("⚠️ No chat data found!")
        st.markdown("""
        ### How to add your chat data:
        
        1. Open WhatsApp
        2. Go to the chat you want to analyze
        3. Click More options (⋮) > More > Export chat
        4. Choose "Without media"
        5. Save the file as `_chat.txt` in this directory
        
        > Note: Your chat data stays on your computer and is never uploaded anywhere.
        """)
        st.stop()
    
    try:
        with open(chat_file, 'r', encoding='utf-8') as f:
            chat_text = f.read()
    except UnicodeDecodeError:
        try:
            with open(chat_file, 'r', encoding='latin1') as f:
                chat_text = f.read()
        except Exception as e:
            st.error(f"❌ Error reading chat file: {str(e)}")
            st.stop()
    except Exception as e:
        st.error(f"❌ Error reading chat file: {str(e)}")
        st.stop()
    
    try:
        parser = ChatParser()
        return parser.parse_chat(chat_text)
    except Exception as e:
        st.error("❌ Error parsing chat data!")
        st.error(f"Details: {str(e)}")
        st.stop()

def main():
    st.title("📱 WhatsApp Chat Analysis")
    
    # Add file uploader as an alternative
    uploaded_file = st.file_uploader("Upload your WhatsApp chat export (or place '_chat.txt' in the app directory)", 
                                   type=['txt'])
    
    # Load data
    with st.spinner('Loading chat data...'):
        if uploaded_file is not None:
            # If file is uploaded, read from upload
            try:
                chat_text = uploaded_file.getvalue().decode('utf-8')
                parser = ChatParser()
                df = parser.parse_chat(chat_text)
            except Exception as e:
                st.error("❌ Error processing uploaded file!")
                st.error(f"Details: {str(e)}")
                st.stop()
        else:
            # Try loading from _chat.txt
            df = load_data()
        
        if df is None or df.empty:
            st.error("❌ No valid chat data found!")
            st.stop()
            
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
    
    try:
        # Basic Statistics in modern cards
        st.header("📊 Chat Overview")
        metrics_container = st.container()
        with metrics_container:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Messages", f"{len(df):,}", 
                         delta=f"+{len(df[df['date'] == df['date'].max()])} today")
            with col2:
                st.metric("Active Users", df['username'].nunique())
            with col3:
                days = (df['date'].max() - df['date'].min()).days
                st.metric("Days Active", f"{days:,}")
            with col4:
                media_count = len(df[df['type'] == 'media'])
                st.metric("Media Shared", f"{media_count:,}")
        
        # Message Activity with modern styling
        st.header("📈 Message Trends")
        daily_messages = df.groupby('date').size().reset_index(name='count')
        fig = px.line(daily_messages, x='date', y='count',
                    title='Daily Message Volume')
        fig.update_layout(**create_modern_chart_theme())
        fig.update_traces(line=dict(color=COLORS['primary'], width=2))
        st.plotly_chart(fig, use_container_width=True)
        
        # User Activity Analysis with modern styling
        st.header("👥 User Engagement")
        col1, col2 = st.columns(2)
        
        with col1:
            user_message_counts = df['username'].value_counts().head(10)
            fig = px.bar(x=user_message_counts.index, y=user_message_counts.values,
                        title='Top Contributors',
                        labels={'x': 'User', 'y': 'Messages Sent'})
            fig.update_layout(**create_modern_chart_theme())
            fig.update_traces(marker_color=COLORS['primary'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            message_types = df['type'].value_counts()
            fig = px.pie(values=message_types.values, names=message_types.index,
                        title='Message Types',
                        color_discrete_sequence=[COLORS['primary'], COLORS['secondary'], COLORS['accent']])
            fig.update_layout(**create_modern_chart_theme())
            st.plotly_chart(fig, use_container_width=True)
        
        # Hourly Activity Pattern with modern styling
        st.header("🕰️ Chat Patterns")
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        hourly_activity = df.groupby('hour').size().reset_index(name='count')
        fig = px.bar(hourly_activity, x='hour', y='count',
                    title='Message Distribution by Hour',
                    labels={'hour': 'Hour of Day (24h)', 'count': 'Messages'})
        fig.update_layout(**create_modern_chart_theme())
        fig.update_traces(marker_color=COLORS['primary'])
        st.plotly_chart(fig, use_container_width=True)
        
        # User Details with modern styling
        st.header("👤 User Insights")
        selected_user = st.selectbox("Select User", df['username'].unique())
        user_df = df[df['username'] == selected_user]
        
        user_metrics_container = st.container()
        with user_metrics_container:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Messages", f"{len(user_df):,}")
            with col2:
                st.metric("Media Shared", f"{len(user_df[user_df['type'] == 'media']):,}")
            with col3:
                st.metric("First Message", user_df['timestamp'].min().strftime('%Y-%m-%d'))
            with col4:
                st.metric("Last Message", user_df['timestamp'].max().strftime('%Y-%m-%d'))
        
        # User's daily activity pattern
        user_daily = user_df.groupby('date').size().reset_index(name='count')
        fig = px.line(user_daily, x='date', y='count',
                    title=f"{selected_user}'s Daily Activity",
                    labels={'count': 'Messages', 'date': 'Date'})
        fig.update_layout(
            **create_modern_chart_theme(),
            title_font_size=18,
            title_font_color=COLORS['text']
        )
        fig.update_traces(line_color=COLORS['accent'])
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error("❌ Error rendering visualizations!")
        st.error(f"Details: {str(e)}")

if __name__ == "__main__":
    main()
