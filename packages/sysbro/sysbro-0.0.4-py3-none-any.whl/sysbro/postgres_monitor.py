import psycopg2


def get_idle_transactions(conn_info, idle_threshold=150):
    conn = psycopg2.connect(**conn_info)
    cursor = conn.cursor()
    query = """
    SELECT pid, state, query, age(clock_timestamp(), query_start) as age
    FROM pg_stat_activity
    WHERE state = 'idle in transaction' AND age > interval '%s minutes';
    """ % idle_threshold
    cursor.execute(query)
    return cursor.fetchall()


def kill_idle_transactions(conn_info, idle_threshold=150):
    conn = psycopg2.connect(**conn_info)
    cursor = conn.cursor()
    idle_transactions = get_idle_transactions(conn_info, idle_threshold)
    for trans in idle_transactions:
        pid = trans[0]
        cursor.execute(f"SELECT pg_terminate_backend({pid});")
    conn.commit()
