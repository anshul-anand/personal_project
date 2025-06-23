import snowflake.connector


def run_query(query, snowflake_config):
    conn = snowflake.connector.connect(
        user=snowflake_config["user"],
        account=snowflake_config["account"],
        #private_key_path=snowflake_config["key_path"],  # or use password
        #role=snowflake_config.get("role", "SUPPORT_ROLE"),
        #warehouse=snowflake_config.get("warehouse", "SUPPORT_WH"),
        #database=snowflake_config.get("database", "SUPPORT_DB"),
        #schema=snowflake_config.get("schema", "LOGS")
        authenticator=snowflake_config["authenticator"]
    )

    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows




 
snowflake_conf = {
                    "user": "user",
                    "account": "account",
                    "authenticator":"externalbrowser"
                 }


query = "select current_account();"

rows = run_query(query,snowflake_conf)
print(rows)

####
#if you wish to load from the env file. 

# from dotenv import load_dotenv
# import os

# load_dotenv()
# user = os.getenv("SNOWFLAKE_USER")
