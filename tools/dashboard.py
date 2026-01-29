import streamlit as st
import utils.db as db
import pandas as pd

def render():
    st.markdown("""
    <style>
        .metric-card {
            background: white;
            padding: 24px;
            border-radius: 12px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
        }
        .metric-title {
            color: #64748B;
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .metric-value {
            color: #1E1B4B;
            font-size: 2rem;
            font-weight: 700;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("Trikon Performance Dashboard")
    
    data, total_count = db.get_stats()
    
    # Summary Metrics with Custom HTML
    col1, col2, col3 = st.columns(3)
    
    monthly_stats = db.get_monthly_stats()
    current_month = pd.Timestamp.now().strftime('%Y-%m')
    this_month_count = monthly_stats.get(current_month, 0)
    bc_count = len([x for x in data if x['tool'] == 'Business Card'])

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Generations</div>
            <div class="metric-value">{total_count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">This Month</div>
            <div class="metric-value">{this_month_count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Business Cards</div>
            <div class="metric-value">{bc_count}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # History Table
    if data:
        st.subheader("Generation History")
        df = pd.DataFrame(data)
        df = df[['created_at', 'tool', 'name', 'metadata']]
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(df, use_container_width=True)
        
        # Simple Chart
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Growth Trends")
        if monthly_stats:
            chart_data = pd.DataFrame(list(monthly_stats.items()), columns=['Month', 'Count']).sort_values('Month')
            # Custom line chart color
            st.line_chart(chart_data.set_index('Month'), color="#6366F1")
    else:
        st.info("No data available yet. Start generating cards to see stats!")
