from python.helpers.tool import Tool, Response
from python.helpers import files
import subprocess
import os
import re

class TestRunner(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method or self.args.get("method", "run")
        framework = self.args.get("framework", "pytest").lower()
        path = self.args.get("path", ".")

        abs_path = files.get_abs_path(path)

        if method == "run":
            command = []
            if framework == "pytest":
                command = ["pytest", "--verbose", abs_path]
            elif framework == "unittest":
                command = ["python", "-m", "unittest", "discover", "-s", abs_path]
            else:
                return Response(message=f"Error: Unsupported framework '{framework}'. Use 'pytest' or 'unittest'.", break_loop=False)
            try:
                # Set PYTHONPATH to include current dir
                env = os.environ.copy()
                env["PYTHONPATH"] = files.get_base_dir() + os.pathsep + env.get("PYTHONPATH", "")

                result = subprocess.run(command, capture_output=True, text=True, env=env)

                output = result.stdout + "\n" + result.stderr

                # Simple parsing for common failure patterns
                summary = "Test Run Summary:\n"
                if result.returncode == 0:
                    summary += "✅ All tests passed.\n"
                else:
                    summary += "❌ Some tests failed.\n"

                    # Look for failed test names in pytest output
                    failed_tests = re.findall(r"FAILED\s+(.*?) -", output)
                    if failed_tests:
                        summary += "Failed tests:\n"
                        for test in failed_tests[:10]:
                            summary += f"  - {test}\n"

                message = f"{summary}\nDetailed Output:\n\n{output}"
                return Response(message=message, break_loop=False)

            except Exception as e:
                return Response(message=f"Error running tests: {str(e)}", break_loop=False)
        else:
            return Response(message=f"Error: Unknown method '{method}'. Valid methods are: run.", break_loop=False)
