# -*- coding: utf-8 -*-
import streamlit as st
import time
import json
import requests

st.set_page_config(page_title="Lite-Tutor Pro | 极客导师", page_icon="🤖", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好，极客！我是 Lite-Tutor。请在左侧选择我的运行模式，然后输入你的科学或工程问题。"}
    ]

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "你是 Lite-Tutor，一名泛理科智能体导师。请用简洁、结构化的中文回答。"

st.markdown(
    """
<style>
    .stApp { background: radial-gradient(1200px 800px at 10% 10%, #0b1220 0%, #04070d 45%, #020308 100%); color: #e8f0ff; }
    .block-container { padding-top: 1.2rem; }
    h1, h2, h3, h4 { color: #e8f0ff; text-shadow: 0 0 12px rgba(90, 170, 255, 0.35); }
    .neon-card { background: rgba(10, 18, 35, 0.7); border: 1px solid rgba(90, 170, 255, 0.35); border-radius: 14px; padding: 14px 16px; box-shadow: 0 0 20px rgba(40, 90, 200, 0.18); }
    .hud { font-family: "Segoe UI", "SF Pro Text", sans-serif; letter-spacing: 0.2px; }
    .stTextInput > div > div > input, .stTextArea > div > textarea { background: rgba(7, 12, 24, 0.8); color: #dbe6ff; border: 1px solid rgba(90, 170, 255, 0.4); }
    .stChatMessage { background: rgba(6, 10, 20, 0.65); border: 1px solid rgba(90, 170, 255, 0.25); border-radius: 12px; }
</style>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.title("⚙️ 战情室控制台")
    st.markdown("---")
    openclaw_url = st.text_input("OpenClaw Base URL", value="https://your-openclaw-host/v1")
    edge_url = st.text_input("Edge Node URL", value="http://127.0.0.1:8000")
    api_key = st.text_input("API Key", type="password")
    model_name = st.text_input("Model", value="deepseek-chat")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.5, value=0.6, step=0.1)
    max_tokens = st.slider("Max Tokens", min_value=128, max_value=4096, value=1024, step=64)
    st.text_area("System Prompt", key="system_prompt", height=120)

    st.markdown("---")
    st.subheader("🔋 算力自适应模式")
    mode = st.radio(
        "选择导师运行状态：",
        ("Lite 模式 (纯文本云端)", "Standard 模式 (多模态交互)", "Pro 模式 (本地沙箱计算)"),
        index=1
    )
    
    st.markdown("---")
    st.subheader("📊 诊断状态看板")
    if "Lite" in mode:
        st.info("当前状态：低功耗云端推理\n\n适合设备：老旧设备、无 GPU 终端\n\n优势：极致普惠教育")
    elif "Standard" in mode:
        st.success("当前状态：视听感官已唤醒\n\n接入：算能 OCR / 飞桨视觉引擎\n\n优势：支持拍照搜题与语音讲课")
    else:
        st.error("当前状态：物理机沙盒接管\n\n触发机制：MCP 原子化工具链\n\n优势：100% 零幻觉代码与数学推演")

header_left, header_right = st.columns([3, 2], vertical_alignment="center")
with header_left:
    st.title("🛰️ Lite-Tutor 战情室")
    st.caption("端云双脑协同 | OpenClaw 路由 | 本地物理算力")
with header_right:
    status = "就绪" if openclaw_url.strip() else "未配置"
    st.markdown(
        f"""
        <div class="neon-card hud">
            <div>连接状态：{status}</div>
            <div>当前模式：{mode}</div>
            <div>模型：{model_name}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(" ")
st.subheader("🧭 任务对话")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

def _fetch_edge_tools(base_url: str):
    try:
        resp = requests.get(f"{base_url.rstrip('/')}/tools", timeout=8)
        if resp.ok:
            data = resp.json()
            return data.get("tools", [])
    except Exception:
        return []
    return []

def _call_edge_tool(base_url: str, name: str, arguments: dict):
    try:
        if name == "edge_compute_sandbox":
            payload = {
                "task_instruction": arguments.get("task_instruction", ""),
                "code": arguments.get("code", ""),
                "language": arguments.get("language", "python"),
                "timeout": arguments.get("timeout", 20)
            }
            resp = requests.post(f"{base_url.rstrip('/')}/solve", json=payload, timeout=20)
            if resp.ok:
                return json.dumps(resp.json(), ensure_ascii=False)
            return f"Tool execution failed: HTTP {resp.status_code}"
        if name == "edge_knowledge_rag":
            payload = {
                "query": arguments.get("query", ""),
                "mode": "hybrid",
                "n_results": 2
            }
            resp = requests.post(f"{base_url.rstrip('/')}/search", json=payload, timeout=20)
            if resp.ok:
                return json.dumps(resp.json(), ensure_ascii=False)
            return f"Tool execution failed: HTTP {resp.status_code}"
        return f"Unknown tool: {name}"
    except Exception as e:
        return f"Tool execution error: {e}"

if prompt := st.chat_input("向极客导师提问（例如：帮我画一个DFS算法的树状结构）..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        if not openclaw_url.strip():
            full_response = "OpenClaw Base URL 未配置。"
        else:
            messages = []
            if st.session_state.system_prompt.strip():
                messages.append({"role": "system", "content": st.session_state.system_prompt.strip()})
            messages.extend(st.session_state.messages)
            headers = {"Content-Type": "application/json"}
            if api_key.strip():
                headers["Authorization"] = f"Bearer {api_key.strip()}"
            tools = []
            if "Pro" in mode and edge_url.strip():
                tools = _fetch_edge_tools(edge_url)
            payload = {
                "model": model_name.strip(),
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
            }
            if tools:
                payload["tools"] = tools
                payload["tool_choice"] = "auto"
            endpoint = f"{openclaw_url.rstrip('/')}/chat/completions"
            try:
                resp = requests.post(endpoint, json=payload, headers=headers, timeout=60)
                if resp.ok:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices and "message" in choices[0]:
                        message = choices[0]["message"]
                        tool_calls = message.get("tool_calls", [])
                        if tool_calls and tools:
                            messages.append(message)
                            for call in tool_calls:
                                name = call.get("function", {}).get("name", "")
                                raw_args = call.get("function", {}).get("arguments", "{}")
                                try:
                                    args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                                except Exception:
                                    args = {}
                                result = _call_edge_tool(edge_url, name, args)
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": call.get("id", ""),
                                    "name": name,
                                    "content": result
                                })
                            payload["messages"] = messages
                            follow = requests.post(endpoint, json=payload, headers=headers, timeout=60)
                            if follow.ok:
                                follow_data = follow.json()
                                follow_choices = follow_data.get("choices", [])
                                if follow_choices and "message" in follow_choices[0]:
                                    full_response = follow_choices[0]["message"].get("content", "")
                                else:
                                    full_response = "OpenClaw 返回内容为空。"
                            else:
                                full_response = f"OpenClaw 请求失败，HTTP {follow.status_code}"
                        else:
                            full_response = message.get("content", "")
                    else:
                        full_response = "OpenClaw 返回内容为空。"
                else:
                    full_response = f"OpenClaw 请求失败，HTTP {resp.status_code}"
            except Exception as e:
                full_response = f"OpenClaw 调用失败：{e}"
        
        display_text = ""
        for chunk in full_response.split(" "):
            display_text += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(display_text + "▌")
        message_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
