import os
import subprocess
import re
import uuid
from collections import Counter
from typing import Optional, Dict, Any, List
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from rag_builder import LocalRAGKnowledgeBase
from edge_tool import get_tool_schemas

class UTF8JSONResponse(JSONResponse):
    media_type = "application/json; charset=utf-8"

app = FastAPI(title="LiteTutor Edge Node", default_response_class=UTF8JSONResponse)

def _tokenize(text: str) -> List[str]:
    return [t for t in re.split(r"[^a-zA-Z0-9\u4e00-\u9fff]+", text.lower()) if len(t) > 1]

def _extract_keywords(text: str, limit: int = 4) -> List[str]:
    tokens = _tokenize(text)
    if not tokens:
        return []
    counts = Counter(tokens)
    return [w for w, _ in counts.most_common(limit)]

tutor_sessions: Dict[str, Dict[str, Any]] = {}

print("Waking up Right Brain (ChromaDB)...")
rag_db = LocalRAGKnowledgeBase()

class TaskRequest(BaseModel):
    task_instruction: Optional[str] = None
    code: Optional[str] = None
    language: str = "python"
    timeout: int = 20

@app.post("/solve")
async def receive_task(request: TaskRequest):
    if request.code and request.code.strip():
        if request.language.lower() != "python":
            return {"status": "error", "message": "Only python is supported for code execution."}
        try:
            result = subprocess.run(
                ["python", "-c", request.code],
                capture_output=True,
                text=True,
                timeout=request.timeout
            )
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    if request.task_instruction and request.task_instruction.strip():
        instruction = request.task_instruction
        print("\n" + "="*60)
        print(f"[TASK RECEIVED] Instruction: {instruction}")
        try:
            print("Waking up OpenCode Native UI (Fire-and-Forget Mode)...")
            full_command = f'opencode --prompt "{instruction}"'
            subprocess.Popen(full_command, shell=True)
            return {
                "status": "success", 
                "solution": "[Task dispatched successfully. Execution output is rendering natively on the Edge Node physical screen.]"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    return {"status": "error", "message": "Either task_instruction or code must be provided."}

class SearchRequest(BaseModel):
    query: str
    mode: str = "hybrid"
    n_results: int = 2

@app.post("/search")
async def search_knowledge(req: SearchRequest):
    print("\n" + "="*60)
    print(f"[SEARCH RECEIVED] Query: {req.query}")
    try:
        if req.mode.lower() == "vector":
            retrieved_context = rag_db.query_knowledge(req.query, n_results=req.n_results)
        else:
            retrieved_context = rag_db.query_knowledge_hybrid(req.query, n_results=req.n_results)
        print(f"[SEARCH RESULT] Found {len(retrieved_context)} characters of context.")
        return {
            "status": "success", 
            "context": retrieved_context
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/tools")
async def list_tools():
    public_url = os.getenv("EDGE_PUBLIC_URL", "http://127.0.0.1:8000").strip()
    tools = get_tool_schemas(public_url)
    return {"status": "success", "tools": tools}

class TutorRequest(BaseModel):
    session_id: Optional[str] = None
    user_input: str

@app.post("/tutor")
async def tutor_fsm(req: TutorRequest):
    session_id = req.session_id or str(uuid.uuid4())
    state = tutor_sessions.get(session_id)
    if not state:
        state = {
            "stage": "diagnose",
            "question": req.user_input.strip(),
            "context": "",
            "keywords": []
        }
        tutor_sessions[session_id] = state

    stage = state["stage"]
    if stage == "diagnose":
        response = (
            f"我先做诊断：你正在处理的问题是「{state['question']}」。"
            "请补充你目前的解题进度或卡住点。"
        )
        state["stage"] = "explain"
        return {"status": "success", "session_id": session_id, "stage": "diagnose", "response": response}

    if stage == "explain":
        context = rag_db.query_knowledge_hybrid(state["question"], n_results=2)
        state["context"] = context
        keywords = _extract_keywords(context)
        state["keywords"] = keywords
        response = (
            "启发讲解如下：\n\n"
            f"{context}\n\n"
            "如果理解了，请回答“继续测验”。"
        )
        state["stage"] = "quiz"
        return {"status": "success", "session_id": session_id, "stage": "explain", "response": response}

    if stage == "quiz":
        keywords = state.get("keywords", [])
        if keywords:
            prompt = "请用一句话解释以下关键词并至少覆盖其中两个： " + "、".join(keywords)
        else:
            prompt = "请用一句话总结你对该问题的理解。"
        state["stage"] = "validate"
        return {"status": "success", "session_id": session_id, "stage": "quiz", "response": prompt}

    if stage == "validate":
        keywords = state.get("keywords", [])
        answer = req.user_input.strip()
        answer_lower = answer.lower()
        hit = [k for k in keywords if k in answer_lower]
        if keywords and len(hit) >= 1:
            result = "校验通过"
        elif not keywords and len(answer) >= 6:
            result = "校验通过"
        else:
            result = "校验未通过"
        response = f"{result}。如果需要，我可以继续补充讲解或出新题。"
        state["stage"] = "complete"
        return {"status": "success", "session_id": session_id, "stage": "validate", "response": response, "matched_keywords": hit}

    response = "本轮已完成。如需继续，请提交新问题。"
    return {"status": "success", "session_id": session_id, "stage": "complete", "response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
