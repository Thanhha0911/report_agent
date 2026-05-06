import os
import duckdb
import pandas as pd
import subprocess
from crewai.tools import BaseTool

OUTPUT_DB = r'D:\src\data\olist.duckdb'

class DuckDBQueryTool(BaseTool):
    name: str = "DuckDB Query Tool"
    description: str = "Run SQL queries against the Data Warehouse. Use 'SHOW TABLES' to see available tables first. Use double quotes for table names with spaces."

    def _run(self, query: str) -> str:
        try:
            conn = duckdb.connect(OUTPUT_DB, read_only=True)
            df = conn.execute(query).df()
            conn.close()
            return df.to_string()
        except Exception as e:
            return f"Error: {str(e)}"

class PythonExecutionTool(BaseTool):
    name: str = "Python Execution Tool"
    description: str = "Runs a python script. Pass the absolute filename as argument."

    def _run(self, filename: str) -> str:
        try:
            result = subprocess.run(['python', filename], capture_output=True, text=True)
            if result.returncode != 0:
                return f"Error: Execution Failed.\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
            return f"Success: {result.stdout}"
        except Exception as e:
            return f"Error: Tool encountered an exception: {str(e)}"
