#!/usr/bin/env python3
"""Import SQL schema into the database, handling comments and delimiters properly."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_config import get_connection

def import_sql_file(filepath):
    """Import SQL file into database, properly handling comments."""
    with open(filepath, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Split by statements more carefully
    statements = []
    current_stmt = []
    in_comment = False
    
    for line in sql_content.split('\n'):
        stripped = line.strip()
        
        # Skip comment lines
        if stripped.startswith('--'):
            continue
        if stripped.startswith('/*'):
            in_comment = True
            continue
        if '*/' in stripped:
            in_comment = False
            continue
        if in_comment:
            continue
        
        # Handle DELIMITER directives
        if stripped.upper().startswith('DELIMITER'):
            continue
        
        # Skip empty lines
        if not stripped:
            continue
        
        current_stmt.append(line)
        
        # Check if statement ends with semicolon
        if stripped.endswith(';'):
            stmt = '\n'.join(current_stmt).strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
            current_stmt = []
    
    # Add any remaining statement
    if current_stmt:
        stmt = '\n'.join(current_stmt).strip()
        if stmt and not stmt.startswith('--'):
            statements.append(stmt)
    
    # Execute statements
    conn = get_connection()
    try:
        cur = conn.cursor()
        print(f"Found {len(statements)} SQL statements to execute")
        
        success_count = 0
        fail_count = 0
        
        for idx, stmt in enumerate(statements, 1):
            if not stmt.strip():
                continue
            
            try:
                print(f"[{idx}/{len(statements)}] Executing...", end='', flush=True)
                cur.execute(stmt)
                conn.commit()
                print(" OK")
                success_count += 1
            except Exception as e:
                print(f" ERROR: {str(e)[:80]}")
                fail_count += 1
                # Continue on error to process remaining statements
        
        print(f"\n{'='*60}")
        print(f"Execution Complete: {success_count} succeeded, {fail_count} failed")
        print(f"{'='*60}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    sql_file = os.path.join(os.path.dirname(__file__), 'Hospital_Management.sql')
    import_sql_file(sql_file)
