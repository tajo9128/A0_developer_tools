from python.helpers.tool import Tool, Response
import subprocess
import os

class IacOps(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method or self.args.get("method")
        
        if method == "docker_manage":
            action = self.args.get("action", "ps") # ps, up, down, restart
            service = self.args.get("service", "")
            
            cmd = ["docker-compose", action]
            if service: cmd.append(service)
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                return Response(message=f"Docker Compose ({action}):\n\n{result.stdout}\n{result.stderr}", break_loop=False)
            except Exception as e:
                return Response(message=f"Docker action failed: {str(e)}", break_loop=False)
        elif method == "env_check":
            required = self.args.get("required", "").split(",")
            missing = [env for env in required if env.strip() and not os.environ.get(env.strip())]
            
            if not missing:
                return Response(message="All required environment variables are set.", break_loop=False)
            else:
                return Response(message=f"Missing environment variables: {', '.join(missing)}", break_loop=False)
        else:
            return Response(message=f"Unknown method '{method}'.", break_loop=False)
