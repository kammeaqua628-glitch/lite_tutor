'''
import subprocess
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
app = FastAPI(title="LiteTutor Edge Node")

class TaskRequest(BaseModel):
    task_instruction: str


@app.post("/solve")
async def receive_task(request: TaskRequest):
    instruction = request.task_instruction
    print("\n" + "="*60)
    print(f"[TASK RECEIVED] Instruction: {instruction}")
    print("="*60)
   
    try:
        print("Running OpenCode engine (Interactive Mode)...")
        # Using the correct prompt argument without capturing output
        full_command = f'opencode --prompt "{instruction}"'
        # This allows the UI or terminal output to display directly
        process = subprocess.run(
            full_command,
            shell=True
        )
        if process.returncode == 0:
            status = "completed"
            result_output = "Task executed directly. Please check the local screen or UI."
            print("[DONE] Execution successful.")
        else:
            status = "failed"
            result_output = f"Failed with CODE: {process.returncode}"
            print(f"[ERROR] Code {process.returncode}")
        return {
            "status": status,
            "solution": result_output
        }

    except Exception as e:
        print(f"[SYSTEM ERROR] {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

import subprocess
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="LiteTutor Edge Node")

class TaskRequest(BaseModel):
    task_instruction: str

@app.post("/solve")
async def receive_task(request: TaskRequest):
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

from rag_builder import LocalRAGKnowledgeBase

print("Waking up Right Brain (ChromaDB)...")
rag_db = LocalRAGKnowledgeBase()

class SearchRequest(BaseModel):
    query: str

@app.post("/search")
async def search_knowledge(req: SearchRequest):
    print("\n" + "="*60)
    print(f"[SEARCH RECEIVED] Query: {req.query}")
    try:
        retrieved_context = rag_db.query_knowledge(req.query) 
        print(f"[SEARCH RESULT] Found {len(retrieved_context)} characters of context.")
        
        return {
            "status": "success", 
            "context": retrieved_context
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)