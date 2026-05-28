import sqlite3
import os
from typing import List, Dict, Any, Optional
from app.schemas.db import DBSchemaSpec, DBTable, ColumnType

DB_PATH = os.path.join(os.path.dirname(__file__), "dynamic_app.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(schema: DBSchemaSpec):
    """
    Dynamically initializes SQLite tables based on the schema spec and inserts seed data.
    """
    # Delete the old database to start fresh
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for table in schema.tables:
            columns_def = []
            for col in table.columns:
                col_type = "TEXT"
                if col.type == ColumnType.INTEGER:
                    col_type = "INTEGER"
                elif col.type == ColumnType.REAL:
                    col_type = "REAL"
                elif col.type == ColumnType.BOOLEAN:
                    col_type = "INTEGER"  # SQLite stores booleans as 0 or 1

                col_def = f'"{col.name}" {col_type}'

                if col.is_primary_key:
                    col_def += " PRIMARY KEY AUTOINCREMENT"
                elif not col.is_nullable:
                    col_def += " NOT NULL"

                if col.default_value is not None:
                    col_def += f" DEFAULT {col.default_value}"

                if col.foreign_key:
                    ref_table, ref_col = col.foreign_key.split(".")
                    col_def += f' REFERENCES "{ref_table}"("{ref_col}")'

                columns_def.append(col_def)

            create_query = f'CREATE TABLE IF NOT EXISTS "{table.name}" ({", ".join(columns_def)})'
            cursor.execute(create_query)

            # Insert seed data if present
            if table.seed_data:
                for row in table.seed_data:
                    # Filter only columns defined in the table
                    valid_cols = [col.name for col in table.columns if col.name != "id"]
                    insert_cols = [c for c in row.keys() if c in valid_cols]
                    
                    if not insert_cols:
                        continue

                    placeholders = ", ".join(["?" for _ in insert_cols])
                    cols_str = ", ".join([f'"{c}"' for c in insert_cols])
                    values = [row[c] for c in insert_cols]

                    insert_query = f'INSERT INTO "{table.name}" ({cols_str}) VALUES ({placeholders})'
                    cursor.execute(insert_query, values)

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def list_records(table_name: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = f'SELECT * FROM "{table_name}"'
        params = []
        if filters:
            conditions = []
            for k, v in filters.items():
                if v is not None:
                    conditions.append(f'"{k}" = ?')
                    params.append(v)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_record(table_name: str, record_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f'SELECT * FROM "{table_name}" WHERE id = ?', (record_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def create_record(table_name: str, record: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Get table columns to prevent injection / invalid column errors
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        cols = [r["name"] for r in cursor.fetchall() if r["name"] != "id"]
        
        insert_data = {k: v for k, v in record.items() if k in cols}
        
        cols_str = ", ".join([f'"{c}"' for c in insert_data.keys()])
        placeholders = ", ".join(["?" for _ in insert_data])
        values = list(insert_data.values())

        query = f'INSERT INTO "{table_name}" ({cols_str}) VALUES ({placeholders})'
        cursor.execute(query, values)
        new_id = cursor.lastrowid
        conn.commit()
        return {**insert_data, "id": new_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def update_record(table_name: str, record_id: int, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        cols = [r["name"] for r in cursor.fetchall() if r["name"] != "id"]
        
        update_data = {k: v for k, v in record.items() if k in cols}
        if not update_data:
            return get_record(table_name, record_id)

        set_clause = ", ".join([f'"{c}" = ?' for c in update_data.keys()])
        values = list(update_data.values()) + [record_id]

        query = f'UPDATE "{table_name}" SET {set_clause} WHERE id = ?'
        cursor.execute(query, values)
        conn.commit()
        return get_record(table_name, record_id)
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_record(table_name: str, record_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f'DELETE FROM "{table_name}" WHERE id = ?', (record_id,))
        changes = conn.total_changes
        conn.commit()
        return changes > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def aggregate_records(table_name: str, operation: str, column: str, group_by: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Performs analytical aggregations for dynamic metric widgets and charts.
    operation can be 'count', 'sum', 'avg', 'min', 'max'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        agg_clause = f'{operation}("{column}")'
        if operation.lower() == "count" and column == "*":
            agg_clause = 'COUNT(*)'

        if group_by:
            query = f'SELECT "{group_by}", {agg_clause} as value FROM "{table_name}" GROUP BY "{group_by}"'
        else:
            query = f'SELECT {agg_clause} as value FROM "{table_name}"'

        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
