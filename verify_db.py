#!/usr/bin/env python3
"""Verify that all required database tables and triggers exist."""

import mysql.connector
from db_config import get_connection

def verify_database():
    """Check if all required tables and triggers exist in the database."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # List of expected tables
        tables = [
            'Patient', 'Doctor', 'Appointment', 'MedicalRecord', 'Billing', 'Payment', 
            'Users', 'PaymentStatus', 'Prescription', 'Department', 'Room', 'LabTest', 
            'TriggerActionLog'
        ]
        
        # List of expected triggers
        triggers = [
            'TR_UPDATE_PAYMENT_STATUS', 'TR_LOG_PRESCRIPTION_INSERT', 
            'TR_LOG_ROOM_OCCUPANCY', 'TR_ADD_LAB_TEST_CHARGE'
        ]
        
        # List of expected routines (functions/procedures)
        routines = ['FN_GET_PATIENT_BALANCE', 'SP_ADD_NEW_DOCTOR']
        
        print("=" * 60)
        print("DATABASE VERIFICATION REPORT")
        print("=" * 60)
        
        # Check tables
        print("\n[TABLES]:")
        cur.execute("""SELECT TABLE_NAME FROM information_schema.TABLES 
                      WHERE TABLE_SCHEMA = %s""", ('hospital_management',))
        existing_tables = set(row[0] for row in cur.fetchall())
        
        for table in tables:
            status = "[OK]" if table in existing_tables else "[MISSING]"
            print(f"  {table:<25} {status}")
        
        # Check triggers
        print("\n[TRIGGERS]:")
        cur.execute("""SELECT TRIGGER_NAME FROM information_schema.TRIGGERS 
                      WHERE TRIGGER_SCHEMA = %s""", ('hospital_management',))
        existing_triggers = set(row[0] for row in cur.fetchall())
        
        for trigger in triggers:
            status = "[OK]" if trigger in existing_triggers else "[MISSING]"
            print(f"  {trigger:<35} {status}")
        
        # Check routines
        print("\n[FUNCTIONS/PROCEDURES]:")
        cur.execute("""SELECT ROUTINE_NAME FROM information_schema.ROUTINES 
                      WHERE ROUTINE_SCHEMA = %s""", ('hospital_management',))
        existing_routines = set(row[0] for row in cur.fetchall())
        
        for routine in routines:
            status = "[OK]" if routine in existing_routines else "[MISSING]"
            print(f"  {routine:<35} {status}")
        
        # Summary
        missing_tables = set(tables) - existing_tables
        missing_triggers = set(triggers) - existing_triggers
        missing_routines = set(routines) - existing_routines
        
        print("\n" + "=" * 60)
        if not missing_tables and not missing_triggers and not missing_routines:
            print("[SUCCESS] ALL DATABASE OBJECTS VERIFIED!")
        else:
            print("[ERROR] MISSING DATABASE OBJECTS:")
            if missing_tables:
                print(f"  Tables: {', '.join(missing_tables)}")
            if missing_triggers:
                print(f"  Triggers: {', '.join(missing_triggers)}")
            if missing_routines:
                print(f"  Routines: {', '.join(missing_routines)}")
        print("=" * 60)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Error connecting to database: {e}")
        print("Make sure MySQL is running and db_config.py is properly configured.")

if __name__ == "__main__":
    verify_database()
