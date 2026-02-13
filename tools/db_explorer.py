from python.helpers.tool import Tool, Response
from python.helpers import files
import sqlite3
import os

class DbExplorer(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method or self.args.get("method")
        db_path = self.args.get("db_path")
        sql = self.args.get("sql", "")
        
        if not db_path:
            return Response(message="Error: 'db_path' is required.", break_loop=False)
            
        abs_db_path = files.get_abs_path(db_path)
        
        if method == "query":
            if not sql:
                return Response(message="Error: 'sql' query is required.", break_loop=False)
            
            try:
                conn = sqlite3.connect(abs_db_path)
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                conn.close()
                
                result = [f"Columns: {', '.join(columns)}"]
                for row in rows[:50]: # Limit to 50 rows
                    result.append(str(row))
                
                return Response(message=f"Query Results ({len(rows)} rows):\n\n" + "\n".join(result), break_loop=False)
            except Exception as e:
                return Response(message=f"Database error: {str(e)}", break_loop=False)
        elif method == "list_tables":
            try:
                conn = sqlite3.connect(abs_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()
                return Response(message=f"Tables in '{db_path}':\n" + "\n".join(tables), break_loop=False)
            except Exception as e:
                return Response(message=f"Error listing tables: {str(e)}", break_loop=False)
        else:
            return Response(message=f"Unknown method '{method}'. Currently only SQLite is supported via this tool.", break_loop=False)
