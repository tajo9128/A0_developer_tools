from python.helpers.tool import Tool, Response
from python.helpers import files
import os
class ContextManager(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method or self.args.get("method")
        
        # This tool interacts with the agent's memory/history
        # In Agent Zero, "pinning" is effectively adding extra context to the LoopData
        
        if method == "pin_file":
            path = self.args.get("path")
            if not path:
                return Response(message="Error: 'path' argument is required.", break_loop=False)
            
            try:
                content = files.read_file(path)
                # Store in persistent extras so it persists across iterations in this conversation
                if self.loop_data:
                    self.loop_data.extras_persistent[f"pinned_{path}"] = f"--- Pinned File: {path} ---\n{content}\n"
                return Response(message=f"File '{path}' pinned to context.", break_loop=False)
            except Exception as e:
                return Response(message=f"Error pinning file: {str(e)}", break_loop=False)
        elif method == "unpin_file":
            path = self.args.get("path")
            if self.loop_data and f"pinned_{path}" in self.loop_data.extras_persistent:
                del self.loop_data.extras_persistent[f"pinned_{path}"]
                return Response(message=f"File '{path}' unpinned.", break_loop=False)
            return Response(message=f"File '{path}' was not pinned.", break_loop=False)
        elif method == "summarize":
            # Just a hint for the agent to use its own reasoning to summarize
            return Response(message="Please provide a concise summary of the current task and progress to stay within token limits.", break_loop=False)
        else:
            return Response(message=f"Error: Unknown method '{method}'.", break_loop=False)
