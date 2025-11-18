# utils/db_helpers.py
import pandas as pd
from db_config import get_connection

def fetch_all(query, params=None):
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn, params=params)
        return df
    finally:
        conn.close()

def fetch_one(query, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()
    finally:
        conn.close()

def execute_query(query, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()

def call_procedure(proc_name, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.callproc(proc_name, params or [])
        results = []
        for rs in cur.stored_results():
            results.append(rs.fetchall())
        conn.commit()
        return results
    finally:
        conn.close()

def call_function(func_name, params=None):
    conn = get_connection()
    try:
        placeholders = ", ".join(["%s"] * len(params))
        query = f"SELECT {func_name}({placeholders})"
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()[0]
    finally:
        conn.close()


def ensure_db_objects():
    """Ensure required DB objects (tables, trigger, function, procedure, paymentstatus) exist.
    This will create missing objects. Safe to call multiple times.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        # Ensure PaymentStatus table exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS PaymentStatus (
                PatientID INT PRIMARY KEY,
                LatestBillAmount DECIMAL(10,2),
                PaymentComplete BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (PatientID) REFERENCES Patient(PatientID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)

        # Ensure TriggerActionLog table exists
        cur.execute("""
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
            )
        """)

        # Ensure Prescription table exists
        cur.execute("""
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
            )
        """)

        # Ensure Department table exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Department (
                DepartmentID INT AUTO_INCREMENT PRIMARY KEY,
                DepartmentName VARCHAR(100) UNIQUE,
                HeadDoctor INT,
                Phone VARCHAR(15),
                FOREIGN KEY (HeadDoctor) REFERENCES Doctor(DoctorID) ON DELETE SET NULL ON UPDATE CASCADE
            )
        """)

        # Ensure Room table exists
        cur.execute("""
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
            )
        """)

        # Ensure LabTest table exists
        cur.execute("""
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
            )
        """)

        # Populate or update PaymentStatus from Billing & Payment
        try:
            cur.execute("""
                INSERT INTO PaymentStatus (PatientID, LatestBillAmount, PaymentComplete)
                SELECT 
                    B.PatientID,
                    B.Amount,
                    CASE WHEN (SELECT IFNULL(SUM(AmountPaid),0) FROM Payment WHERE PatientID = B.PatientID) >= B.Amount THEN TRUE ELSE FALSE END
                FROM Billing B
                ON DUPLICATE KEY UPDATE
                    LatestBillAmount = VALUES(LatestBillAmount),
                    PaymentComplete = VALUES(PaymentComplete)
            """)
        except:
            pass

        # Create function if missing
        cur.execute("SELECT ROUTINE_NAME FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA=%s AND ROUTINE_NAME=%s", ('hospital_management','FN_GET_PATIENT_BALANCE'))
        if not cur.fetchone():
            func_sql = """
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
            """
            cur.execute(func_sql)

        # Create procedure if missing
        cur.execute("SELECT ROUTINE_NAME FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA=%s AND ROUTINE_NAME=%s", ('hospital_management','SP_ADD_NEW_DOCTOR'))
        if not cur.fetchone():
            proc_sql = """
            CREATE PROCEDURE SP_ADD_NEW_DOCTOR(IN n VARCHAR(100), IN s VARCHAR(100), IN p VARCHAR(15))
            BEGIN
                INSERT INTO Doctor (Name, Specialization, Phone)
                VALUES (n, s, p);

                SELECT 'SUCCESS' AS status, DoctorID, Name, Specialization
                FROM Doctor
                WHERE DoctorID = LAST_INSERT_ID();
            END
            """
            cur.execute(proc_sql)

        # Create trigger if missing
        cur.execute("SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=%s AND TRIGGER_NAME=%s", ('hospital_management','TR_UPDATE_PAYMENT_STATUS'))
        if not cur.fetchone():
            trig_sql = """
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
            """
            cur.execute(trig_sql)

        # Create TR_LOG_PRESCRIPTION_INSERT trigger if missing
        cur.execute("SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=%s AND TRIGGER_NAME=%s", ('hospital_management','TR_LOG_PRESCRIPTION_INSERT'))
        if not cur.fetchone():
            trig_presc = """
            CREATE TRIGGER TR_LOG_PRESCRIPTION_INSERT
            AFTER INSERT ON Prescription
            FOR EACH ROW
            BEGIN
                INSERT INTO TriggerActionLog (TriggerName, ActionType, TableName, RecordID, NewValue, PatientID)
                VALUES ('TR_LOG_PRESCRIPTION_INSERT', 'INSERT', 'Prescription', NEW.PrescriptionID, 
                        CONCAT('Medicine: ', NEW.MedicineName, ', Dosage: ', NEW.Dosage), NEW.PatientID);
            END
            """
            try:
                cur.execute(trig_presc)
            except:
                pass

        # Create TR_LOG_ROOM_OCCUPANCY trigger if missing
        cur.execute("SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=%s AND TRIGGER_NAME=%s", ('hospital_management','TR_LOG_ROOM_OCCUPANCY'))
        if not cur.fetchone():
            trig_room = """
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
            """
            try:
                cur.execute(trig_room)
            except:
                pass

        # Create TR_ADD_LAB_TEST_CHARGE trigger if missing
        cur.execute("SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=%s AND TRIGGER_NAME=%s", ('hospital_management','TR_ADD_LAB_TEST_CHARGE'))
        if not cur.fetchone():
            trig_lab = """
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
            """
            try:
                cur.execute(trig_lab)
            except:
                pass

        conn.commit()
    except Exception as e:
        print(f"Error in ensure_db_objects: {e}")
    finally:
        conn.close()
