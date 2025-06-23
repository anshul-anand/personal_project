query_map = {
    "OAuth Authentication Issue": "SELECT * FROM logs.oauth_errors WHERE timestamp > current_timestamp - interval '1 hour';",
    "SSO/SSO Token Issue": "SELECT * FROM logs.sso_logs WHERE timestamp > current_timestamp - interval '1 hour';",
    "Access Denied": "SELECT * FROM logs.access_denied WHERE timestamp > current_timestamp - interval '1 hour';",
    "General Error": "SELECT * FROM logs.general_errors WHERE timestamp > current_timestamp - interval '1 hour';"
}

def get_query(issue_type):
    return query_map.get(issue_type, query_map["General Error"])
