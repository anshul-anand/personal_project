import streamlit as st
from har_parser import load_har, extract_failed_requests
from issue_mapper import map_issue_type
from query_template import get_query
from snowflake_connector import run_query

st.title("HAR Log Analyzer – Snowflake Automation Tool")

uploaded_file = st.file_uploader("Upload a .har file", type="har")

if uploaded_file:
    har_data = load_har(uploaded_file)
    failed_requests = extract_failed_requests(har_data)

    if not failed_requests:
        st.success("✅ No failed requests found.")
    else:
        for i, req in enumerate(failed_requests, start=1):
            issue_type = map_issue_type(req)
            st.subheader(f"Issue {i}: {issue_type}")
            st.write(f"**URL**: {req['url']}")
            st.code(req['response_body'][:1000])  # Truncate long body

            query = get_query(issue_type)
            st.code(query, language='sql')

            if st.button(f"Run Query for Issue {i}"):
                # Dummy Snowflake config
                snowflake_config = {
                    "user": "AANAND",
                    "account": "snowhouse",
                    "authenticator":"externalbrowser"
                }
                results = run_query(query, snowflake_config)
                st.write("Query Results:")
                st.dataframe(results)
