import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_config import get_connection
import re

SQL_FILE = os.path.join(os.path.dirname(__file__), '..', 'Hospital_Management.sql')


def split_sql_statements(sql_text):
    # Remove Windows/Unix newlines normalization
    lines = sql_text.splitlines()
    statements = []
    cur = []
    delimiter = ';'

    i = 0
    while i < len(lines):
        line = lines[i]
        # check for DELIMITER directive
        m = re.match(r"^\s*DELIMITER\s+(\S+)", line, re.IGNORECASE)
        if m:
            delimiter = m.group(1)
            i += 1
            continue

        cur.append(line)
        joined = "\n".join(cur)
        if joined.strip().endswith(delimiter):
            # remove the trailing delimiter
            stmt = joined.rstrip()
            if stmt.endswith(delimiter):
                stmt = stmt[: -len(delimiter)]
            statements.append(stmt.strip())
            cur = []
        i += 1

    # any leftover
    if cur:
        leftover = "\n".join(cur).strip()
        if leftover:
            statements.append(leftover)

    return statements


def init_db():
    print(f"Reading SQL from: {SQL_FILE}")
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        sql_text = f.read()

    stmts = split_sql_statements(sql_text)
    print(f"Found {len(stmts)} statements to execute.")

    conn = get_connection()
    try:
        cur = conn.cursor()
        for idx, stmt in enumerate(stmts, 1):
            s = stmt.strip()
            if not s:
                continue
            try:
                print(f"Executing statement {idx}/{len(stmts)}")
                cur.execute(s)
                # When creating procedures/functions/triggers, some DBs require execute many; commit after
                conn.commit()
            except Exception as e:
                print(f"Statement {idx} failed: {e}\nStatement:\n{s[:200]}...\nContinuing...")
        print("Initialization complete.")
    finally:
        conn.close()


if __name__ == '__main__':
    init_db()
