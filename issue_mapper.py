def map_issue_type(request):
    url = request['url'].lower()
    response_body = request['response_body'].lower()
    
    if "/oauth" in url or "invalid_token" in response_body:
        return "OAuth Authentication Issue"
    elif "sso" in url or "saml" in url or "unauthorized" in response_body:
        return "SSO/SSO Token Issue"
    elif "403" in str(request['status']):
        return "Access Denied"
    else:
        return "General Error"
