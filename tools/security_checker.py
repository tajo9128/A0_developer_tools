from python.helpers.tool import Tool, Response
from python.helpers import files
import subprocess
import os
import re

class SecurityChecker(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method or self.args.get("method")
        path = self.args.get("path", ".")
        abs_path = files.get_abs_path(path)
        
        if method == "audit":
            # Check Python dependencies
            if os.path.exists(os.path.join(abs_path, "requirements.txt")):
                try:
                    # 'safety' needs to be installed via dep_manager
                    result = subprocess.run(["safety", "check", "-r", os.path.join(abs_path, "requirements.txt")], capture_output=True, text=True)
                    return Response(message=f"Python Security Audit:\n\n{result.stdout or 'No issues found.'}", break_loop=False)
                except FileNotFoundError:
                    return Response(message="Error: 'safety' tool not found. Install it with dep_manager: `pip install safety`", break_loop=False)
            
            # Check Node dependencies
            elif os.path.exists(os.path.join(abs_path, "package.json")):
                result = subprocess.run(["npm", "audit"], capture_output=True, text=True, cwd=abs_path)
                return Response(message=f"Node Security Audit:\n\n{result.stdout}", break_loop=False)
            
            return Response(message="No requirements.txt or package.json found for auditing.", break_loop=False)
        elif method == "scan_secrets":
            secret_patterns = {
                "API Key": r"(?:key|api|token|secret|pwd|password)[-_a-z0-9]{0,20}\s*[:=]\s*['\"]([a-z0-9]{16,})['\"]",
                "Generic Token": r"[a-z0-9]{32,}",
            }
            
            findings = []
            for root, _, filenames in os.walk(abs_path):
                if any(x in root for x in [".git", "node_modules", "venv", "__pycache__"]): continue
                for filename in filenames:
                    fpath = os.path.join(root, filename)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            content = f.read()
                        for p_name, pattern in secret_patterns.items():
                            if re.search(pattern, content, re.IGNORECASE):
                                findings.append(f"Potential {p_name} found in: {os.path.relpath(fpath, abs_path)}")
                    except: continue
            
            return Response(message="Secret Scan Results:\n\n" + ("\n".join(findings) or "No clear secrets found in source code."), break_loop=False)
        else:
            return Response(message=f"Unknown method '{method}'. Use 'audit' or 'scan_secrets'.", break_loop=False)
