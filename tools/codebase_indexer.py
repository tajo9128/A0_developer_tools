from python.helpers.tool import Tool, Response
from python.helpers import files
import os
import re
import json
class CodebaseIndexer(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method or self.args.get("method", "index")
        base_dir = files.get_base_dir()
        index_file = os.path.join(base_dir, ".agent_zero_index.json")
        if method == "index":
            index = {"files": {}, "symbols": {}}
            for root, _, filenames in os.walk(base_dir):
                if any(x in root for x in [".git", "node_modules", "__pycache__", "venv", ".gemini"]):
                    continue
                for filename in filenames:
                    if not filename.endswith((".py", ".js", ".ts", ".html")):
                        continue
                    
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, base_dir)
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # Extract classes and functions
                        matches = re.finditer(r"^\s*(class|def|function|async\s+def)\s+([a-zA-Z_][a-zA-Z0-9_]*)", content, re.MULTILINE)
                        file_symbols = []
                        for match in matches:
                            sym_type, sym_name = match.groups()
                            file_symbols.append({"name": sym_name, "type": sym_type, "line": content.count("\n", 0, match.start()) + 1})
                            
                            if sym_name not in index["symbols"]:
                                index["symbols"][sym_name] = []
                            index["symbols"][sym_name].append(rel_path)
                            
                        index["files"][rel_path] = {"symbols": file_symbols}
                    except Exception:
                        continue
            
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(index, f, indent=2)
            
            return Response(message=f"Codebase indexed successfully. Indexed {len(index['files'])} files and {len(index['symbols'])} symbols.", break_loop=False)
        elif method == "lookup":
            symbol = self.args.get("symbol")
            if not symbol:
                return Response(message="Error: 'symbol' argument is required.", break_loop=False)
            
            if not os.path.exists(index_file):
                return Response(message="Error: Index file not found. Please run 'index' first.", break_loop=False)
            
            with open(index_file, "r", encoding="utf-8") as f:
                index = json.load(f)
            
            locations = index["symbols"].get(symbol, [])
            if not locations:
                return Response(message=f"Symbol '{symbol}' not found in index.", break_loop=False)
            
            return Response(message=f"Symbol '{symbol}' found in:\n" + "\n".join(locations), break_loop=False)
        else:
            return Response(message=f"Error: Unknown method '{method}'.", break_loop=False)
