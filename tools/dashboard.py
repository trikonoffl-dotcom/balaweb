import streamlit as st
import utils.db as db
import pandas as pd

def render():
    st.title("📊 Usage Dashboard")
    
    data, total_count = db.get_stats()
    
    # Summary Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Generations", total_count)
    
    monthly_stats = db.get_monthly_stats()
    current_month = pd.Timestamp.now().strftime('%Y-%m')
    this_month_count = monthly_stats.get(current_month, 0)
    
    with col2:
        st.metric("Generations This Month", this_month_count)
    
    with col3:
        # Get count for Business Cards vs Welcome Aboard
        bc_count = len([x for x in data if x['tool'] == 'Business Card'])
        st.metric("Business Cards Created", bc_count)

    st.divider()

    # History Table
    if data:
        st.subheader("Recent Activity")
        df = pd.DataFrame(data)
        # Rename and reorder for better display
        df = df[['created_at', 'tool', 'name', 'metadata']]
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(df, use_container_width=True)
        
        # Simple Chart
        st.subheader("Monthly Trends")
        if monthly_stats:
            chart_data = pd.DataFrame(list(monthly_stats.items()), columns=['Month', 'Count']).sort_values('Month')
            st.line_chart(chart_data.set_index('Month'))
    else:
        st.info("No data available yet. Start generating cards to see stats!")
