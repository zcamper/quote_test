import sqlite3
import pyodbc
import pandas as pd
import re
import traceback

# --- 1. CONFIGURATION ---
# Update these details to match your SQL Server connection
SQL_SERVER = "REP3"  # The server name, e.g., 'localhost' or 'SERVER_IP'
DATABASE = "KINSL"   # The database name
# Using Windows Authentication. For SQL Server Authentication, use the string below.
CONNECTION_STRING = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"
# SQL_AUTH_CONNECTION_STRING = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE={DATABASE};UID=your_username;PWD=your_password;"

# Name for the output SQLite database file
SQLITE_DB_NAME = "test_data_trim.db"

# --- 2. QUERIES AND TABLE NAMES ---
# All queries are now active.

QUERIES_TO_RUN = [
    {
        "table_name": "sv000123_overhead_groups",
        "query": """
        SELECT [Overhead_Group_Code], [Labor_Group_Name], [DEPRTMNT], [JOBTITLE], 
               [PAYRCORD], [Billing_Amount], [Billing_Description], [Wennsoft_Affiliate], 
               [Wennsoft_Region], [Wennsoft_Branch], [USERID], [Technician_ID], 
               [Technician_Team], [User_Define_1], [User_Define_2], [USRDAT01], 
               [USRDAT02], [User_Defined_Dollar_1], [User_Defined_Dollar_2], 
               [User_Def_Integer_1], [User_Def_Integer_2], [WSReserved_CB1], 
               [WSReserved_CB2], [DEX_ROW_ID] 
        FROM [KINSL].[dbo].[SV000123]
        """
    },
    {
        "table_name": "sv00166_pricing_matrix",
        "query": """
        SELECT [Pricing_Matrix_Name], [WS_Cost_Code], [WS_Other_Cost_Sub_Code], 
               [Price_Matrix_Entry_1], [Price_Matrix_Entry_2], [Price_Matrix_Entry_3], 
               [Price_Matrix_Entry_4], [Price_Matrix_Entry_5], [Price_Matrix_Entry_6], 
               [Price_Matrix_Entry_7], [SEQNUMBR], [WS_Billing_Method], [Billing_Amount], 
               [ITEMDESC], [Pricing_Markup_Amount], [Pricing_Markup_Percent], 
               [Pricing_Amount_1], [Pricing_Amount_2], [WS_Bill_Cost_Code], 
               [WS_Bill_Other_Cost_Code], [Min_Amount_Total], [Max_Amount_Total], 
               [MODIFDT], [Modified_Time], [MDFUSRID], [DEX_ROW_ID] 
        FROM [KINSL].[dbo].[SV00166]
        """
    },
    {
       "table_name": "service_call_details",
       "query": """
        SELECT DISTINCT
            SV00300.Service_Call_ID AS SV00300_Service_Call_ID,
            SV00300.CUSTNMBR AS SV00300_CUSTNMBR,
            SV00300.ADRSCODE AS SV00300_ADRSCODE,
            SV00300.Bill_Customer_Number AS SV00300_Bill_Customer_Number,
            -- Customer Identification
            SV00200.CUSTNAME AS SV00200_CUSTNAME,
            SV00200.Labor_Group_Name AS SV00200_Labor_Group_Name,
            SV00200.Pricing_Matrix_Name AS SV00200_Pricing_Matrix_Name,
            Primary_Loc.CUSTNAME AS PL_CUSTNAME,
            Primary_Loc.Labor_Group_Name AS PL_Labor_Group_Name,
            Primary_Loc.Pricing_Matrix_Name AS PL_Pricing_Matrix_Name,
            BILLCUSTOMER.CUSTNAME AS BillCustomer_CUSTNAME,
            -- Equipment & Unit Information
            SV00302.Equipment_ID AS SV00302_Equipment_ID,
            Generator.Equipment_ID AS Generator_Equipment_ID,
            Generator.Wennsoft_Model_Number AS Generator_Wennsoft_Model_Number,
            Generator.Wennsoft_Serial_Number AS Generator_Wennsoft_Serial_Number,
            STUFF((SELECT '; ' + RTRIM(S.Equipment_ID) FROM [KINSL]..SV00400 AS S WHERE S.ADRSCODE = SV00400.ADRSCODE AND S.CUSTNMBR = SV00400.CUSTNMBR AND S.Equipment_Type = 'ENGINE' FOR XML PATH('')), 1, 1, '') AS Engine_Equipment_ID,
            Engine.Wennsoft_Model_Number AS Engine_Wennsoft_Model_Number,
            STUFF((SELECT '; ' + RTRIM(S.Wennsoft_Serial_Number) FROM [KINSL]..SV00400 AS S WHERE S.ADRSCODE = SV00400.ADRSCODE AND S.CUSTNMBR = SV00400.CUSTNMBR AND S.Equipment_Type = 'ENGINE' FOR XML PATH('')), 1, 1, '') AS Engine_Wennsoft_Serial_Number,
            STUFF((SELECT '; ' + RTRIM(S.Equipment_ID) FROM [KINSL]..SV00400 AS S WHERE S.ADRSCODE = SV00400.ADRSCODE AND S.CUSTNMBR = SV00400.CUSTNMBR AND S.Equipment_Type = 'ATS' FOR XML PATH('')), 1, 1, '') AS ATS_Equipment_ID,
            ATS.Wennsoft_Model_Number AS ATS_Wennsoft_Model_Number,
            STUFF((SELECT '; ' + RTRIM(S.Wennsoft_Serial_Number) FROM [KINSL]..SV00400 AS S WHERE S.ADRSCODE = SV00400.ADRSCODE AND S.CUSTNMBR = SV00400.CUSTNMBR AND S.Equipment_Type = 'ATS' FOR XML PATH('')), 1, 1, '') AS ATS_Wennsoft_Serial_Number,
            -- Warranty Information
            SV00400.[Extended_Warr_Expiration] AS SV00400_Extended_Warr_Expiration,
            SV00400.[Warranty_Expiration] AS SV00400_Warranty_Expiration,
            SV00400.[Install_Date] AS SV00400_Install_Date
        FROM [KINSL]..SV00300 WITH (NOLOCK)
        LEFT JOIN [KINSL]..SV00200 WITH (NOLOCK) ON SV00200.[ADRSCODE] = SV00300.[ADRSCODE] AND SV00200.[CUSTNMBR] = SV00300.[CUSTNMBR]
        LEFT JOIN [KINSL]..SV00302 WITH (NOLOCK) ON SV00302.[Service_Call_ID] = SV00300.[Service_Call_ID]
        LEFT JOIN [KINSL]..SV00400 WITH (NOLOCK) ON SV00400.[CUSTNMBR] = SV00302.[CUSTNMBR] AND SV00400.[ADRSCODE] = SV00302.[ADRSCODE] AND SV00400.[Equipment_ID] = SV00302.[Equipment_ID]
        LEFT JOIN [KINSL]..[SV00502] WITH (NOLOCK) ON SV00502.[Quote_Number] = SV00300.[Service_Call_ID]
        INNER JOIN [KINSL]..RM00101 AS T6 WITH (NOLOCK) ON T6.[CUSTNMBR] = SV00300.[CUSTNMBR]
        INNER JOIN [KINSL]..RM00201 AS T7 WITH (NOLOCK) ON T7.[CLASSID] = T6.[CUSTCLAS]
        LEFT JOIN (SELECT * FROM [KINSL]..SV00200 WHERE ADRSCODE = 'PRIMARY') AS Primary_Loc ON SV00300.CUSTNMBR = Primary_Loc.CUSTNMBR
        LEFT JOIN (SELECT * FROM [KINSL]..SV00400 WHERE Equipment_Type = 'Generator') AS Generator ON SV00302.ADRSCODE = Generator.ADRSCODE AND SV00302.CUSTNMBR = Generator.CUSTNMBR
        LEFT JOIN (SELECT * FROM [KINSL]..SV00400 WHERE Equipment_Type = 'ENGINE') AS Engine ON SV00302.ADRSCODE = Engine.ADRSCODE AND SV00302.CUSTNMBR = Engine.CUSTNMBR
        LEFT JOIN (SELECT * FROM [KINSL]..SV00400 WHERE Equipment_Type = 'ATS') AS ATS ON SV00302.ADRSCODE = ATS.ADRSCODE AND SV00302.CUSTNMBR = ATS.CUSTNMBR
        LEFT JOIN [KINSL]..WSCustomer WITH (NOLOCK) ON SV00300.CUSTNMBR = WSCustomer.CustomerNumber
        LEFT JOIN [KINSL]..RM00101 AS BILLCUSTOMER WITH (NOLOCK) ON SV00300.Bill_Customer_Number = BILLCUSTOMER.CUSTNMBR
        WHERE
        SV00300.Service_Call_ID like '25%'
       """
    },
    {
      "table_name": "sv000805_service_notes",
      "query": """
      SELECT [CUSTNMBR], [ADRSCODE], [Service_Call_ID], [Record_Notes], [WS_Note_Type],
             [Note_Service_Index], [USERID], [Technician_ID], [Technician_Team], [Note_Author]
      FROM [KINSL].[dbo].[SV000805]
      WHERE Service_Call_ID like '25%'
      """
    },
    {
      "table_name": "iv00102_item_quantity_all",
      "query": """
      SELECT IV00102.ITEMNMBR, IV00102.LOCNCODE, IV00102.QTYONHND
      FROM IV00102
      """
    }
]

def clean_and_extract_sql(power_query_string):
    """
    Extracts the pure SQL query from a Power Query M string.
    """
    # Use regex to find the content inside [Query="..."]
    match = re.search(r'\[Query="(.+)"\]', power_query_string, re.DOTALL)
    if not match:
        # Fallback for other formats
        if "SELECT" in power_query_string.upper():
            return power_query_string
        return None

    sql_query = match.group(1)
    
    # Replace Power Query specific line breaks and tabs with spaces
    sql_query = sql_query.replace("#(lf)", " ").replace("#(tab)", " ")
    
    # Clean up any extra whitespace
    return ' '.join(sql_query.split())


def process_queries(query_list, sql_conn_str, sqlite_db):
    """
    Executes each query against SQL Server and writes the result to SQLite.
    """
    print(f"--- Starting Data Transfer ---")
    print(f"Source:      SQL Server '{SQL_SERVER}', Database '{DATABASE}'")
    print(f"Destination: SQLite file '{sqlite_db}'\n")

    # Establish the SQLite connection once
    try:
        sqlite_conn = sqlite3.connect(sqlite_db)
        print("✅ Successfully connected to SQLite.")
    except Exception as e:
        print(f"❌ ERROR: Could not connect to SQLite database '{sqlite_db}'.")
        print(f"Details: {e}")
        return

    # Process each query
    for item in query_list:
        table_name = item["table_name"]
        query = item["query"]
        print(f"Processing table '{table_name}'...")

        try:
            # 1. Read data from SQL Server using pandas
            with pyodbc.connect(sql_conn_str) as sql_conn:
                df = pd.read_sql_query(query, sql_conn)
            
            print(f"  - Fetched {len(df)} rows from SQL Server.")

            # 2. Write the DataFrame to a table in SQLite
            # 'if_exists='replace'' will drop the table if it already exists and create a new one.
            df.to_sql(table_name, sqlite_conn, if_exists='replace', index=False)
            
            print(f"  - ✅ Successfully wrote data to SQLite table '{table_name}'.\n")

        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"  - ❌ ERROR executing query for '{table_name}' on SQL Server.")
            print(f"  - SQLSTATE: {sqlstate}")
            print(f"  - Details: {ex}\n")
        except Exception as e:
            print(f"  - ❌ An unexpected error occurred for table '{table_name}'.")
            print(traceback.format_exc()) # Provides detailed error info

    # Close the SQLite connection
    sqlite_conn.close()
    print("--- Data Transfer Complete ---")


if __name__ == "__main__":
    process_queries(QUERIES_TO_RUN, CONNECTION_STRING, SQLITE_DB_NAME)