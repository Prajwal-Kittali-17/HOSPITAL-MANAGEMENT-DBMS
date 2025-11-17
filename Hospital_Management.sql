----------------------------------------------------------------
-- HOSPITAL MANAGEMENT SYSTEM DATABASE SCRIPT
----------------------------------------------------------------

-- Step 1: Create the Database
----------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS hospital_management;
USE hospital_management;

----------------------------------------------------------------
-- Step 2: Drop Tables (order matters)
----------------------------------------------------------------
DROP TABLE IF EXISTS PaymentStatus;
DROP TABLE IF EXISTS Payment;
DROP TABLE IF EXISTS Billing;
DROP TABLE IF EXISTS MedicalRecord;
DROP TABLE IF EXISTS Appointment;
DROP TABLE IF EXISTS Doctor;
DROP TABLE IF EXISTS Patient;
DROP TABLE IF EXISTS Users;

----------------------------------------------------------------
-- Step 3: Patient Table
----------------------------------------------------------------
CREATE TABLE Patient (
    PatientID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100),
    Age INT,
    Gender VARCHAR(10),
    Address VARCHAR(255),
    Phone VARCHAR(15)
);

----------------------------------------------------------------
-- Step 4: Doctor Table
----------------------------------------------------------------
CREATE TABLE Doctor (
    DoctorID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100),
    Specialization VARCHAR(100),
    Phone VARCHAR(15)
);

----------------------------------------------------------------
-- Step 5: Appointment Table
----------------------------------------------------------------
CREATE TABLE Appointment (
    AppointmentID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT,
    DoctorID INT,
    AppointmentDate DATE,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

----------------------------------------------------------------
-- Step 6: MedicalRecord Table
----------------------------------------------------------------
CREATE TABLE MedicalRecord (
    RecordID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT,
    DoctorID INT,
    Diagnosis VARCHAR(255),
    Treatment VARCHAR(255),
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

----------------------------------------------------------------
-- Step 7: Billing Table
----------------------------------------------------------------
CREATE TABLE Billing (
    BillID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT,
    Amount DECIMAL(10,2),
    BillingDate DATE,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

----------------------------------------------------------------
-- Step 8: Payment Table
----------------------------------------------------------------
CREATE TABLE Payment (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT,
    AmountPaid DECIMAL(10,2),
    PaymentDate DATE,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

----------------------------------------------------------------
-- Step 9: Users Table (For login)
----------------------------------------------------------------
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'doctor', 'staff') NOT NULL
);

INSERT IGNORE INTO Users (username, password_hash, role)
VALUES ('admin', SHA2('admin123', 256), 'admin');

----------------------------------------------------------------
-- Step 10: Insert Patient Data
----------------------------------------------------------------
INSERT INTO Patient (Name, Age, Gender, Address, Phone) VALUES
('Aarav Sharma', 28, 'Male', 'Bangalore', '9876543210'),
('Priya Mehta', 34, 'Female', 'Mumbai', '9988776655'),
('Rohan Patel', 41, 'Male', 'Ahmedabad', '9123456789'),
('Ananya Reddy', 25, 'Female', 'Hyderabad', '9001122334'),
('Karan Singh', 38, 'Male', 'Delhi', '9898989898'),
('Ishita Das', 29, 'Female', 'Kolkata', '9123123123'),
('Rahul Nair', 33, 'Male', 'Kochi', '9333344444'),
('Sneha Iyer', 27, 'Female', 'Chennai', '9555566666');

----------------------------------------------------------------
-- Step 11: Insert Doctor Data
----------------------------------------------------------------
INSERT INTO Doctor (Name, Specialization, Phone) VALUES
('Dr. Arjun Rao', 'Cardiology', '9111111111'),
('Dr. Neha Kapoor', 'Neurology', '9222222222'),
('Dr. Vikram Desai', 'Orthopedics', '9333333333'),
('Dr. Meera Menon', 'Dermatology', '9444444444'),
('Dr. Rajesh Khanna', 'Pediatrics', '9555555555'),
('Dr. Pooja Bansal', 'ENT', '9666666666');

----------------------------------------------------------------
-- Step 12: Insert Appointment Data
----------------------------------------------------------------
INSERT INTO Appointment (PatientID, DoctorID, AppointmentDate) VALUES
(1, 1, '2025-10-01'),
(2, 2, '2025-10-03'),
(3, 1, '2025-10-05'),
(4, 3, '2025-10-07'),
(5, 4, '2025-10-09'),
(6, 5, '2025-10-10'),
(7, 6, '2025-10-11'),
(8, 3, '2025-10-12');

----------------------------------------------------------------
-- Step 13: Insert Medical Record Data
----------------------------------------------------------------
INSERT INTO MedicalRecord (PatientID, DoctorID, Diagnosis, Treatment) VALUES
(1, 1, 'High Blood Pressure', 'Prescribed Amlodipine 5mg daily'),
(2, 2, 'Migraine', 'Prescribed Sumatriptan'),
(3, 1, 'Chest Pain', 'Referred for ECG'),
(4, 3, 'Fracture (Arm)', 'Applied cast'),
(5, 4, 'Skin Allergy', 'Antihistamines and cream'),
(6, 5, 'Fever', 'Paracetamol 500mg'),
(7, 6, 'Ear Infection', 'Antibiotic drops'),
(8, 3, 'Joint Pain', 'Physiotherapy');

----------------------------------------------------------------
-- Step 14: Insert Billing Data
----------------------------------------------------------------
INSERT INTO Billing (PatientID, Amount, BillingDate) VALUES
(1, 1800.00, '2025-10-01'),
(2, 2300.00, '2025-10-03'),
(3, 2500.00, '2025-10-05'),
(4, 2700.00, '2025-10-07'),
(5, 1900.00, '2025-10-09'),
(6, 2200.00, '2025-10-10'),
(7, 3100.00, '2025-10-11'),
(8, 2800.00, '2025-10-12');

----------------------------------------------------------------
-- Step 15: Insert Payment Data
----------------------------------------------------------------
INSERT INTO Payment (PatientID, AmountPaid, PaymentDate) VALUES
(1, 1800.00, '2025-10-01'),
(2, 2300.00, '2025-10-03'),
(3, 2000.00, '2025-10-05'),
(4, 2700.00, '2025-10-07'),
(5, 1900.00, '2025-10-09'),
(6, 2000.00, '2025-10-10'),
(7, 3000.00, '2025-10-11'),
(8, 2800.00, '2025-10-12');

----------------------------------------------------------------
-- Step 16: PaymentStatus Table
----------------------------------------------------------------
CREATE TABLE PaymentStatus (
    PatientID INT PRIMARY KEY,
    LatestBillAmount DECIMAL(10, 2),
    PaymentComplete BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

INSERT INTO PaymentStatus (PatientID, LatestBillAmount, PaymentComplete)
SELECT 
    B.PatientID, 
    B.Amount,
    CASE 
        WHEN (SELECT SUM(AmountPaid) FROM Payment WHERE PatientID = B.PatientID) >= B.Amount THEN TRUE
        ELSE FALSE
    END
FROM Billing B;

----------------------------------------------------------------
-- Step 17: Trigger
----------------------------------------------------------------
DELIMITER $$
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
END$$
DELIMITER ;

----------------------------------------------------------------
-- Step 18: Stored Function
----------------------------------------------------------------
DELIMITER $$
CREATE FUNCTION FN_GET_PATIENT_BALANCE(p_id INT)
RETURNS DECIMAL(10,2)
READS SQL DATA
BEGIN
    DECLARE billed DECIMAL(10,2);
    DECLARE paid DECIMAL(10,2);

    SELECT IFNULL(SUM(Amount),0) INTO billed FROM Billing WHERE PatientID = p_id;
    SELECT IFNULL(SUM(AmountPaid),0) INTO paid FROM Payment WHERE PatientID = p_id;

    RETURN billed - paid;
END$$
DELIMITER ;

----------------------------------------------------------------
-- Step 19: Procedure
----------------------------------------------------------------
DELIMITER $$
CREATE PROCEDURE SP_ADD_NEW_DOCTOR(IN n VARCHAR(100), IN s VARCHAR(100), IN p VARCHAR(15))
BEGIN
    INSERT INTO Doctor (Name, Specialization, Phone)
    VALUES (n, s, p);

    SELECT 'SUCCESS', DoctorID, Name, Specialization
    FROM Doctor
    WHERE DoctorID = LAST_INSERT_ID();
END$$
DELIMITER ;

----------------------------------------------------------------
-- Step 20: View
----------------------------------------------------------------
CREATE OR REPLACE VIEW PatientAppointmentView AS
SELECT 
    p.PatientID,
    p.Name AS PatientName,
    d.Name AS DoctorName,
    d.Specialization,
    a.AppointmentDate,
    b.Amount AS BillAmount,
    b.BillingDate
FROM Patient p
JOIN Appointment a ON p.PatientID = a.PatientID
JOIN Doctor d ON a.DoctorID = d.DoctorID
JOIN Billing b ON p.PatientID = b.PatientID;

----------------------------------------------------------------
-- END OF FILE
----------------------------------------------------------------
