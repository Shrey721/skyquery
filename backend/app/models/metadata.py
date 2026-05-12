from typing import List, Optional
from pydantic import BaseModel, Field

class ColumnMetadata(BaseModel):
    name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="Data type of the column")
    is_nullable: bool = Field(..., description="Whether the column can contain null values")

class TableMetadata(BaseModel):
    catalog: str = Field(..., description="Catalog name")
    schema_name: str = Field(..., description="Schema name")
    table_name: str = Field(..., description="Table name")
    columns: List[ColumnMetadata] = Field(default_factory=list, description="List of columns in the table")
    row_count: Optional[int] = Field(None, description="Estimated row count from stats")

class SchemaMetadata(BaseModel):
    tables: List[TableMetadata] = Field(default_factory=list, description="List of tables in the schema")
