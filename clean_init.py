#!/usr/bin/env python3
"""Clean database initialization - drops and recreates everything."""

import mysql.connector
from mysql.connector import Error

def init_clean():
    """Drop and recreate the database from scratch."""
    # Connect without specifying database
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="@Prajwal2728",
            auth_plugin="mysql_native_password"
        )
        cur = conn.cursor()
        
        print("Dropping database if exists...")
        cur.execute("DROP DATABASE IF EXISTS hospital_management")
        conn.commit()
        
        print("Creating database...")
        cur.execute("CREATE DATABASE hospital_management")
        conn.commit()
        
        print("Selecting database...")
        cur.execute("USE hospital_management")
        
        print("Creating Patient table...")
        cur.execute("""
            CREATE TABLE Patient (
                PatientID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(100),
                Age INT,
                Gender VARCHAR(10),
                Address VARCHAR(255),
                Phone VARCHAR(15)
            )
        """)
        
        print("Creating Doctor table...")
        cur.execute("""
            CREATE TABLE Doctor (
                DoctorID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(100),
                Specialization VARCHAR(100),
                Phone VARCHAR(15)
            )
        """)
        
        print("Creating Appointment table...")
        cur.execute("""
            CREATE TABLE Appointment (
                AppointmentID INT AUTO_INCREMENT PRIMARY KEY,
                PatientID INT,
                DoctorID INT,
                AppointmentDate DATE,
                FOREIGN KEY (PatientID) REFERENCES Patient(PatientID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        print("Creating MedicalRecord table...")
        cur.execute("""
            CREATE TABLE MedicalRecord (
                RecordID INT AUTO_INCREMENT PRIMARY KEY,
                PatientID INT,
                DoctorID INT,
                Diagnosis VARCHAR(255),
                Treatment VARCHAR(255),
                FOREIGN KEY (PatientID) REFERENCES Patient(PatientID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        print("Creating Billing table...")
        cur.execute("""
            CREATE TABLE Billing (
                BillID INT AUTO_INCREMENT PRIMARY KEY,
                PatientID INT,
                Amount DECIMAL(10,2),
                BillingDate DATE,
                FOREIGN KEY (PatientID) REFERENCES Patient(PatientID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        print("Creating Payment table...")
        cur.execute("""
            CREATE TABLE Payment (
                PaymentID INT AUTO_INCREMENT PRIMARY KEY,
                PatientID INT,
                AmountPaid DECIMAL(10,2),
                PaymentDate DATE,
                FOREIGN KEY (PatientID) REFERENCES Patient(PatientID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        print("Creating Users table...")
        cur.execute("""
            CREATE TABLE Users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE,
                password_hash VARCHAR(255),
                role VARCHAR(50)
            )
        """)
        
        print("Creating PaymentStatus table...")
        cur.execute("""
            CREATE TABLE PaymentStatus (
                PatientID INT PRIMARY KEY,
                LatestBillAmount DECIMAL(10,2),
                PaymentComplete BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (PatientID) REFERENCES Patient(PatientID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        print("Creating TriggerActionLog table...")
        cur.execute("""
            CREATE TABLE TriggerActionLog (
                LogID INT AUTO_INCREMENT PRIMARY KEY,
                TriggerName VARCHAR(100),
                ActionType VARCHAR(50),
                TableName VARCHAR(100),
                RecordID INT,
                OldValue VARCHAR(255),
                NewValue VARCHAR(255),
                ActionTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PatientID INT
            )
        """)
        
        print("Creating Prescription table...")
        cur.execute("""
            CREATE TABLE Prescription (
                PrescriptionID INT AUTO_INCREMENT PRIMARY KEY,
                PatientID INT NOT NULL,
                DoctorID INT NOT NULL,
                MedicineName VARCHAR(100),
                Dosage VARCHAR(50),
                Frequency VARCHAR(50),
                StartDate DATE,
                EndDate DATE,
                Notes VARCHAR(255),
                FOREIGN KEY (PatientID) REFERENCES Patient(PatientID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        print("Creating Department table...")
        cur.execute("""
            CREATE TABLE Department (
                DepartmentID INT AUTO_INCREMENT PRIMARY KEY,
                DepartmentName VARCHAR(100) UNIQUE,
                HeadDoctor INT,
                Phone VARCHAR(15),
                FOREIGN KEY (HeadDoctor) REFERENCES Doctor(DoctorID) ON DELETE SET NULL ON UPDATE CASCADE
            )
        """)
        
        print("Creating Room table...")
        cur.execute("""
            CREATE TABLE Room (
                RoomID INT AUTO_INCREMENT PRIMARY KEY,
                RoomNumber VARCHAR(20) UNIQUE,
                RoomType ENUM('General', 'ICU', 'Private', 'Semi-Private'),
                Capacity INT,
                IsOccupied BOOLEAN DEFAULT FALSE,
                CurrentPatientID INT,
                DepartmentID INT,
                FOREIGN KEY (CurrentPatientID) REFERENCES Patient(PatientID) ON DELETE SET NULL ON UPDATE CASCADE,
                FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID) ON DELETE SET NULL ON UPDATE CASCADE
            )
        """)
        
        print("Creating LabTest table...")
        cur.execute("""
            CREATE TABLE LabTest (
                TestID INT AUTO_INCREMENT PRIMARY KEY,
                PatientID INT NOT NULL,
                DoctorID INT NOT NULL,
                TestName VARCHAR(100),
                TestDate DATE,
                Result VARCHAR(255),
                Status ENUM('Pending', 'Completed', 'Cancelled') DEFAULT 'Pending',
                Notes VARCHAR(255),
                FOREIGN KEY (PatientID) REFERENCES Patient(PatientID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        # Insert sample data
        print("Inserting sample users...")
        cur.execute("""
            INSERT IGNORE INTO Users (username, password_hash, role)
            VALUES ('admin', SHA2('admin123', 256), 'admin')
        """)
        
        # Create triggers
        print("Creating TR_UPDATE_PAYMENT_STATUS trigger...")
        cur.execute("""
            CREATE TRIGGER TR_UPDATE_PAYMENT_STATUS
            AFTER INSERT ON Payment
            FOR EACH ROW
            BEGIN
                DECLARE v_billed DECIMAL(10, 2);
                DECLARE v_paid DECIMAL(10, 2);

                SELECT IFNULL(SUM(AmountPaid), 0)
                INTO v_paid
                FROM Payment
                WHERE PatientID = NEW.PatientID;

                SELECT LatestBillAmount
                INTO v_billed
                FROM PaymentStatus
                WHERE PatientID = NEW.PatientID;

                UPDATE PaymentStatus
                SET PaymentComplete = (v_paid >= v_billed)
                WHERE PatientID = NEW.PatientID;
            END
        """)
        
        print("Creating TR_LOG_PRESCRIPTION_INSERT trigger...")
        cur.execute("""
            CREATE TRIGGER TR_LOG_PRESCRIPTION_INSERT
            AFTER INSERT ON Prescription
            FOR EACH ROW
            BEGIN
                INSERT INTO TriggerActionLog (TriggerName, ActionType, TableName, RecordID, NewValue, PatientID)
                VALUES ('TR_LOG_PRESCRIPTION_INSERT', 'INSERT', 'Prescription', NEW.PrescriptionID, 
                        CONCAT('Medicine: ', NEW.MedicineName, ', Dosage: ', NEW.Dosage), NEW.PatientID);
            END
        """)
        
        print("Creating TR_LOG_ROOM_OCCUPANCY trigger...")
        cur.execute("""
            CREATE TRIGGER TR_LOG_ROOM_OCCUPANCY
            AFTER UPDATE ON Room
            FOR EACH ROW
            BEGIN
                IF NEW.IsOccupied <> OLD.IsOccupied THEN
                    INSERT INTO TriggerActionLog (TriggerName, ActionType, TableName, RecordID, OldValue, NewValue, PatientID)
                    VALUES ('TR_LOG_ROOM_OCCUPANCY', 'UPDATE', 'Room', NEW.RoomID, 
                            IF(OLD.IsOccupied, 'Occupied', 'Vacant'), IF(NEW.IsOccupied, 'Occupied', 'Vacant'), NEW.CurrentPatientID);
                END IF;
            END
        """)
        
        print("Creating TR_ADD_LAB_TEST_CHARGE trigger...")
        cur.execute("""
            CREATE TRIGGER TR_ADD_LAB_TEST_CHARGE
            AFTER UPDATE ON LabTest
            FOR EACH ROW
            BEGIN
                DECLARE lab_charge DECIMAL(10,2);
                
                IF NEW.Status = 'Completed' AND OLD.Status <> 'Completed' THEN
                    SET lab_charge = 500.00;
                    INSERT INTO Billing (PatientID, Amount, BillingDate) 
                    VALUES (NEW.PatientID, lab_charge, CURDATE());
                    
                    INSERT INTO TriggerActionLog (TriggerName, ActionType, TableName, RecordID, NewValue, PatientID)
                    VALUES ('TR_ADD_LAB_TEST_CHARGE', 'INSERT', 'Billing', LAST_INSERT_ID(), 
                            CONCAT('Lab Test Charge: $', lab_charge), NEW.PatientID);
                END IF;
            END
        """)
        
        # Create function
        print("Creating FN_GET_PATIENT_BALANCE function...")
        cur.execute("""
            CREATE FUNCTION FN_GET_PATIENT_BALANCE(p_id INT)
            RETURNS DECIMAL(10,2)
            READS SQL DATA
            BEGIN
                DECLARE billed DECIMAL(10,2);
                DECLARE paid DECIMAL(10,2);

                SELECT IFNULL(SUM(Amount),0) INTO billed FROM Billing WHERE PatientID = p_id;
                SELECT IFNULL(SUM(AmountPaid),0) INTO paid FROM Payment WHERE PatientID = p_id;

                RETURN billed - paid;
            END
        """)
        
        # Create procedure
        print("Creating SP_ADD_NEW_DOCTOR procedure...")
        cur.execute("""
            CREATE PROCEDURE SP_ADD_NEW_DOCTOR(IN n VARCHAR(100), IN s VARCHAR(100), IN p VARCHAR(15))
            BEGIN
                INSERT INTO Doctor (Name, Specialization, Phone)
                VALUES (n, s, p);

                SELECT 'SUCCESS' AS status, DoctorID, Name, Specialization
                FROM Doctor
                WHERE DoctorID = LAST_INSERT_ID();
            END
        """)
        
        conn.commit()
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("="*60)
        
        cur.close()
        conn.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    init_clean()
