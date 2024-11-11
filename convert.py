import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('instance\sensor_data.db')

# List of table names to export
tables = ['sensor_data0', 'sensor_data1', 'sensor_data']

# Create a Pandas Excel writer using XlsxWriter as the engine
with pd.ExcelWriter('output.xlsx', engine='xlsxwriter') as writer:
    for table in tables:
        # Query the database and load the data into a pandas DataFrame
        query = f"SELECT * FROM {table}"
        df = pd.read_sql_query(query, conn)
        
        # Write the DataFrame to a specific sheet in the Excel file
        df.to_excel(writer, sheet_name=table, index=False)

# Close the database connection
conn.close()