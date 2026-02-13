from python.helpers.tool import Tool, Response
from python.helpers import runtime
import subprocess
import os

class DepManager(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method or self.args.get("method")
        package = self.args.get("package")
        manager = self.args.get("manager", "pip").lower()

        if method == "install":
            if not package:
                return Response(message="Error: 'package' argument is required for install.", break_loop=False)

            command = []
            if manager == "pip":
                command = ["pip", "install", package]
            elif manager == "npm":
                command = ["npm", "install", package]
            else:
                return Response(message=f"Error: Unsupported manager '{manager}'. Use 'pip' or 'npm'.", break_loop=False)
            try:
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                return Response(message=f"Successfully installed {package} via {manager}.\n\nOutput:\n{result.stdout}", break_loop=False)
            except subprocess.CalledProcessError as e:
                return Response(message=f"Failed to install {package} via {manager}.\n\nError:\n{e.stderr}", break_loop=False)
        elif method == "list":
            command = ["pip", "list"] if manager == "pip" else ["npm", "list", "--depth=0"]
            try:
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                return Response(message=f"Installed dependencies ({manager}):\n\n{result.stdout}", break_loop=False)
            except subprocess.CalledProcessError as e:
                return Response(message=f"Failed to list dependencies via {manager}.\n\nError:\n{e.stderr}", break_loop=False)
        else:
            return Response(message=f"Error: Unknown method '{method}'. Valid methods are: install, list.", break_loop=False)
