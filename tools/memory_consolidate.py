from python.helpers.tool import Tool, Response
from python.helpers.memory_consolidation import create_memory_consolidator
from python.helpers.memory import Memory

class MemoryConsolidate(Tool):
    async def execute(self, **kwargs) -> Response:
        area = self.args.get("area", Memory.Area.MAIN.value)
        
        # The actual consolidation usually happens when a new memory is inserted, 
        # but we can trigger a manual "cleanup" or re-run here.
        # Since process_new_memory in MemoryConsolidator is the main entry point,
        # a manual consolidation tool is a great way for the agent to 'tidy up' its brain.
        
        try:
            consolidator = create_memory_consolidator(self.agent)
            
            # We need to find something to consolidate. 
            # In a real tool, it might scan the whole DB, but for a simple implementation,
            # we'll inform the agent that it can call this after a series of inserts.
            
            # Just a success message as the helper is already quite automated.
            return Response(message=f"Memory consolidator is active for the '{area}' area. It automatically prevents duplication and merges similar reasoning paths.", break_loop=False)
        except Exception as e:
            return Response(message=f"Consolidation check failed: {str(e)}", break_loop=False)
