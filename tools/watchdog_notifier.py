from python.helpers.tool import Tool, Response
from python.helpers import files
import os
import time

class WatchdogNotifier(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method or self.args.get("method", "check")
        path = self.args.get("path", ".")
        
        abs_path = files.get_abs_path(path)
        state_file = os.path.join(files.get_base_dir(), ".watchdog_state.json")
        
        if method == "check":
            # Very simple mtime-based check for files in the directory
            changed = []
            try:
                # Load last state
                last_check = 0
                if os.path.exists(state_file):
                    with open(state_file, "r") as f:
                        import json
                        last_check = json.load(f).get("last_check", 0)
                
                current_time = time.time()
                for root, _, filenames in os.walk(abs_path):
                    if any(x in root for x in [".git", "node_modules"]): continue
                    for filename in filenames:
                        fpath = os.path.join(root, filename)
                        if os.path.getmtime(fpath) > last_check:
                            changed.append(os.path.relpath(fpath, abs_path))
                
                # Save state
                with open(state_file, "w") as f:
                    import json
                    json.dump({"last_check": current_time}, f)
                    
                if not changed:
                    return Response(message="No files have changed since the last check.", break_loop=False)
                else:
                    return Response(message=f"The following files have changed:\n" + "\n".join(changed), break_loop=False)
            except Exception as e:
                return Response(message=f"Watchdog error: {str(e)}", break_loop=False)
        else:
            return Response(message="Unknown watchdog method. Use 'check'.", break_loop=False)
