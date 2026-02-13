from python.helpers.tool import Tool, Response
from python.helpers import files
import os
import re
class RefactorTool(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method or self.args.get("method")
        
        if method == "rename_symbol":
            old = self.args.get("old")
            new = self.args.get("new")
            path = self.args.get("path", ".")
            
            if not old or not new:
                return Response(message="Error: 'old' and 'new' are required.", break_loop=False)
            
            abs_path = files.get_abs_path(path)
            count = 0
            for root, _, filenames in os.walk(abs_path):
                if ".git" in root: continue
                for filename in filenames:
                    if not filename.endswith((".py", ".js", ".html")): continue
                    fpath = os.path.join(root, filename)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            content = f.read()
                        if old in content:
                            new_content = content.replace(old, new)
                            with open(fpath, "w", encoding="utf-8") as f:
                                f.write(new_content)
                            count += 1
                    except: continue
            
            return Response(message=f"Renamed '{old}' to '{new}' in {count} files.", break_loop=False)
        else:
            return Response(message=f"Error: Unknown method '{method}'.", break_loop=False)
