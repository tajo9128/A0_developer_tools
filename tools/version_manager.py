from python.helpers.tool import Tool, Response
from python.helpers import files
from git import Repo
import os
import re
import json
import urllib.request
import urllib.error


# GitHub credentials provided by user
GITHUB_USER = 'tajo9128'
GITHUB_EMAIL = 'tajo9128@gmail.com'

class VersionManager(Tool):
    def _api_call(self, endpoint, method="GET", data=None):
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable is required")

        repo_full_name = self.args.get("repo")
        if not repo_full_name:
            try:
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
            "User-Agent": "Agent-Zero-Version-Tool"
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

        if method == "bump":
            file_path = self.args.get("file", "package.json")
            part = self.args.get("part", "patch").lower() # major, minor, patch
            abs_path = files.get_abs_path(file_path)

            if not os.path.exists(abs_path):
                return Response(message=f"Error: Version file '{file_path}' not found.", break_loop=False)

            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for common version patterns
            # 1. JSON "version": "1.2.3"
            json_match = re.search(r'''"version"\s*:\s*"(\d+)\.(\d+)\.(\d+)"''', content)
            # 2. Python __version__ = "1.2.3"
            py_match = re.search(r'''__version__\s*=\s*["'](\d+)\.(\d+)\.(\d+)["']''', content)

            if json_match:
                major, minor, patch = map(int, json_match.groups())
                if part == "major":
                    major += 1
                    minor = 0
                    patch = 0
                elif part == "minor":
                    minor += 1
                    patch = 0
                else:
                    patch += 1
                new_version = f"{major}.{minor}.{patch}"
                new_content = re.sub(r'"version"\s*:\s*"\d+\.\d+\.\d+"', f'"version": "{new_version}"', content)
            elif py_match:
                major, minor, patch = map(int, py_match.groups())
                if part == "major":
                    major += 1
                    minor = 0
                    patch = 0
                elif part == "minor":
                    minor += 1
                    patch = 0
                else:
                    patch += 1
                new_version = f"{major}.{minor}.{patch}"
                new_content = re.sub(r'''__version__\s*=\s*["']\d+\\.\d+\\.\d+["']''', f'__version__ = "{new_version}"', content)
            else:
                return Response(message="Error: Could not find a supported version pattern in the file.", break_loop=False)

            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            return Response(message=f"Successfully bumped {part} version to {new_version} in '{file_path}'.", break_loop=False)
        elif method == "create_tag":
            tag_name = self.args.get("tag")
            message = self.args.get("message", f"Version {tag_name}")
            if not tag_name:
                return Response(message="Error: 'tag' argument required.", break_loop=False)

            try:
                repo = Repo(files.get_base_dir())
                # Set git user and email from provided credentials
                repo.config_writer().set_value("user", "name", GITHUB_USER).release()
                repo.config_writer().set_value("user", "email", GITHUB_EMAIL).release()
                new_tag = repo.create_tag(tag_name, message=message)
                repo.remotes.origin.push(new_tag)
                return Response(message=f"Successfully created and pushed tag '{tag_name}'.", break_loop=False)
            except Exception as e:
                return Response(message=f"Git Tag Error: {str(e)}", break_loop=False)
        elif method == "create_release":
            tag_name = self.args.get("tag")
            name = self.args.get("name", tag_name)
            body = self.args.get("body", "")

            if not tag_name:
                return Response(message="Error: 'tag' argument required for release.", break_loop=False)

            data = {"tag_name": tag_name, "name": name, "body": body, "draft": False, "prerelease": False}
            resp, err = self._api_call("releases", "POST", data)
            if err:
                return Response(message=err, break_loop=False)
            return Response(message=f"Successfully created GitHub Release: {resp.get('html_url')}", break_loop=False)
        else:
            return Response(message=f"Error: Unknown method '{method}'. Valid: bump, create_tag, create_release.", break_loop=False)
