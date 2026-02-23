# -*- coding: utf-8 -*-
import streamlit as st
import time
import requests

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
    backend_url = st.text_input("后端地址", value="http://127.0.0.1:8000")
    
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
        full_response = ""
        if "Pro" in mode:
            try:
                resp = requests.post(
                    f"{backend_url.rstrip('/')}/solve",
                    json={"task_instruction": prompt},
                    timeout=30
                )
                if resp.ok:
                    data = resp.json()
                    status = data.get("status")
                    solution = data.get("solution", "")
                    if status:
                        full_response = f"**[系统识别为 {mode}]**: 状态 {status}\n\n{solution}"
                    else:
                        full_response = f"**[系统识别为 {mode}]**: {solution}"
                else:
                    full_response = f"**[系统识别为 {mode}]**: /solve 请求失败，HTTP {resp.status_code}"
            except Exception as e:
                full_response = f"**[系统识别为 {mode}]**: /solve 调用失败：{e}"
        else:
            try:
                resp = requests.post(
                    f"{backend_url.rstrip('/')}/search",
                    json={"query": prompt},
                    timeout=30
                )
                if resp.ok:
                    data = resp.json()
                    status = data.get("status")
                    context = data.get("context", "")
                    if context:
                        if status:
                            full_response = f"**[系统识别为 {mode}]**: 状态 {status}\n\n{context}"
                        else:
                            full_response = f"**[系统识别为 {mode}]**:\n\n{context}"
                    else:
                        if status:
                            full_response = f"**[系统识别为 {mode}]**: 状态 {status}\n\n未检索到有效上下文。"
                        else:
                            full_response = f"**[系统识别为 {mode}]**: 未检索到有效上下文。"
                else:
                    full_response = f"**[系统识别为 {mode}]**: /search 请求失败，HTTP {resp.status_code}"
            except Exception as e:
                full_response = f"**[系统识别为 {mode}]**: /search 调用失败：{e}"
        
        display_text = ""
        for chunk in full_response.split(" "):
            display_text += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(display_text + "▌")
        message_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
