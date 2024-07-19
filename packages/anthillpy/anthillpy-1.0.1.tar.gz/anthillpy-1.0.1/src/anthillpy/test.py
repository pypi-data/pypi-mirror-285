from src.anthillpy import AntHillClient

client = AntHillClient(token="TOKEN")


def pack_data(title, description, comments, url, ticket_key):
    ticket_data = {
        "ticket": {
            "title": {
                "name": "title",
                "data": title,
                "data_type": "str"
            },
            "description": {
                "name": "description",
                "data": description,
                "data_type": "str"
            },
            "comments": {
                "name": "comments",
                "data": comments,
                "data_type": "list"
            }
        },
        "url": url,
        "issue_id": ticket_key
    }
    return ticket_data


def get_data(include_comments=False, limit=None):
    if not client:
        return {}

    if workspaces := client.get_workspaces():
        for w in workspaces:
            workspace_gid = w.get("gid", "")
            if projects := client.get_projects(workspace=workspace_gid):
                for p in projects:
                    project_gid = p.get("gid", "")
                    if issues := client.get_issues(project=project_gid):
                        for i in issues:
                            comments = []
                            title = i.get("title", "")
                            issue_gid = i.get("gid", "")
                            description = i.get("description", "")
                            url = i.get("permalink_url", "")
                            if include_comments:
                                if cs := client.get_comments(issue=issue_gid):
                                    for c in cs:
                                        comments.append(c)
                            ticket = pack_data(title, description, comments, url, issue_gid)
                            yield ticket


if user := client.get_user("me"):
    print(f"Logged as {user}")

for t in get_data(include_comments=True):
    print(t)

issue_gid = "ABB-ABB-ABB"
posted = client.post_comment(issue_gid, "new comment")
print(f"Posted new comment: {posted}")

for t in get_data(include_comments=True):
    print(t)