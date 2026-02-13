from python.helpers.tool import Tool, Response
from python.helpers import files
import subprocess
import os
import time

class PerfProfiler(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method or self.args.get("method")
        command = self.args.get("command")
        
        if method == "profile":
            if not command:
                return Response(message="Error: 'command' (e.g., 'python script.py') is required for profiling.", break_loop=False)
            
            # Use cProfile to profile a Python command
            if command.startswith("python"):
                profile_cmd = command.replace("python", "python -m cProfile -s cumulative")
                try:
                    result = subprocess.run(profile_cmd, shell=True, capture_output=True, text=True, timeout=30)
                    return Response(message=f"Performance Profile Result:\n\n{result.stdout[:2000]}", break_loop=False)
                except Exception as e:
                    return Response(message=f"Profiling failed: {str(e)}", break_loop=False)
            
            return Response(message="Only Python profiling is supported currently via cProfile.", break_loop=False)
        elif method == "bench":
            # Simple timing of a shell command
            if not command:
                return Response(message="Error: 'command' is required for benchmarking.", break_loop=False)
            
            start = time.time()
            try:
                subprocess.run(command, shell=True, capture_output=True, check=True)
                end = time.time()
                return Response(message=f"Benchmark: '{command}' took {end - start:.4f} seconds.", break_loop=False)
            except Exception as e:
                return Response(message=f"Benchmark failed: {str(e)}", break_loop=False)
        else:
            return Response(message=f"Unknown method '{method}'. Use 'profile' or 'bench'.", break_loop=False)
