
import pandas as pd
import sqlite3

def excel_to_sqlite(excel_file, db_file):
    # Create SQLite connection
    conn = sqlite3.connect(db_file)
    
    # Read all sheets from Excel file
    excel = pd.ExcelFile(excel_file)
    
    # Convert each sheet to a table
    for sheet_name in excel.sheet_names:
        # Read sheet into DataFrame
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        # Write DataFrame to SQLite
        # Use sheet name as table name, replace spaces with underscore
        table_name = sheet_name.replace(' ', '_')
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    # Close connections
    conn.close()
    excel.close()

if __name__ == '__main__':
    # Example usage
    excel_to_sqlite('output.xlsx', 'sensor_data.db')