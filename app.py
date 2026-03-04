# app.py - 主应用程序文件
import streamlit as st
import duckdb
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# 页面配置
st.set_page_config(
    page_title="工程机械高管驾驶舱",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式 - 深色科技风
st.markdown("""
<style>
    header {visibility: hidden;}
    /* 页面顶部整体上移 */
    .block-container {
        padding-top: 0.5rem !important;
    }
    
    /* 标题间距压缩 */
    h1 {
        margin-top: 0rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    /* 副标题压缩 */
    h3 {
        margin-top: 0rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* 分割线压缩 */
    hr {
        margin: 0.3rem 0rem !important;
    }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: 2px;
    }
    
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    .kpi-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
        border-color: rgba(96, 165, 250, 0.3);
    }
    
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .kpi-label {
        color: #94a3b8;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .kpi-delta-positive {
        color: #4ade80;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .kpi-delta-negative {
        color: #f87171;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    hr {
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.3), transparent);
        margin: 2rem 0;
    }
    
    .status-dot {
        height: 8px;
        width: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    
    .status-good { background-color: #4ade80; box-shadow: 0 0 8px #4ade80; }
    .status-warning { background-color: #fbbf24; box-shadow: 0 0 8px #fbbf24; }
    .status-danger { background-color: #f87171; box-shadow: 0 0 8px #f87171; }
</style>
""", unsafe_allow_html=True)

# 生成模拟数据
def generate_data():
    np.random.seed(42)
    
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    months = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    
    # 财务数据
    financial_daily = pd.DataFrame({
        'date': dates,
        'revenue': np.cumsum(np.random.normal(2.5, 0.8, len(dates))) + 50,
        'profit': np.cumsum(np.random.normal(0.4, 0.2, len(dates))) + 8,
        'cash_flow': np.cumsum(np.random.normal(0.3, 0.5, len(dates))) + 15,
        'cost': np.cumsum(np.random.normal(2.1, 0.6, len(dates))) + 42
    })
    
    # 月度运营数据
    operations_monthly = pd.DataFrame({
        'month': months,
        'oee': np.random.uniform(0.75, 0.92, len(months)),
        'equipment_utilization': np.random.uniform(0.68, 0.85, len(months)),
        'on_time_delivery': np.random.uniform(0.88, 0.98, len(months)),
        'production_volume': np.random.randint(450, 650, len(months)),
        'defect_rate': np.random.uniform(0.01, 0.04, len(months)),
        'safety_incidents': np.random.randint(0, 5, len(months))
    })
    
    # 销售与订单数据
    sales_data = pd.DataFrame({
        'region': ['华北', '华东', '华南', '西南', '海外'] * 12,
        'month': list(months) * 5,
        'orders': np.random.randint(20, 80, 60),
        'backlog_value': np.random.uniform(50, 200, 60),
        'win_rate': np.random.uniform(0.25, 0.45, 60)
    })
    
    # 设备类别数据
    equipment_types = ['挖掘机', '起重机', '混凝土机械', '桩工机械', '路面机械']
    equipment_data = pd.DataFrame({
        'type': equipment_types,
        'sales_volume': [450, 320, 280, 190, 150],
        'revenue': [2.8, 3.2, 1.9, 1.4, 1.1],
        'market_share': [0.28, 0.24, 0.18, 0.15, 0.15],
        'growth_rate': [0.15, 0.08, 0.22, 0.12, 0.05]
    })
    
    # 供应链数据
    supply_data = pd.DataFrame({
        'supplier': ['供应商A', '供应商B', '供应商C', '供应商D', '供应商E'],
        'delivery_rate': [0.94, 0.89, 0.96, 0.91, 0.88],
        'quality_score': [92, 88, 95, 90, 87],
        'lead_time': [12, 15, 10, 14, 18],
        'cost_variance': [-0.02, 0.03, -0.01, 0.02, 0.04]
    })
    
    # 项目数据
    projects = pd.DataFrame({
        'project_name': ['雄安项目', '大湾区基建', '海外矿山', '高铁项目', '港口建设', '风电项目'],
        'progress': [0.85, 0.62, 0.45, 0.78, 0.91, 0.33],
        'budget_used': [0.82, 0.58, 0.48, 0.75, 0.88, 0.35],
        'cpi': [1.05, 1.12, 0.98, 1.08, 1.15, 0.95],
        'spi': [0.98, 0.89, 0.92, 1.02, 1.05, 0.88]
    })
    
    return financial_daily, operations_monthly, sales_data, equipment_data, supply_data, projects

# 初始化DuckDB
@st.cache_resource
def init_duckdb():
    conn = duckdb.connect(':memory:')
    
    fin_daily, ops_monthly, sales, equip, supply, projects = generate_data()
    
    conn.execute("CREATE TABLE financial_daily AS SELECT * FROM fin_daily")
    conn.execute("CREATE TABLE operations_monthly AS SELECT * FROM ops_monthly")
    conn.execute("CREATE TABLE sales_data AS SELECT * FROM sales")
    conn.execute("CREATE TABLE equipment_data AS SELECT * FROM equip")
    conn.execute("CREATE TABLE supply_data AS SELECT * FROM supply")
    conn.execute("CREATE TABLE projects AS SELECT * FROM projects")
    
    return conn, fin_daily, ops_monthly, sales, equip, supply, projects

# 加载数据
conn, fin_daily, ops_monthly, sales, equip, supply, projects = init_duckdb()

# 页面标题
st.markdown('<h1 class="main-title">🏗️ 工程机械行业高管驾驶舱</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Executive Dashboard | Construction Machinery Industry</p>', unsafe_allow_html=True)

# 顶部筛选栏
#col_filter1, col_filter2, col_filter3, col_filter4 = st.columns([2, 2, 2, 2])
#with col_filter1:
#    selected_year = st.selectbox("📅 年度", ["2024", "2023", "2022"], index=0)
#with col_filter2:
#    selected_region = st.selectbox("🌍 区域", ["全部", "华北", "华东", "华南", "西南", "海外"], index=0)
#with col_filter3:
#   selected_product = st.selectbox("🏭 产品类别", ["全部", "挖掘机", "起重机", "混凝土机械", "桩工机械", "路面机械"], index=0)
#with col_filter4:
 #   refresh = st.button("🔄 刷新数据", use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)
# 第一行：核心KPI指标
st.markdown("### 📊 核心财务指标")

# KPI数据（模拟实时）
total_revenue = 128.5
total_profit = 16.8
cash_flow = 23.4
profit_margin = 13.1
order_backlog = 156.7

kpi_cols = st.columns(5)

with kpi_cols[0]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">💰 总营收</div>
        <div class="kpi-value" style="color: #60a5fa;">{total_revenue:.1f}亿</div>
        <div class="kpi-delta-positive">▲ 12.5% 同比</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[1]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">📈 净利润</div>
        <div class="kpi-value" style="color: #4ade80;">{total_profit:.1f}亿</div>
        <div class="kpi-delta-positive">▲ 8.3% 同比</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[2]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">💵 经营现金流</div>
        <div class="kpi-value" style="color: #f472b6;">{cash_flow:.1f}亿</div>
        <div class="kpi-delta-positive">▲ 15.2% 同比</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[3]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">📊 净利润率</div>
        <div class="kpi-value" style="color: #c084fc;">{profit_margin:.1f}%</div>
        <div class="kpi-delta-negative">▼ 0.5pp 同比</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[4]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">📋 在手订单</div>
        <div class="kpi-value" style="color: #fbbf24;">{order_backlog:.1f}亿</div>
        <div class="kpi-delta-positive">▲ 22.1% 同比</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
# 第四行：产品分析、供应链与项目监控
row4_col1, row4_col2, row4_col3 = st.columns([2, 2, 2])

with row4_col1:
    st.markdown("#### 🏗️ 产品类别营收分析")
    
    equip_data = conn.execute("SELECT * FROM equipment_data").fetchdf()
    
    fig_product = go.Figure()
    
    fig_product.add_trace(go.Bar(
        x=equip_data['type'],
        y=equip_data['revenue'],
        name='营收(亿元)',
        marker=dict(
            color=['#60a5fa', '#c084fc', '#f472b6', '#4ade80', '#fbbf24'],
            line=dict(color='rgba(255,255,255,0.1)', width=1)
        ),
        text=equip_data['revenue'],
        textposition='outside',
        textfont=dict(color='#e2e8f0')
    ))
    
    fig_product.add_trace(go.Scatter(
        x=equip_data['type'],
        y=equip_data['growth_rate'] * 100,
        name='增长率(%)',
        mode='lines+markers',
        line=dict(color='#fbbf24', width=3),
        marker=dict(size=10, symbol='star', color='#fbbf24'),
        yaxis='y2'
    ))
    
    fig_product.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        margin=dict(l=40, r=40, t=30, b=80),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(tickangle=-30, showgrid=False),
        yaxis=dict(title='营收(亿元)', showgrid=True, gridcolor='rgba(148, 163, 184, 0.1)'),
        yaxis2=dict(title='增长率(%)', overlaying='y', side='right', showgrid=False),
        height=350
    )
    
    st.plotly_chart(fig_product, use_container_width=True)

with row4_col2:
    st.markdown("#### 📊 供应商绩效矩阵")
    
    supply_data = conn.execute("SELECT * FROM supply_data").fetchdf()
    
    fig_supply = go.Figure()
    
    fig_supply.add_trace(go.Scatter(
        x=supply_data['delivery_rate'] * 100,
        y=supply_data['quality_score'],
        mode='markers+text',
        text=supply_data['supplier'],
        textposition="top center",
        textfont=dict(size=10, color='#e2e8f0'),
        marker=dict(
            size=supply_data['lead_time'] * 2,
            color=supply_data['cost_variance'],
            colorscale=[[0, '#4ade80'], [0.5, '#fbbf24'], [1, '#f87171']],
            showscale=True,
            colorbar=dict(title="成本偏差", tickfont=dict(color='#e2e8f0')),
            line=dict(color='rgba(255,255,255,0.5)', width=1)
        ),
        hovertemplate='%{text}<br>交付率: %{x:.1f}%<br>质量分: %{y}<br>提前期: %{marker.size:.0f}天<extra></extra>'
    ))
    
    fig_supply.add_hline(y=90, line_dash="dash", line_color="rgba(148, 163, 184, 0.3)")
    fig_supply.add_vline(x=92, line_dash="dash", line_color="rgba(148, 163, 184, 0.3)")
    fig_supply.add_annotation(x=88, y=97, text="问题供应商", showarrow=False, font=dict(color='#f87171', size=12))
    fig_supply.add_annotation(x=96, y=97, text="战略供应商", showarrow=False, font=dict(color='#4ade80', size=12))
    
    fig_supply.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        margin=dict(l=40, r=40, t=30, b=40),
        xaxis=dict(title='交付率(%)', range=[85, 100], showgrid=True, gridcolor='rgba(148, 163, 184, 0.1)'),
        yaxis=dict(title='质量评分', range=[85, 100], showgrid=True, gridcolor='rgba(148, 163, 184, 0.1)'),
        height=350
    )
    
    st.plotly_chart(fig_supply, use_container_width=True)

with row4_col3:
    st.markdown("#### 🎯 重大项目健康度")
    
    projects_data = conn.execute("SELECT * FROM projects").fetchdf()
    
    fig_projects = make_subplots(
        rows=2, cols=3,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}],
               [{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]],
        vertical_spacing=0.3,
        horizontal_spacing=0.1
    )
    
    colors = ['#4ade80', '#60a5fa', '#fbbf24', '#c084fc', '#f472b6', '#94a3b8']
    
    for idx, row in projects_data.iterrows():
        row_idx = idx // 3 + 1
        col_idx = idx % 3 + 1
        
        health_score = (row['cpi'] * 0.5 + row['spi'] * 0.5) * 100
        
        fig_projects.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=health_score,
                title={'text': row['project_name'], 'font': {'size': 12, 'color': '#e2e8f0'}},
                number={'font': {'size': 16, 'color': '#e2e8f0'}},
                gauge={
                    'axis': {'range': [80, 120], 'tickwidth': 1},
                    'bar': {'color': colors[idx % len(colors)]},
                    'bgcolor': 'rgba(30, 41, 59, 0.5)',
                    'borderwidth': 0,
                    'threshold': {
                        'line': {'color': "white", 'width': 2},
                        'thickness': 0.75,
                        'value': 100
                    }
                }
            ),
            row=row_idx, col=col_idx
        )
    
    fig_projects.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        margin=dict(l=20, r=20, t=30, b=20),
        height=350
    )
    
    st.plotly_chart(fig_projects, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)


# 第二行：图表区域
row2_col1, row2_col2 = st.columns([3, 2])

with row2_col1:
    st.markdown("#### 📈 营收与利润趋势")
    
    monthly_data = conn.execute("""
        SELECT 
            DATE_TRUNC('month', date) as month,
            MAX(revenue) - MIN(revenue) as monthly_revenue,
            MAX(profit) - MIN(profit) as monthly_profit
        FROM financial_daily
        GROUP BY DATE_TRUNC('month', date)
        ORDER BY month
    """).fetchdf()
    
    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_trend.add_trace(
        go.Scatter(
            x=monthly_data['month'], 
            y=monthly_data['monthly_revenue'],
            name="月度营收",
            fill='tozeroy',
            fillcolor='rgba(96, 165, 250, 0.2)',
            line=dict(color='#60a5fa', width=3),
            mode='lines+markers'
        ),
        secondary_y=False
    )
    
    fig_trend.add_trace(
        go.Scatter(
            x=monthly_data['month'], 
            y=monthly_data['monthly_profit'],
            name="月度利润",
            line=dict(color='#4ade80', width=3, dash='dot'),
            mode='lines+markers',
            marker=dict(size=8, symbol='diamond')
        ),
        secondary_y=True
    )
    
    fig_trend.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode='x unified'
    )
    
    fig_trend.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
    fig_trend.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)', secondary_y=False)
    fig_trend.update_yaxes(showgrid=False, secondary_y=True)
    
    st.plotly_chart(fig_trend, use_container_width=True)

with row2_col2:
    st.markdown("#### 🗺️ 区域销售分布")
    
    region_data = conn.execute("""
        SELECT 
            region,
            SUM(orders) as total_orders,
            SUM(backlog_value) as total_backlog
        FROM sales_data
        GROUP BY region
    """).fetchdf()
    
    fig_region = go.Figure(data=[go.Pie(
        labels=region_data['region'],
        values=region_data['total_orders'],
        hole=0.6,
        marker=dict(
            colors=['#60a5fa', '#c084fc', '#f472b6', '#4ade80', '#fbbf24'],
            line=dict(color='rgba(30, 41, 59, 0.8)', width=2)
        ),
        textinfo='label+percent',
        textfont=dict(size=12, color='#e2e8f0'),
        hovertemplate='%{label}<br>订单量: %{value}<br>占比: %{percent}<extra></extra>'
    )])
    
    fig_region.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        margin=dict(l=20, r=20, t=30, b=20),
        annotations=[dict(text='总订单<br>分布', x=0.5, y=0.5, font_size=16, showarrow=False, font_color='#94a3b8')]
    )
    
    st.plotly_chart(fig_region, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# 第三行：运营效率指标
st.markdown("### ⚙️ 运营效率监控")

row3_col1, row3_col2, row3_col3 = st.columns([1, 1, 1])

with row3_col1:
    st.markdown("#### 🏭 设备综合效率 (OEE)")
    
    oee_data = conn.execute("SELECT month, oee FROM operations_monthly ORDER BY month").fetchdf()
    
    fig_oee = go.Figure()
    fig_oee.add_trace(go.Bar(
        x=oee_data['month'],
        y=oee_data['oee'] * 100,
        marker=dict(
            color=oee_data['oee'],
            colorscale=[[0, '#f87171'], [0.5, '#fbbf24'], [1, '#4ade80']],
            showscale=False,
            line=dict(color='rgba(255,255,255,0.1)', width=1)
        ),
        text=[f"{v:.1f}%" for v in oee_data['oee'] * 100],
        textposition='outside',
        textfont=dict(color='#e2e8f0', size=10)
    ))
    
    fig_oee.add_hline(y=85, line_dash="dash", line_color="#4ade80", annotation_text="目标线 85%")
    
    fig_oee.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        margin=dict(l=40, r=20, t=30, b=40),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(148, 163, 184, 0.1)', range=[60, 100]),
        height=300
    )
    
    st.plotly_chart(fig_oee, use_container_width=True)

with row3_col2:
    st.markdown("#### 📦 准时交付率")
    
    delivery_data = conn.execute("SELECT month, on_time_delivery FROM operations_monthly ORDER BY month").fetchdf()
    
    fig_delivery = go.Figure()
    fig_delivery.add_trace(go.Scatter(
        x=delivery_data['month'],
        y=delivery_data['on_time_delivery'] * 100,
        fill='tozeroy',
        fillcolor='rgba(192, 132, 252, 0.2)',
        line=dict(color='#c084fc', width=3),
        mode='lines+markers',
        marker=dict(size=8, color='#c084fc'),
        name='交付率'
    ))
    
    fig_delivery.add_hline(y=95, line_dash="dash", line_color="#4ade80")
    
    fig_delivery.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        margin=dict(l=40, r=20, t=30, b=40),
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(148, 163, 184, 0.1)', range=[85, 100]),
        height=300
    )
    
    st.plotly_chart(fig_delivery, use_container_width=True)

with row3_col3:
    st.markdown("#### 🔧 设备利用率")
    
    util_data = conn.execute("SELECT month, equipment_utilization FROM operations_monthly ORDER BY month").fetchdf()
    
    fig_util = go.Figure()
    fig_util.add_trace(go.Scatter(
        x=util_data['month'],
        y=util_data['equipment_utilization'] * 100,
        mode='lines+markers',
        line=dict(color='#f472b6', width=3),
        marker=dict(size=8, color='#f472b6', symbol='circle'),
        fill='tonexty',
        fillcolor='rgba(244, 114, 182, 0.1)'
    ))
    
    fig_util.add_trace(go.Scatter(
        x=util_data['month'],
        y=[60]*len(util_data),
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig_util.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        margin=dict(l=40, r=20, t=30, b=40),
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(148, 163, 184, 0.1)', range=[60, 90]),
        height=300
    )
    
    st.plotly_chart(fig_util, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)



# 第五行：详细数据表格与预警信息
st.markdown("### 📋 详细数据监控")

row5_col1, row5_col2 = st.columns([2, 1])

with row5_col1:
    st.markdown("#### 📈 月度运营数据明细")
    
    detail_data = conn.execute("""
        SELECT 
            month as 月份,
            ROUND(oee * 100, 2) as OEE百分比,
            ROUND(equipment_utilization * 100, 2) as 设备利用率,
            ROUND(on_time_delivery * 100, 2) as 准时交付率,
            production_volume as 产量台数,
            ROUND(defect_rate * 100, 2) as 缺陷率,
            safety_incidents as 安全事故
        FROM operations_monthly
        ORDER BY month DESC
    """).fetchdf()
    
    st.dataframe(
        detail_data,
        use_container_width=True,
        height=300,
        column_config={
            "OEE百分比": st.column_config.ProgressColumn("OEE", min_value=0, max_value=100, format="%.1f%%"),
            "设备利用率": st.column_config.ProgressColumn("设备利用率", min_value=0, max_value=100, format="%.1f%%"),
            "准时交付率": st.column_config.ProgressColumn("交付率", min_value=0, max_value=100, format="%.1f%%"),
            "缺陷率": st.column_config.NumberColumn("缺陷率", format="%.2f%%")
        }
    )

with row5_col2:
    st.markdown("#### ⚠️ 关键预警")
    
    alerts = [
        {"level": "danger", "msg": "西南区交付率低于90%", "time": "2小时前"},
        {"level": "warning", "msg": "供应商C交付延迟3天", "time": "4小时前"},
        {"level": "warning", "msg": "风电项目SPI低于0.9", "time": "6小时前"},
        {"level": "good", "msg": "本月OEE创历史新高达91%", "time": "1天前"},
        {"level": "good", "msg": "海外订单增长35%", "time": "1天前"}
    ]
    
    for alert in alerts:
        dot_class = f"status-{alert['level']}"
        color = '#f87171' if alert['level'] == 'danger' else '#fbbf24' if alert['level'] == 'warning' else '#4ade80'
        
        st.markdown(f"""
        <div style="
            background: rgba(30, 41, 59, 0.5);
            border-left: 4px solid {color};
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 0 8px 8px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div>
                <span class="status-dot {dot_class}"></span>
                <span style="color: #e2e8f0; font-size: 0.9rem;">{alert['msg']}</span>
            </div>
            <span style="color: #64748b; font-size: 0.75rem;">{alert['time']}</span>
        </div>
        """, unsafe_allow_html=True)

# 底部页脚
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.8rem; padding: 1rem;">
    <p>© 2026 工程机械智能管理平台 | 数据更新时间: 2025-01-09 23:59:59 | 系统版本 v2.1.0</p>
    <p style="margin-top: 0.5rem;">
        <span style="margin: 0 10px;">🟢 系统运行正常</span>
        <span style="margin: 0 10px;">📊 数据延迟 < 5分钟</span>
        <span style="margin: 0 10px;">🔒 安全连接</span>
    </p>
</div>
""", unsafe_allow_html=True)
