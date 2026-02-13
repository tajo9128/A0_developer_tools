from python.helpers.memory import Memory
from python.helpers.tool import Tool, Response

class MemoryQuery(Tool):
    async def execute(self, **kwargs) -> Response:
        query = self.args.get("text", "")
        area = self.args.get("area", "") # Optional: main, fragments, solutions, instruments
        threshold = float(self.args.get("threshold", "0.6"))
        limit = int(self.args.get("limit", "5"))
        
        if not query:
            return Response(message="Error: 'text' (query) is required.", break_loop=False)
        try:
            db = await Memory.get(self.agent)
            
            filter_str = ""
            if area:
                filter_str = f"area == '{area}'"
                
            docs = await db.search_similarity_threshold(
                query=query, 
                limit=limit, 
                threshold=threshold, 
                filter=filter_str
            )
            if not docs:
                return Response(message=f"No memories found matching '{query}' in area '{area or 'all'}' with threshold {threshold}.", break_loop=False)
            results = []
            for doc in docs:
                meta = doc.metadata
                results.append(f"[ID: {meta.get('id', '?')}] [Area: {meta.get('area', '?')}] [Time: {meta.get('timestamp', '?')}]\n{doc.page_content}")
            
            return Response(message="\n\n---\n\n".join(results), break_loop=False)
        except Exception as e:
            return Response(message=f"Query failed: {str(e)}", break_loop=False)
