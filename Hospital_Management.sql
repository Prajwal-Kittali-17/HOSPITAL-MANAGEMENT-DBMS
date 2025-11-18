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
-- Step 21: Trigger Action Log Table (For tracking trigger executions)
----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS TriggerActionLog (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    TriggerName VARCHAR(100),
    ActionType VARCHAR(50),
    TableName VARCHAR(100),
    RecordID INT,
    OldValue VARCHAR(255),
    NewValue VARCHAR(255),
    ActionTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PatientID INT
);

----------------------------------------------------------------
-- Step 22: Prescription Table
----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Prescription (
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
);

----------------------------------------------------------------
-- Step 23: Department Table
----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Department (
    DepartmentID INT AUTO_INCREMENT PRIMARY KEY,
    DepartmentName VARCHAR(100) UNIQUE,
    HeadDoctor INT,
    Phone VARCHAR(15),
    FOREIGN KEY (HeadDoctor) REFERENCES Doctor(DoctorID) ON DELETE SET NULL ON UPDATE CASCADE
);

----------------------------------------------------------------
-- Step 24: Hospital Rooms Table
----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Room (
    RoomID INT AUTO_INCREMENT PRIMARY KEY,
    RoomNumber VARCHAR(20) UNIQUE,
    RoomType ENUM('General', 'ICU', 'Private', 'Semi-Private'),
    Capacity INT,
    IsOccupied BOOLEAN DEFAULT FALSE,
    CurrentPatientID INT,
    DepartmentID INT,
    FOREIGN KEY (CurrentPatientID) REFERENCES Patient(PatientID) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID) ON DELETE SET NULL ON UPDATE CASCADE
);

----------------------------------------------------------------
-- Step 25: Lab Test Table
----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS LabTest (
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
);

----------------------------------------------------------------
-- Step 26: Insert Department Data
----------------------------------------------------------------
INSERT IGNORE INTO Department (DepartmentName, HeadDoctor, Phone) VALUES
('Cardiology', 1, '9111111111'),
('Neurology', 2, '9222222222'),
('Orthopedics', 3, '9333333333');

----------------------------------------------------------------
-- Step 27: Insert Room Data
----------------------------------------------------------------
INSERT IGNORE INTO Room (RoomNumber, RoomType, Capacity, DepartmentID) VALUES
('101', 'General', 2, 1),
('102', 'General', 2, 1),
('ICU-01', 'ICU', 1, 1),
('ICU-02', 'ICU', 1, 2),
('Private-01', 'Private', 1, 3);

----------------------------------------------------------------
-- Step 28: Insert Prescription Data
----------------------------------------------------------------
INSERT IGNORE INTO Prescription (PatientID, DoctorID, MedicineName, Dosage, Frequency, StartDate, EndDate) VALUES
(1, 1, 'Amlodipine', '5mg', 'Once daily', '2025-10-01', '2025-10-31'),
(2, 2, 'Sumatriptan', '50mg', 'As needed', '2025-10-03', '2025-10-31'),
(3, 1, 'Aspirin', '100mg', 'Once daily', '2025-10-05', '2025-10-31');

----------------------------------------------------------------
-- Step 29: Insert Lab Test Data
----------------------------------------------------------------
INSERT IGNORE INTO LabTest (PatientID, DoctorID, TestName, TestDate, Status, Result) VALUES
(1, 1, 'Blood Test (Complete Blood Count)', '2025-10-01', 'Completed', 'Normal'),
(2, 2, 'MRI Brain', '2025-10-03', 'Pending', NULL),
(3, 1, 'ECG', '2025-10-05', 'Completed', 'Abnormal - Follow up required'),
(4, 3, 'X-Ray Arm', '2025-10-07', 'Completed', 'Fracture confirmed');

----------------------------------------------------------------
-- Step 30: Additional Trigger - Log Prescription Addition
----------------------------------------------------------------
DELIMITER $$
CREATE TRIGGER TR_LOG_PRESCRIPTION_INSERT
AFTER INSERT ON Prescription
FOR EACH ROW
BEGIN
    INSERT INTO TriggerActionLog (TriggerName, ActionType, TableName, RecordID, NewValue, PatientID)
    VALUES ('TR_LOG_PRESCRIPTION_INSERT', 'INSERT', 'Prescription', NEW.PrescriptionID, 
            CONCAT('Medicine: ', NEW.MedicineName, ', Dosage: ', NEW.Dosage), NEW.PatientID);
END$$
DELIMITER ;

----------------------------------------------------------------
-- Step 31: Additional Trigger - Log Room Occupancy Change
----------------------------------------------------------------
DELIMITER $$
CREATE TRIGGER TR_LOG_ROOM_OCCUPANCY
AFTER UPDATE ON Room
FOR EACH ROW
BEGIN
    IF NEW.IsOccupied <> OLD.IsOccupied THEN
        INSERT INTO TriggerActionLog (TriggerName, ActionType, TableName, RecordID, OldValue, NewValue, PatientID)
        VALUES ('TR_LOG_ROOM_OCCUPANCY', 'UPDATE', 'Room', NEW.RoomID, 
                IF(OLD.IsOccupied, 'Occupied', 'Vacant'), IF(NEW.IsOccupied, 'Occupied', 'Vacant'), NEW.CurrentPatientID);
    END IF;
END$$
DELIMITER ;

----------------------------------------------------------------
-- Step 32: Trigger - Automatic Bill Update on Lab Test Completion
----------------------------------------------------------------
DELIMITER $$
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
END$$
DELIMITER ;

----------------------------------------------------------------
-- Step 33: View - Patient Room Status
----------------------------------------------------------------
CREATE OR REPLACE VIEW PatientRoomView AS
SELECT 
    p.PatientID,
    p.Name AS PatientName,
    r.RoomNumber,
    r.RoomType,
    d.DepartmentName,
    r.IsOccupied
FROM Patient p
LEFT JOIN Room r ON p.PatientID = r.CurrentPatientID
LEFT JOIN Department d ON r.DepartmentID = d.DepartmentID
WHERE r.IsOccupied = TRUE;

----------------------------------------------------------------
-- Step 34: View - Department Workload
----------------------------------------------------------------
CREATE OR REPLACE VIEW DepartmentWorkloadView AS
SELECT 
    d.DepartmentName,
    d.HeadDoctor,
    doc.Name AS HeadDoctorName,
    COUNT(DISTINCT a.AppointmentID) AS TotalAppointments,
    COUNT(DISTINCT r.RoomID) AS TotalRooms,
    SUM(CASE WHEN r.IsOccupied THEN 1 ELSE 0 END) AS OccupiedRooms
FROM Department d
LEFT JOIN Doctor doc ON d.HeadDoctor = doc.DoctorID
LEFT JOIN Doctor dept_doc ON d.DepartmentID = (SELECT DepartmentID FROM Room WHERE DepartmentID = d.DepartmentID LIMIT 1)
LEFT JOIN Appointment a ON dept_doc.DoctorID = a.DoctorID
LEFT JOIN Room r ON d.DepartmentID = r.DepartmentID
GROUP BY d.DepartmentID, d.DepartmentName, d.HeadDoctor, doc.Name;

----------------------------------------------------------------
-- END OF FILE
----------------------------------------------------------------
