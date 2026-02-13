from python.helpers.tool import Tool, Response

class WorkflowMacros(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method or self.args.get("method")
        
        if method == "feature_flow":
            desc = self.args.get("description", "a new feature")
            instructions = [
                "1. [PLAN] Read existing code related to the feature.",
                "2. [PLAN] Create an implementation_plan.md and get user approval.",
                "3. [EXECUTE] Write the code using file_ops and git_ops (on a new branch).",
                "4. [EXECUTE] Add unit tests in the tests/ directory.",
                "5. [VERIFY] Run tests using test_runner.py.",
                "6. [VERIFY] Run linter.py and fix any issues.",
                "7. [FINALIZE] Create a Pull Request using github_ops.py."
            ]
            return Response(message=f"Workflow for: {desc}\n\nPlease follow these steps autonomously:\n\n" + "\n".join(instructions), break_loop=False)
        elif method == "hotfix_flow":
            issue = self.args.get("issue", "the reported bug")
            instructions = [
                "1. [PLAN] Reproduce the bug with a new test case in test_runner.",
                "2. [EXECUTE] Fix the code using codebase_indexer to find the root cause.",
                "3. [VERIFY] Confirm the new test passes.",
                "4. [VERIFY] Run full regression tests.",
                "5. [FINALIZE] Commit and push fix with version_manager.py."
            ]
            return Response(message=f"Hotfix Workflow for: {issue}\n\nExecute the following:\n\n" + "\n".join(instructions), break_loop=False)
        else:
            return Response(message="Unknown macro. Available: feature_flow, hotfix_flow.", break_loop=False)
