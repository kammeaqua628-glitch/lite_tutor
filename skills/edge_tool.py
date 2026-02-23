import requests
import json
from typing import Dict, Any

class EdgeComputeTool:
    """
    Atomized tool for local physical sandbox execution.
    Compliant with basic Agent Tool interface standards.
    """
    
    def __init__(self, cpolar_url: str):
        # Dynamically bind the dynamic Cpolar URL
        self.api_url = f"{cpolar_url.rstrip('/')}/solve"
        self.name = "edge_compute_sandbox"
        self.description = (
            "Execute complex math, physics, or coding tasks in a secure local physical sandbox. "
            "Use this ONLY when deterministic calculation or code execution is required. "
            "Do NOT use this for general knowledge queries."
        )

    def get_tool_schema(self) -> Dict[str, Any]:
        """
        Returns the JSON Schema of the tool, ready to be injected into DeepSeek/OpenAI APIs.
        This is the core of Function Calling / MCP.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_instruction": {
                            "type": "string",
                            "description": "The natural language instruction or math problem for the physical machine to solve (e.g., 'Calculate 2^10')."
                        }
                    },
                    "required": ["task_instruction"]
                }
            }
        }

    def execute(self, task_instruction: str) -> str:
        """
        The actual execution engine of the tool.
        Fires the POST request to the Edge Node.
        """
        print(f"\n[TOOL TRIGGERED] Name: {self.name} | Payload: {task_instruction}")
        headers = {"Content-Type": "application/json"}
        payload = {"task_instruction": task_instruction}
        
        try:
            # Fire-and-forget request with a short timeout to prevent blocking the LLM
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return f"Tool Execution Status: {data.get('status')}. Receipt: {data.get('solution')}"
            else:
                return f"Tool Execution Failed with status code: {response.status_code}"
                
        except Exception as e:
            return f"Tool Execution Error (Edge node might be offline): {str(e)}"

# Quick Local Test Block
if __name__ == "__main__":
    # Replace with your current active Cpolar URL
    TEST_CPOLAR_URL = "https://4ee5dca5.r6.cpolar.top" 
    
    # Initialize the weapon
    sandbox_tool = EdgeComputeTool(TEST_CPOLAR_URL)
    
    # Check the schema (What the LLM sees)
    print("--- Tool Schema (For LLM) ---")
    print(json.dumps(sandbox_tool.get_tool_schema(), indent=2))
    
    # Pull the trigger (What happens when the LLM calls it)
    print("\n--- Testing Execution ---")
    result = sandbox_tool.execute("Write a Python code to calculate 2 to the power of 10 and print GeekDay")
    print(f"Return to LLM:\n{result}")