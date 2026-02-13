from python.helpers.tool import Tool, Response
import urllib.request
import json

class ApiExplorer(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method or self.args.get("method")
        url = self.args.get("url")
        
        if not url:
            return Response(message="Error: 'url' is required.", break_loop=False)
            
        if method == "discover":
            common_paths = [
                "/swagger.json", "/openapi.json", "/v1/swagger.json", 
                "/api/docs", "/swagger/index.html", "/health"
            ]
            findings = []
            for path in common_paths:
                test_url = url.rstrip("/") + path
                try:
                    req = urllib.request.Request(test_url, method="HEAD")
                    with urllib.request.urlopen(req, timeout=3) as response:
                        if response.status == 200:
                            findings.append(f"Found: {test_url}")
                except:
                    continue
            
            return Response(message="API Discovery Results:\n\n" + ("\n".join(findings) or "No standard definition files found at common paths."), break_loop=False)
        elif method == "read_spec":
            try:
                with urllib.request.urlopen(url, timeout=5) as response:
                    content = response.read().decode("utf-8")
                # If it's JSON, pretty print it
                try:
                    data = json.loads(content)
                    content = json.dumps(data, indent=2)
                except: pass
                
                return Response(message=f"API Specification from {url}:\n\n{content[:3000]}", break_loop=False)
            except Exception as e:
                return Response(message=f"Failed to read API spec: {str(e)}", break_loop=False)
        else:
            return Response(message="Unknown method. Use 'discover' or 'read_spec'.", break_loop=False)
