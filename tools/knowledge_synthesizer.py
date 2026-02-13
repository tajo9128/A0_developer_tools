from python.helpers.tool import Tool, Response
from python.helpers.memory import Memory
import urllib.request
import re

class KnowledgeSynthesizer(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method or self.args.get("method")
        
        if method == "digest_url":
            url = self.args.get("url")
            if not url:
                return Response(message="Error: 'url' is required.", break_loop=False)
            
            try:
                headers = {"User-Agent": "Agent-Zero-Knowledge-Bot"}
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    html = response.read().decode('utf-8')
                
                # Very simple HTML strip for text
                text = re.sub(r'<[^>]+>', ' ', html)
                text = re.sub(r'\s+', ' ', text).strip()
                
                # Call utility model to summarize
                summary = await self.agent.call_utility_model(
                    system="Summarize the following technical content into a concise set of 'Best Practices' or 'Technical Reference' points for a coding agent.",
                    message=f"Content from {url}:\n\n{text[:5000]}", # Limit input
                    background=True
                )
                
                # Save to memory
                db = await Memory.get(self.agent)
                id = await db.insert_text(summary, {"source": url, "area": Memory.Area.MAIN.value, "type": "synthesized_knowledge"})
                
                return Response(message=f"Knowledge synthesized from {url} and saved to memory (ID: {id}).\n\nSummary:\n{summary}", break_loop=False)
            except Exception as e:
                return Response(message=f"Failed to digest URL: {str(e)}", break_loop=False)
        else:
            return Response(message=f"Unknown method '{method}'.", break_loop=False)
