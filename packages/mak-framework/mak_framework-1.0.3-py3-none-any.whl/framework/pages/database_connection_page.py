import pyodbc
import time
from framework.utils.utils import LoggerUtils

logger = LoggerUtils()


def execute_query(connection_string, query, values=None):
    start_time = time.time()
    try:
        with pyodbc.connect(connection_string) as connection:
            connection.autocommit = True
            with connection.cursor() as cursor:
                if values:
                    cursor.execute(query, values)
                    logger.log_info(f"Query executed successfully with params: {str(values)} - {query}")
                else:
                    cursor.execute(query)
                    logger.log_info(f"Query executed successfully without params - {query}")

                # Check if the query contains "update"
                is_update = 'update' in query.lower()

                if is_update:
                    result = f"{cursor.rowcount} rows affected"
                else:
                    if cursor.description:
                        columns = [column[0] for column in cursor.description]
                        row = cursor.fetchone()

                        if row:
                            result = dict(zip(columns, row))
                        else:
                            result = "No rows returned"
                    else:
                        result = f"{cursor.rowcount} rows affected"

                execution_time = time.time() - start_time
                logger.log_info(f"Query execution time: {execution_time} seconds")

                return result

    except pyodbc.Error as e:
        error_message = f"Error executing query: {e}"
        logger.log_error(error_message)
        raise e
