from python.helpers.tool import Tool, Response
from python.helpers.memory import Memory
from python.helpers.dirty_json import DirtyJson
import json

class MemoryReflect(Tool):
    async def execute(self, **kwargs) -> Response:
        # 1. Gather chat history
        # Agent Zero usually keeps history in self.agent.history
        history = self.agent.history
        if not history:
            return Response(message="No chat history found to reflect upon.", break_loop=False)
        # 2. Call LLM to extract "Solutions" or "Patterns"
        system_prompt = "You are a 'System 2' memory processor for an AI agent. Analyze the provided chat history and extract any generalizable lessons, optimized code patterns, or business logic discovered during this session. Ignore transient errors or simple typos. Focus on things that will be useful in future, different sessions. Return a list of concise 'Solution Memories'."
        
        # Format history for LLM
        history_text = ""
        for msg in history[-10:]: # Look at the last 10 messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            history_text += f"{role.upper()}: {content}\n\n"
        try:
            reflection_response = await self.agent.call_utility_model(
                system=system_prompt,
                message=f"Chat History:\n{history_text}",
                background=True
            )
            # 3. Save as Solutions
            db = await Memory.get(self.agent)
            
            # We assume the response is a string or list of items. 
            # If it's markdown with multiple points, we'll save it as one high-quality solution.
            metadata = {
                "area": Memory.Area.SOLUTIONS.value,
                "type": "reflection",
                "session_id": self.agent.agent_id
            }
            
            id = await db.insert_text(reflection_response, metadata)
            
            return Response(message=f"Successfully reflected on history and saved a new solution memory (ID: {id}).\n\nReflection Summary:\n{reflection_response[:500]}...", break_loop=False)
        except Exception as e:
            return Response(message=f"Reflection failed: {str(e)}", break_loop=False)
