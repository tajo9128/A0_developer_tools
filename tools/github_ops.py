from python.helpers.tool import Tool, Response
from python.helpers import files
import json
import os
import urllib.request
import urllib.error


# GitHub credentials provided by user
GITHUB_USER = 'tajo9128'
GITHUB_EMAIL = 'tajo9128@gmail.com'

class GitHubOps(Tool):
    def _api_call(self, endpoint, method="GET", data=None):
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable is required")

        repo_full_name = self.args.get("repo")
        if not repo_full_name:
            try:
                from git import Repo
                repo = Repo(files.get_base_dir())
                url = repo.remotes.origin.url
                if "github.com" in url:
                    repo_full_name = url.split("github.com")[-1].strip(":").strip("/").replace(".git", "")
            except:
                return None, "Error: 'repo' argument required or GITHUB_TOKEN not configured for local repo."

        url = f"https://api.github.com/repos/{repo_full_name}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Agent-Zero-GitHub-Tool"
        }

        req = urllib.request.Request(url, headers=headers, method=method)
        if data:
            req.data = json.dumps(data).encode("utf-8")
            req.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode()), None
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            error_msg = f"GitHub API Error: {e.code} {e.reason}"
            if error_body:
                error_msg = f"{error_msg}\n{error_body}"
            return None, error_msg
        except Exception as e:
            return None, f"Error: {str(e)}"

    async def execute(self, **kwargs) -> Response:
        method = self.method or self.args.get("method")

        if method == "create_pr":
            title = self.args.get("title")
            body = self.args.get("body", "")
            head = self.args.get("head")
            base = self.args.get("base", "main")

            if not title or not head:
                return Response(message="Error: 'title' and 'head' are required for create_pr.", break_loop=False)

            data = {"title": title, "body": body, "head": head, "base": base}
            resp, err = self._api_call("pulls", "POST", data)
            if err:
                return Response(message=err, break_loop=False)
            return Response(message=f"Successfully created PR: {resp.get('html_url')}", break_loop=False)

        elif method == "list_prs":
            state = self.args.get("state", "open")
            resp, err = self._api_call(f"pulls?state={state}")
            if err:
                return Response(message=err, break_loop=False)
            prs = [f"#{pr['number']} {pr['title']} ({pr['user']['login']})" for pr in resp]
            pr_list = "\n".join(prs) if prs else "None"
            return Response(message=f"Pull Requests ({state}):\n{pr_list}", break_loop=False)

        elif method == "add_comment":
            issue_no = self.args.get("number")
            body = self.args.get("body")
            if not issue_no or not body:
                return Response(message="Error: 'number' and 'body' required for add_comment.", break_loop=False)

            resp, err = self._api_call(f"issues/{issue_no}/comments", "POST", {"body": body})
            if err:
                return Response(message=err, break_loop=False)
            return Response(message=f"Comment added to #{issue_no}.", break_loop=False)

        elif method == "check_workflows":
            resp, err = self._api_call("actions/runs?per_page=5")
            if err:
                return Response(message=err, break_loop=False)
            runs = [f"{run['name']} - {run['status']} ({run['conclusion'] or 'running'})" for run in resp.get("workflow_runs", [])]
            run_list = "\n".join(runs) if runs else "None"
            return Response(message=f"Recent Workflow Runs:\n{run_list}", break_loop=False)

        else:
            return Response(message=f"Error: Unknown method '{method}'. Valid methods: create_pr, list_prs, add_comment, check_workflows.", break_loop=False)
