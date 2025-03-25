import psycopg2
from psycopg2 import sql

# Database connection parameters
db_params = {
    'dbname': 'mydatabase',
    'user': 'myuser',
    'password': 'mypassword',
    'host': 'postgres_db',  # or your database host
    'port': '5432'        # default PostgreSQL port
}

# Connect to the PostgreSQL database
connection = psycopg2.connect(**db_params)

async def fetch_all_data_from_table(table_name):
    """
    Connects to the PostgreSQL database and retrieves all data from the specified table.

    Parameters:
    db_params (dict): A dictionary containing database connection parameters.
    table_name (str): The name of the table to fetch data from.

    Returns:
    list: A list of tuples containing the rows from the table.
    """
    cursor = None
    try:
        cursor = connection.cursor()

        # Create a SQL query to select all data from the table
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the executed query
        rows = cursor.fetchall()

        data = []
        for row in rows:
            data.append(
                {
                    "project_id": row[0],
                    "project_name": row[1]
                }
            )

        return data
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()