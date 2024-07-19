import json
import os

install_path = os.path.dirname(os.path.abspath(__file__))
mock_file = f"{install_path}/config/mock.json"


class AntHillClient():
    def __init__(self, token):
        self.token = token
        mock_data = {}
        with open(mock_file) as f:
            mock_data = json.load(f)
        self.data = mock_data

    def get_user(self, username):
        if len(self.token) > 0:
            return "Flik"
        return "annonymous"

    def get_workspaces(self):
        for w in self.data:
            yield self.data[w]

    def get_projects(self, workspace):
        for w in self.get_workspaces():
            if w.get("gid", "").lower() == workspace.lower():
                return w.get("projects", [])
        return []

    def get_issues(self, project):
        for workspace in self.get_workspaces():
            w = workspace.get("gid", "")
            for p in self.get_projects(w):
                if p.get("gid", "").lower() == project.lower():
                    return p.get("issues", {})
        return []

    def get_comments(self, issue):
        for workspace in self.get_workspaces():
            w = workspace.get("gid", "")
            for project in self.get_projects(w):
                p = project.get("gid", "")
                for i in self.get_issues(p):
                    if i.get("gid", "").lower() == issue.lower():
                        return i.get("comments", [])
        return []

    def post_comment(self, issue, comment):
        comments = self.get_comments(issue)
        original_len = len(comments)
        comments.append(comment)
        if original_len + 1 == len(comments):
            return True
        return False

