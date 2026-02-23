# -*- coding: utf-8 -*-
import streamlit as st
import time

# ================= 页面基础配置 =================
st.set_page_config(page_title="Lite-Tutor Pro | 极客导师", page_icon="🤖", layout="wide")

# 初始化聊天历史状态
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好，极客！我是 Lite-Tutor。请在左侧选择我的运行模式，然后输入你的科学或工程问题。"}
    ]

# ================= 左侧控制面板 (Sidebar) =================
with st.sidebar:
    st.title("⚙️ 核心引擎控制台")
    st.markdown("---")
    
    # 核心卖点：三级自适应模式切换
    st.subheader("🔋 算力自适应模式")
    mode = st.radio(
        "选择导师运行状态：",
        ("Lite 模式 (纯文本云端)", "Standard 模式 (多模态交互)", "Pro 模式 (本地沙箱计算)"),
        index=2 # 默认选最硬核的 Pro
    )
    
    st.markdown("---")
    st.subheader("📊 诊断状态看板")
    if "Lite" in mode:
        st.info("当前状态：低功耗云端推理\n\n适合设备：老旧设备、无 GPU 终端\n\n优势：极致普惠教育")
    elif "Standard" in mode:
        st.success("当前状态：视听感官已唤醒\n\n接入：算能 OCR / 飞桨视觉引擎\n\n优势：支持拍照搜题与语音讲课")
    else:
        st.error("当前状态：物理机沙盒接管\n\n触发机制：MCP 原子化工具链\n\n优势：100% 零幻觉代码与数学推演")

# ================= 主战斗界面 (Chat Interface) =================
st.title("🪐 23.5°N Lite-Tutor 终端")
st.caption("基于端云架构的泛理科智能体导师 (GeekDay 2026 参赛版)")

# 渲染历史聊天记录
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 接收用户输入
if prompt := st.chat_input("向极客导师提问（例如：帮我画一个DFS算法的树状结构）..."):
    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 模拟导师思考与回复
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        # 这里先用简单的动画模拟思考过程，后续我们将在这里接入真实的后端逻辑
        full_response = ""
        mock_reply = f"**[系统识别为 {mode}]**: 收到指令！正在解析问题「{prompt}」。\n\n*(注意：当前为 UI 测试框架，我们的 ChromaDB 右脑与 OpenCode 沙盒接口即将挂载...)*"
        
        # 打字机特效展示
        for chunk in mock_reply.split(" "):
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})