from cc_py_commons.db import connection as db_connection


def execute(table_name):
	conn = None
	try:
		conn = db_connection.get()
		cursor = conn.cursor()
		sql_query = f"CREATE TABLE {table_name} (search_result text, error text)"
		cursor.execute(sql_query)
		conn.commit()
	finally:
		db_connection.close(conn)
	return table_name
