import psycopg2


def create_tables_if_needed(conn, channel_name):
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS articles "
                        "(link VARCHAR(255) PRIMARY KEY, stock_index VARCHAR(255), "
                        "date timestamp without time zone, article bytea);")
            cur.execute("CREATE TABLE IF NOT EXISTS companies "
                        "(stock_index VARCHAR(255) PRIMARY KEY, name VARCHAR(255));")
            cur.execute("CREATE TABLE IF NOT EXISTS channels "
                        "(channel VARCHAR(255) PRIMARY KEY, name VARCHAR(255));")
            cur.execute("Create TABLE IF NOT EXISTS train "
                        "(link VARCHAR(255) PRIMARY KEY, stock_index VARCHAR(255),"
                        "company_name VARCHAR(255), date timestamp without time zone, article bytea);")
            cur.execute("insert into channels (channel, name) values (%s, %s)", (channel_name, "Polina"))
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
    finally:
        conn.close()
