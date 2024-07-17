# Postgresql Table Builder
 
### 🌐 Installation and updating

`py -m pip install --upgrade pg_table_builder`



### ⚙️ Features


You can get SQL query string for creating table

Example:

```python
from pg_table_builder import Table, Column, Serial, Varchar, Text

Table(
    "users",
    Column("id", Serial(primary_key=True, not_null=True)),
    Column("username", Varchar(limit_size=10, not_null=True)),
    Column("description", Text(default_expression="'It''s your description'"))
)

```

```sql
CREATE TABLE IF NOT EXISTS users (
	id SERIAL PRIMARY KEY NOT NULL,
	username VARCHAR (10) NOT NULL,
	description TEXT default 'It''s your description'
);
```
