#!/usr/bin/env python3
"""Add sample data to the database for testing."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_config import get_connection

def seed_data():
    """Insert sample data into the database."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        print("Seeding sample data...")
        
        # Insert sample patients
        print("  Adding patients...")
        cur.execute("INSERT INTO Patient (Name, Age, Gender, Address, Phone) VALUES (%s, %s, %s, %s, %s)",
            ("John Doe", 45, "Male", "123 Main St", "555-0001"))
        cur.execute("INSERT INTO Patient (Name, Age, Gender, Address, Phone) VALUES (%s, %s, %s, %s, %s)",
            ("Jane Smith", 38, "Female", "456 Oak Ave", "555-0002"))
        cur.execute("INSERT INTO Patient (Name, Age, Gender, Address, Phone) VALUES (%s, %s, %s, %s, %s)",
            ("Bob Johnson", 65, "Male", "789 Elm St", "555-0003"))
        
        # Insert sample doctors
        print("  Adding doctors...")
        cur.execute("INSERT INTO Doctor (Name, Specialization, Phone) VALUES (%s, %s, %s)",
            ("Dr. Alice Brown", "Cardiology", "555-1001"))
        cur.execute("INSERT INTO Doctor (Name, Specialization, Phone) VALUES (%s, %s, %s)",
            ("Dr. Charlie Davis", "General Surgery", "555-1002"))
        cur.execute("INSERT INTO Doctor (Name, Specialization, Phone) VALUES (%s, %s, %s)",
            ("Dr. Eve Wilson", "Neurology", "555-1003"))
        
        # Insert departments
        print("  Adding departments...")
        cur.execute("INSERT INTO Department (DepartmentName, HeadDoctor, Phone) VALUES (%s, %s, %s)",
            ("Cardiology", 1, "555-2001"))
        cur.execute("INSERT INTO Department (DepartmentName, HeadDoctor, Phone) VALUES (%s, %s, %s)",
            ("Surgery", 2, "555-2002"))
        cur.execute("INSERT INTO Department (DepartmentName, HeadDoctor, Phone) VALUES (%s, %s, %s)",
            ("Neurology", 3, "555-2003"))
        
        # Insert rooms
        print("  Adding rooms...")
        cur.execute("INSERT INTO Room (RoomNumber, RoomType, Capacity, IsOccupied, DepartmentID) VALUES (%s, %s, %s, %s, %s)",
            ("101", "General", 2, False, 1))
        cur.execute("INSERT INTO Room (RoomNumber, RoomType, Capacity, IsOccupied, DepartmentID) VALUES (%s, %s, %s, %s, %s)",
            ("102", "ICU", 1, False, 1))
        cur.execute("INSERT INTO Room (RoomNumber, RoomType, Capacity, IsOccupied, DepartmentID) VALUES (%s, %s, %s, %s, %s)",
            ("201", "Private", 1, False, 2))
        
        # Insert appointments
        print("  Adding appointments...")
        cur.execute("INSERT INTO Appointment (PatientID, DoctorID, AppointmentDate) VALUES (%s, %s, %s)",
            (1, 1, "2025-01-15"))
        cur.execute("INSERT INTO Appointment (PatientID, DoctorID, AppointmentDate) VALUES (%s, %s, %s)",
            (2, 2, "2025-01-16"))
        cur.execute("INSERT INTO Appointment (PatientID, DoctorID, AppointmentDate) VALUES (%s, %s, %s)",
            (3, 3, "2025-01-17"))
        
        # Insert billing records
        print("  Adding billing records...")
        cur.execute("INSERT INTO Billing (PatientID, Amount, BillingDate) VALUES (%s, %s, %s)",
            (1, 500.00, "2025-01-10"))
        cur.execute("INSERT INTO Billing (PatientID, Amount, BillingDate) VALUES (%s, %s, %s)",
            (2, 750.00, "2025-01-11"))
        cur.execute("INSERT INTO Billing (PatientID, Amount, BillingDate) VALUES (%s, %s, %s)",
            (3, 1000.00, "2025-01-12"))
        
        # Insert payments
        print("  Adding payments...")
        cur.execute("INSERT INTO Payment (PatientID, AmountPaid, PaymentDate) VALUES (%s, %s, %s)",
            (1, 300.00, "2025-01-13"))
        cur.execute("INSERT INTO Payment (PatientID, AmountPaid, PaymentDate) VALUES (%s, %s, %s)",
            (2, 750.00, "2025-01-14"))
        
        # Insert prescriptions
        print("  Adding prescriptions...")
        cur.execute("INSERT INTO Prescription (PatientID, DoctorID, MedicineName, Dosage, Frequency, StartDate, EndDate) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (1, 1, "Aspirin", "100mg", "Once daily", "2025-01-10", "2025-02-10"))
        cur.execute("INSERT INTO Prescription (PatientID, DoctorID, MedicineName, Dosage, Frequency, StartDate, EndDate) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (2, 2, "Ibuprofen", "200mg", "Twice daily", "2025-01-11", "2025-01-25"))
        
        # Insert lab tests
        print("  Adding lab tests...")
        cur.execute("INSERT INTO LabTest (PatientID, DoctorID, TestName, TestDate, Status) VALUES (%s, %s, %s, %s, %s)",
            (1, 1, "Blood Test", "2025-01-15", "Pending"))
        cur.execute("INSERT INTO LabTest (PatientID, DoctorID, TestName, TestDate, Status, Result) VALUES (%s, %s, %s, %s, %s, %s)",
            (2, 2, "X-Ray", "2025-01-16", "Completed", "Normal"))
        
        # Insert medical records
        print("  Adding medical records...")
        cur.execute("INSERT INTO MedicalRecord (PatientID, DoctorID, Diagnosis, Treatment) VALUES (%s, %s, %s, %s)",
            (1, 1, "Hypertension", "Medication and lifestyle changes"))
        cur.execute("INSERT INTO MedicalRecord (PatientID, DoctorID, Diagnosis, Treatment) VALUES (%s, %s, %s, %s)",
            (2, 2, "Appendicitis", "Emergency surgery"))
        
        # Insert PaymentStatus records
        print("  Adding payment status...")
        cur.execute("INSERT INTO PaymentStatus (PatientID, LatestBillAmount, PaymentComplete) VALUES (%s, %s, %s)",
            (1, 500.00, False))
        cur.execute("INSERT INTO PaymentStatus (PatientID, LatestBillAmount, PaymentComplete) VALUES (%s, %s, %s)",
            (2, 750.00, True))
        cur.execute("INSERT INTO PaymentStatus (PatientID, LatestBillAmount, PaymentComplete) VALUES (%s, %s, %s)",
            (3, 1000.00, False))
        
        conn.commit()
        print("\n" + "="*60)
        print("SAMPLE DATA SEEDED SUCCESSFULLY!")
        print("="*60)
        
        cur.close()
        
    finally:
        conn.close()

if __name__ == "__main__":
    seed_data()
