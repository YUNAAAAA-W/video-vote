import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import random

# --- 配置 ---
DATA_FILE = 'video_votes.csv'

# 定义四个视频的配置（已去掉full_name）
VIDEO_CONFIG = {
    1: {
        "name": "视频一",
        "labels": ["水果", "助农", "贵州", "新鲜"],
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

# --- 辅助函数 ---
def init_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=['video_id', 'label_idx', 'timestamp'])
        df.to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE)

def save_vote(video_id, label_idx):
    df = load_data()
    new_row = {'video_id': video_id, 'label_idx': label_idx, 'timestamp': pd.Timestamp.now()}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def clear_all_data():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    init_data()

# --- 页面 1: 学生投票端（已去掉括号和full_name）---
def student_page():
    st.title("🎥 为视频选择标签")
    
    video_choice = st.selectbox(
        "第一步：请选择你观看的视频", 
        options=[1, 2, 3, 4],
        format_func=lambda x: VIDEO_CONFIG[x]['name']
    )
    
    config = VIDEO_CONFIG[video_choice]
    
    # 这里去掉了括号和full_name，只显示视频一/二/三/四
    st.markdown(f"### 你选择的是：{config['name']}")
    
    state_key = f'voted_{video_choice}'
    if state_key not in st.session_state:
        st.session_state[state_key] = False

    if st.session_state[state_key]:
        st.success("✅ 提交成功！感谢你的参与。")
    else:
        st.markdown("### 第二步：请选择一个最符合的标签")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(config['labels'][0], key=f"btn0", use_container_width=True):
                save_vote(video_choice, 0)
                st.session_state[state_key] = True
                st.balloons()
                st.rerun()
            if st.button(config['labels'][1], key=f"btn1", use_container_width=True):
                save_vote(video_choice, 1)
                st.session_state[state_key] = True
                st.balloons()
                st.rerun()
        with col2:
            if st.button(config['labels'][2], key=f"btn2", use_container_width=True):
                save_vote(video_choice, 2)
                st.session_state[state_key] = True
                st.balloons()
                st.rerun()
            if st.button(config['labels'][3], key=f"btn3", use_container_width=True):
                save_vote(video_choice, 3)
                st.session_state[state_key] = True
                st.balloons()
                st.rerun()

# --- 页面 2: 监控后台 ---
def admin_page():
    st.title("📊 后台监控中心")
    
    if st.button("🗑️ 清空所有数据", type="primary"):
        clear_all_data()
        st.warning("数据已清空！")
        st.rerun()

    df = load_data()
    
    for vid in VIDEO_CONFIG:
        config = VIDEO_CONFIG[vid]
        st.markdown(f"---")
        st.subheader(config['name'])
        
        fig = go.Figure()
        axis_range = 6
        
        # 绘制十字坐标轴
        fig.add_hline(y=0, line_width=2, line_color="black")
        fig.add_vline(x=0, line_width=2, line_color="black")
        
        # 添加四个角落的标签
        lbl = config['labels']
        annotations = [
            dict(x=axis_range*0.8, y=axis_range*0.8, text=lbl[0], showarrow=False, font=dict(size=22, color="black", family="Arial Black")),
            dict(x=-axis_range*0.8, y=axis_range*0.8, text=lbl[1], showarrow=False, font=dict(size=22, color="black", family="Arial Black")),
            dict(x=-axis_range*0.8, y=-axis_range*0.8, text=lbl[2], showarrow=False, font=dict(size=22, color="black", family="Arial Black")),
            dict(x=axis_range*0.8, y=-axis_range*0.8, text=lbl[3], showarrow=False, font=dict(size=22, color="black", family="Arial Black"))
        ]
        
        # 准备数据点
        video_data = df[df['video_id'] == vid]
        points_x = []
        points_y = []
        
        if not video_data.empty:
            for _, row in video_data.iterrows():
                kidx = int(row['label_idx'])
                dirs = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
                qx, qy = dirs[kidx]
                x = qx * (1 + random.random() * 3)
                y = qy * (1 + random.random() * 3)
                points_x.append(x)
                points_y.append(y)
        
        # 绘制圆点
        if points_x:
            fig.add_trace(go.Scatter(
                x=points_x, y=points_y,
                mode='markers',
                marker=dict(
                    size=18,
                    color=config['color'],
                    line=dict(width=2, color='white')
                ),
                name='投票'
            ))

        # 纯白背景设置
        fig.update_layout(
            width=800,
            height=600,
            paper_bgcolor='white',
            plot_bgcolor='white',
            xaxis=dict(range=[-axis_range, axis_range], showticklabels=False, showgrid=True, zeroline=False, gridcolor='#eeeeee'),
            yaxis=dict(range=[-axis_range, axis_range], showticklabels=False, showgrid=True, zeroline=False, scaleanchor="x", scaleratio=1, gridcolor='#eeeeee'),
            annotations=annotations,
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# --- 主程序入口 ---
def main():
    init_data()
    
    st.sidebar.title("🧭 导航")
    page = st.sidebar.radio("选择模式：", ["学生端", "后台监控方"])
    
    if page == "学生端":
        student_page()
    else:
        admin_page()

if __name__ == "__main__":
    main()
