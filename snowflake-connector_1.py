import snowflake.connector


conn = snowflake.connector.connect(
    user = 'username',
    account='account',
    authenticator='externalbrowser'

)


cur = conn.cursor()
cur.execute("select current_account();")
print(cur.fetchall())
cur.close()
conn.close()
