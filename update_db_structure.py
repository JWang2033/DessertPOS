import os
import pymysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "root",
    "password": "WYz@Dessert2025",
    "database": "dessert_pos_dev",
}

README = "README.md"
TEMP = "README.tmp"
START_MARKER = "<!-- db:start -->"
END_MARKER = "<!-- db:end -->"


def get_tables(cursor):
    cursor.execute("SHOW TABLES")
    result = cursor.fetchall()
    if not result:
        return []
    key = list(result[0].keys())[0]
    return [row[key] for row in result]


def describe_table(cursor, table_name):
    cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")
    return cursor.fetchall()


def get_foreign_key_map(cursor, db_name):
    """
    返回：
    {
        ("inventory", "ingredient_id"): "ingredients.id",
        ("inventory", "unit_id"): "units.id",
        ...
    }
    """
    sql = """
    SELECT
        kcu.TABLE_NAME AS child_table,
        kcu.COLUMN_NAME AS child_column,
        kcu.REFERENCED_TABLE_NAME AS parent_table,
        kcu.REFERENCED_COLUMN_NAME AS parent_column
    FROM information_schema.KEY_COLUMN_USAGE kcu
    WHERE kcu.TABLE_SCHEMA = %s
      AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
    """
    cursor.execute(sql, (db_name,))
    rows = cursor.fetchall()

    fk_map = {}
    for row in rows:
        key = (row["child_table"], row["child_column"])
        value = f"{row['parent_table']}.{row['parent_column']}"
        fk_map[key] = value

    return fk_map


def to_markdown(table_name, columns, fk_map):
    md = [f"### `{table_name}` 表结构", ""]
    md.append("| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 | Reference |")
    md.append("|--------|------|------|------|--------|------|-----------|")

    for col in columns:
        name = col["Field"]
        type_ = col["Type"]
        pk = "✅" if col["Key"] == "PRI" else ""
        null = "✅" if col["Null"] == "YES" else "❌"
        default = col["Default"] if col["Default"] is not None else ""
        comment = col["Comment"] if col["Comment"] else ""
        reference = fk_map.get((table_name, name), "")

        md.append(
            f"| {name} | {type_} | {pk} | {null} | {default} | {comment} | {reference} |"
        )

    return "\n".join(md)


def update_readme(content):
    with open(README, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(TEMP, "w", encoding="utf-8") as f:
        in_block = False
        for line in lines:
            if START_MARKER in line:
                f.write(line)
                f.write("\n")
                f.write(content)
                f.write("\n")
                in_block = True
            elif END_MARKER in line:
                in_block = False
                f.write(line)
            elif not in_block:
                f.write(line)

    os.replace(TEMP, README)


def main():
    conn = pymysql.connect(
        **DB_CONFIG,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()

    tables = get_tables(cursor)
    fk_map = get_foreign_key_map(cursor, DB_CONFIG["database"])

    combined_markdown = "\n\n---\n\n".join(
        to_markdown(table, describe_table(cursor, table), fk_map)
        for table in tables
    )

    update_readme(combined_markdown)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()