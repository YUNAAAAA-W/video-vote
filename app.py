import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import random

# --- 配置 ---
DATA_FILE = 'video_votes.csv'

# 视频配置：包含标签内容与显示颜色
VIDEO_CONFIG = {
    1: {
        "name": "视频一",
        "labels": ["猕猴桃", "助农", "贵州", "营养"],
        "color": "#27ae60"  # 深绿色
    },
    2: {
        "name": "视频二",
        "labels": ["公园", "风景", "山水", "观山湖"],
        "color": "#2980b9"  # 深蓝色
    },
    3: {
        "name": "视频三",
        "labels": ["贵阳", "美食", "香辣", "特色"],
        "color": "#f39c12"  # 深黄色
    },
    4: {
        "name": "视频四",
        "labels": ["贵州", "非遗", "苗绣", "文化"],
        "color": "#c0392b"  # 深红色
    }
}

# --- 核心辅助函数 ---

def init_data():
    """初始化数据库文件，如果不存在则创建带表头的空文件"""
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=['video_id', 'label_idx', 'timestamp'])
        df.to_csv(DATA_FILE, index=False)

def load_data():
    """读取投票数据"""
    try:
        return pd.read_csv(DATA_FILE)
    except:
        return pd.DataFrame(columns=['video_id', 'label_idx', 'timestamp'])

def save_vote(video_id, label_idx):
    """
    优化点：使用 'a' (append) 模式追加写入。
    这样即使多个学生同时提交，系统也只是在文件末尾加行，
    比读取整个文件再覆盖要安全得多，适合 11 人以上的课堂环境。
    """
    new_row = pd.DataFrame([{
        'video_id': video_id, 
        'label_idx': label_idx, 
        'timestamp': pd.Timestamp.now()
    }])
    # 如果文件不存在则写入表头，否则只追加内容
    new_row.to_csv(DATA_FILE, mode='a', index=False, header=not os.path.exists(DATA_FILE))

def clear_all_data():
    """清空所有投票记录"""
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    init_data()

# --- 页面 1: 学生投票端 ---

def student_page():
    st.title("🎥 为视频选择标签")
    
    video_choice = st.selectbox(
        "第一步：请选择你观看的视频", 
        options=[1, 2, 3, 4],
        format_func=lambda x: VIDEO_CONFIG[x]['name']
    )
    
    config = VIDEO_CONFIG[video_choice]
    st.markdown(f"### 你选择的是：**{config['name']}**")
    
    # 针对每个视频单独记录本地是否已投票，防止学生在同一台设备重复刷票
    state_key = f'voted_{video_choice}'
    if state_key not in st.session_state:
        st.session_state[state_key] = False

    if st.session_state[state_key]:
        st.success("✅ 提交成功！老师已经收到你的想法啦。")
    else:
        st.markdown("### 第二步：请选择一个最符合的标签")
        
        # 使用两列布局显示四个按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button(config['labels'][0], key="btn0", use_container_width=True):
                save_vote(video_choice, 0)
                st.session_state[state_key] = True
                st.balloons()
                st.rerun()
            if st.button(config['labels'][1], key="btn1", use_container_width=True):
                save_vote(video_choice, 1)
                st.session_state[state_key] = True
                st.balloons()
                st.rerun()
        with col2:
            if st.button(config['labels'][2], key="btn2", use_container_width=True):
                save_vote(video_choice, 2)
                st.session_state[state_key] = True
                st.balloons()
                st.rerun()
            if st.button(config['labels'][3], key="btn3", use_container_width=True):
                save_vote(video_choice, 3)
                st.session_state[state_key] = True
                st.balloons()
                st.rerun()

# --- 页面 2: 监控后台 ---

def admin_page():
    st.title("📊 投票结果实时监控")
    
    col_header1, col_header2 = st.columns([3, 1])
    with col_header2:
        if st.button("🗑️ 清空所有数据", type="primary"):
            clear_all_data()
            st.warning("数据已清空！")
            st.rerun()

    df = load_data()
    
    # 循环生成四个视频的坐标系
    for vid in VIDEO_CONFIG:
        config = VIDEO_CONFIG[vid]
        st.markdown("---")
        st.subheader(f"📈 {config['name']} 的标签分布")
        
        fig = go.Figure()
        axis_range = 6
        
        # 绘制十字坐标轴
        fig.add_hline(y=0, line_width=2, line_color="black")
        fig.add_vline(x=0, line_width=2, line_color="black")
        
        # 定义四个角落的标签位置
        lbl = config['labels']
        annotations = [
            dict(x=4.5, y=4.5, text=lbl[0], showarrow=False, font=dict(size=20, color="black")),
            dict(x=-4.5, y=4.5, text=lbl[1], showarrow=False, font=dict(size=20, color="black")),
            dict(x=-4.5, y=-4.5, text=lbl[2], showarrow=False, font=dict(size=20, color="black")),
            dict(x=4.5, y=-4.5, text=lbl[3], showarrow=False, font=dict(size=20, color="black"))
        ]
        
        # 提取当前视频的投票并生成随机散点
        video_data = df[df['video_id'] == vid]
        points_x, points_y = [], []
        
        if not video_data.empty:
            for _, row in video_data.iterrows():
                kidx = int(row['label_idx'])
                # 根据象限随机生成坐标 (1-4范围)
                dirs = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
                qx, qy = dirs[kidx]
                points_x.append(qx * (1.5 + random.random() * 3))
                points_y.append(qy * (1.5 + random.random() * 3))
        
        # 绘制散点
        if points_x:
            fig.add_trace(go.Scatter(
                x=points_x, y=points_y,
                mode='markers',
                marker=dict(size=18, color=config['color'], line=dict(width=1.5, color='white')),
                name='投票点'
            ))

        # 设置图表样式：纯白背景
        fig.update_layout(
            width=800, height=600,
            paper_bgcolor='white', plot_bgcolor='white',
            xaxis=dict(range=[-axis_range, axis_range], showticklabels=False, showgrid=True, zeroline=False, gridcolor='#f0f0f0'),
            yaxis=dict(range=[-axis_range, axis_range], showticklabels=False, showgrid=True, zeroline=False, scaleanchor="x", scaleratio=1, gridcolor='#f0f0f0'),
            annotations=annotations,
            showlegend=False,
            margin=dict(l=10, r=10, t=30, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# --- 主程序入口 ---

def main():
    # 确保程序启动时数据文件已就绪
    init_data()
    
    st.sidebar.title("🧭 功能导航")
    page = st.sidebar.radio("请切换角色：", ["学生端", "后台监控方"])
    
    if page == "学生端":
        student_page()
    else:
        admin_page()

if __name__ == "__main__":
    main()
