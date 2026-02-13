from python.helpers.tool import Tool, Response
from python.helpers import files
import subprocess
import os

class Linter(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method or self.args.get("method")
        path = self.args.get("path", ".")
        tool = self.args.get("tool", "ruff").lower()

        abs_path = files.get_abs_path(path)

        if method == "check":
            command = []
            if tool == "ruff":
                command = ["ruff", "check", abs_path]
            elif tool == "flake8":
                command = ["flake8", abs_path]
            elif tool == "black":
                command = ["black", "--check", abs_path]
            else:
                return Response(message=f"Error: Unsupported tool '{tool}'. Use 'ruff', 'flake8', or 'black'.", break_loop=False)
            try:
                result = subprocess.run(command, capture_output=True, text=True)
                if result.returncode == 0:
                    return Response(message=f"Lint check ({tool}) passed for '{path}'.", break_loop=False)
                else:
                    return Response(message=f"Lint errors found ({tool}):\n\n{result.stdout}\n{result.stderr}", break_loop=False)
            except FileNotFoundError:
                return Response(message=f"Error: Tool '{tool}' not found. Please install it first using dep_manager.", break_loop=False)
            except Exception as e:
                return Response(message=f"Error during linting: {str(e)}", break_loop=False)
        elif method == "fix":
            command = []
            if tool == "ruff":
                command = ["ruff", "check", "--fix", abs_path]
            elif tool == "black":
                command = ["black", abs_path]
            else:
                return Response(message=f"Error: Tool '{tool}' does not support auto-fix via this tool. Use 'ruff' or 'black'.", break_loop=False)
            try:
                result = subprocess.run(command, capture_output=True, text=True)
                return Response(message=f"Applied auto-fixes using {tool} on '{path}'.\n\nOutput:\n{result.stdout}", break_loop=False)
            except Exception as e:
                return Response(message=f"Error during auto-fix: {str(e)}", break_loop=False)
        else:
            return Response(message=f"Error: Unknown method '{method}'. Valid methods are: check, fix.", break_loop=False)
