from har_parser import load_har, extract_failed_requests
from issue_mapper import map_issue_type
from query_template import get_query
from snowflake_connector import run_query


def main():
    har_file_path = input("Enter path to .har file: ")
    har_data = load_har(har_file_path)
    failed_requests = extract_failed_requests(har_data)

    if not failed_requests:
        print("No failed requests found.")
        return

    for req in failed_requests:
        issue_type = map_issue_type(req)
        print(f"\nDetected issue: {issue_type}")
        print(f"URL: {req['url']}")
        query = get_query(issue_type)
        print(f"Generated SQL: {query}")

        run = input("Run query in Snowflake? (y/n): ")
        if run.lower() == 'y':
            snowflake_config = {
                "user": "your_user",
                "account": "your_account",
                "key_path": "path_to_your_key.p8",
                "role": "SUPPORT_ROLE",
                "warehouse": "SUPPORT_WH",
                "database": "SUPPORT_DB",
                "schema": "LOGS"
            }
            results = run_query(query, snowflake_config)
            for row in results:
                print(row)


if __name__ == "__main__":
    main()
