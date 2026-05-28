from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from enum import Enum

class ColumnType(str, Enum):
    TEXT = "text"
    INTEGER = "integer"
    REAL = "real"
    BOOLEAN = "boolean"
    DATETIME = "datetime"

class DBColumn(BaseModel):
    name: str = Field(..., description="Column name, e.g. 'first_name'")
    type: ColumnType = Field(..., description="Data type of the column")
    is_primary_key: bool = Field(default=False, description="Is this the primary key?")
    is_nullable: bool = Field(default=True, description="Can this column be null?")
    default_value: Optional[str] = Field(default=None, description="String representation of default value, e.g. 'CURRENT_TIMESTAMP'")
    foreign_key: Optional[str] = Field(default=None, description="Foreign key table and column, e.g. 'users.id'")

class DBTable(BaseModel):
    name: str = Field(..., description="Name of the table")
    columns: List[DBColumn] = Field(..., description="Columns in the table")
    seed_data: List[Dict[str, Any]] = Field(default_factory=list, description="Initial records to insert")

class DBSchemaSpec(BaseModel):
    tables: List[DBTable] = Field(..., description="Tables in the database schema")
