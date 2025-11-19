"""
Generate Relational Mapping Diagram for Hospital Management DBMS
Shows all 13 tables with their attributes, keys, and relationships
"""

import os
import subprocess

# Relational Schema Diagram in Graphviz DOT format
relational_diagram_dot = """
digraph RelationalMapping {
    rankdir=LR;
    node [shape=plaintext, fontname="Arial", fontsize=9];
    edge [fontname="Arial", fontsize=8, style=bold];
    
    // Patient Table
    Patient [label=<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#FFE6E6">
            <TR><TD COLSPAN="2" BGCOLOR="#FF6666"><B>Patient</B></TD></TR>
            <TR><TD>PatientID</TD><TD>INT (PK, AI)</TD></TR>
            <TR><TD>Name</TD><TD>VARCHAR(100)</TD></TR>
            <TR><TD>Age</TD><TD>INT</TD></TR>
            <TR><TD>Gender</TD><TD>VARCHAR(10)</TD></TR>
            <TR><TD>Address</TD><TD>VARCHAR(255)</TD></TR>
            <TR><TD>Phone</TD><TD>VARCHAR(15)</TD></TR>
        </TABLE>>];
    
    // Doctor Table
    Doctor [label=<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#FFE6E6">
            <TR><TD COLSPAN="2" BGCOLOR="#FF6666"><B>Doctor</B></TD></TR>
            <TR><TD>DoctorID</TD><TD>INT (PK, AI)</TD></TR>
            <TR><TD>Name</TD><TD>VARCHAR(100)</TD></TR>
            <TR><TD>Specialization</TD><TD>VARCHAR(100)</TD></TR>
            <TR><TD>Phone</TD><TD>VARCHAR(15)</TD></TR>
        </TABLE>>];
    
    // Appointment Table
    Appointment [label=<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#E6F3FF">
            <TR><TD COLSPAN="2" BGCOLOR="#6699FF"><B>Appointment</B></TD></TR>
            <TR><TD>AppointmentID</TD><TD>INT (PK, AI)</TD></TR>
            <TR><TD>PatientID</TD><TD>INT (FK)</TD></TR>
            <TR><TD>DoctorID</TD><TD>INT (FK)</TD></TR>
            <TR><TD>AppointmentDate</TD><TD>DATE</TD></TR>
        </TABLE>>];
    
    // Medical Record Table
    MedicalRecord [label=<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#E6F3FF">
            <TR><TD COLSPAN="2" BGCOLOR="#6699FF"><B>MedicalRecord</B></TD></TR>
            <TR><TD>RecordID</TD><TD>INT (PK, AI)</TD></TR>
            <TR><TD>PatientID</TD><TD>INT (FK)</TD></TR>
            <TR><TD>DoctorID</TD><TD>INT (FK)</TD></TR>
            <TR><TD>Diagnosis</TD><TD>VARCHAR(255)</TD></TR>
            <TR><TD>Treatment</TD><TD>VARCHAR(255)</TD></TR>
        </TABLE>>];
    
    // Billing Table
    Billing [label=<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#E6F3FF">
            <TR><TD COLSPAN="2" BGCOLOR="#6699FF"><B>Billing</B></TD></TR>
            <TR><TD>BillID</TD><TD>INT (PK, AI)</TD></TR>
            <TR><TD>PatientID</TD><TD>INT (FK)</TD></TR>
            <TR><TD>Amount</TD><TD>DECIMAL(10,2)</TD></TR>
            <TR><TD>BillingDate</TD><TD>DATE</TD></TR>
        </TABLE>>];
    
    // Payment Table
    Payment [label=<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#E6F3FF">
            <TR><TD COLSPAN="2" BGCOLOR="#6699FF"><B>Payment</B></TD></TR>
            <TR><TD>PaymentID</TD><TD>INT (PK, AI)</TD></TR>
            <TR><TD>PatientID</TD><TD>INT (FK)</TD></TR>
            <TR><TD>AmountPaid</TD><TD>DECIMAL(10,2)</TD></TR>
            <TR><TD>PaymentDate</TD><TD>DATE</TD></TR>
        </TABLE>>];
    
    // Users Table
    Users [label=<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#FFE6E6">
            <TR><TD COLSPAN="2" BGCOLOR="#FF6666"><B>Users</B></TD></TR>
            <TR><TD>user_id</TD><TD>INT (PK, AI)</TD></TR>
            <TR><TD>username</TD><TD>VARCHAR(100)(UNIQUE)</TD></TR>
            <TR><TD>password_hash</TD><TD>VARCHAR(255)</TD></TR>
            <TR><TD>role</TD><TD>ENUM</TD></TR>
        </TABLE>>];
    
    // PaymentStatus Table
    PaymentStatus [label=<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#E6F3FF">
            <TR><TD COLSPAN="2" BGCOLOR="#6699FF"><B>PaymentStatus</B></TD></TR>
            <TR><TD>PatientID</TD><TD>INT (PK, FK)</TD></TR>
            <TR><TD>LatestBillAmount</TD><TD>DECIMAL(10,2)</TD></TR>
            <TR><TD>PaymentComplete</TD><TD>BOOLEAN</TD></TR>
        </TABLE>>];
    
    // Prescription Table
    Prescription [label=<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#E6F3FF">
            <TR><TD COLSPAN="2" BGCOLOR="#6699FF"><B>Prescription</B></TD></TR>
            <TR><TD>PrescriptionID</TD><TD>INT (PK, AI)</TD></TR>
            <TR><TD>PatientID</TD><TD>INT (FK)</TD></TR>
            <TR><TD>DoctorID</TD><TD>INT (FK)</TD></TR>
            <TR><TD>MedicineName</TD><TD>VARCHAR(100)</TD></TR>
            <TR><TD>Dosage</TD><TD>VARCHAR(50)</TD></TR>
            <TR><TD>Frequency</TD><TD>VARCHAR(50)</TD></TR>
            <TR><TD>StartDate</TD><TD>DATE</TD></TR>
            <TR><TD>EndDate</TD><TD>DATE</TD></TR>
            <TR><TD>Notes</TD><TD>VARCHAR(255)</TD></TR>
        </TABLE>>];
    
    // Department Table
    Department [label=<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#FFE6E6">
            <TR><TD COLSPAN="2" BGCOLOR="#FF6666"><B>Department</B></TD></TR>
            <TR><TD>DepartmentID</TD><TD>INT (PK, AI)</TD></TR>
            <TR><TD>DepartmentName</TD><TD>VARCHAR(100)(UNIQUE)</TD></TR>
            <TR><TD>HeadDoctor</TD><TD>INT (FK)</TD></TR>
            <TR><TD>Phone</TD><TD>VARCHAR(15)</TD></TR>
        </TABLE>>];
    
    // Room Table
    Room [label=<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#E6F3FF">
            <TR><TD COLSPAN="2" BGCOLOR="#6699FF"><B>Room</B></TD></TR>
            <TR><TD>RoomID</TD><TD>INT (PK, AI)</TD></TR>
            <TR><TD>RoomNumber</TD><TD>VARCHAR(20)(UNIQUE)</TD></TR>
            <TR><TD>RoomType</TD><TD>ENUM</TD></TR>
            <TR><TD>Capacity</TD><TD>INT</TD></TR>
            <TR><TD>IsOccupied</TD><TD>BOOLEAN</TD></TR>
            <TR><TD>CurrentPatientID</TD><TD>INT (FK)</TD></TR>
            <TR><TD>DepartmentID</TD><TD>INT (FK)</TD></TR>
        </TABLE>>];
    
    // LabTest Table
    LabTest [label=<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#E6F3FF">
            <TR><TD COLSPAN="2" BGCOLOR="#6699FF"><B>LabTest</B></TD></TR>
            <TR><TD>TestID</TD><TD>INT (PK, AI)</TD></TR>
            <TR><TD>PatientID</TD><TD>INT (FK)</TD></TR>
            <TR><TD>DoctorID</TD><TD>INT (FK)</TD></TR>
            <TR><TD>TestName</TD><TD>VARCHAR(100)</TD></TR>
            <TR><TD>TestDate</TD><TD>DATE</TD></TR>
            <TR><TD>Result</TD><TD>VARCHAR(255)</TD></TR>
            <TR><TD>Status</TD><TD>ENUM</TD></TR>
            <TR><TD>Notes</TD><TD>VARCHAR(255)</TD></TR>
        </TABLE>>];
    
    // TriggerActionLog Table
    TriggerLog [label=<
        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#E6F6E6">
            <TR><TD COLSPAN="2" BGCOLOR="#66CC66"><B>TriggerActionLog</B></TD></TR>
            <TR><TD>LogID</TD><TD>INT (PK, AI)</TD></TR>
            <TR><TD>TriggerName</TD><TD>VARCHAR(100)</TD></TR>
            <TR><TD>ActionType</TD><TD>VARCHAR(50)</TD></TR>
            <TR><TD>TableName</TD><TD>VARCHAR(100)</TD></TR>
            <TR><TD>RecordID</TD><TD>INT</TD></TR>
            <TR><TD>OldValue</TD><TD>VARCHAR(255)</TD></TR>
            <TR><TD>NewValue</TD><TD>VARCHAR(255)</TD></TR>
            <TR><TD>ActionTimestamp</TD><TD>TIMESTAMP</TD></TR>
            <TR><TD>PatientID</TD><TD>INT</TD></TR>
        </TABLE>>];
    
    // Relationships
    Patient -> Appointment [label="1:M"];
    Patient -> MedicalRecord [label="1:M"];
    Patient -> Billing [label="1:M"];
    Patient -> Payment [label="1:M"];
    Patient -> PaymentStatus [label="1:1"];
    Patient -> Prescription [label="1:M"];
    Patient -> LabTest [label="1:M"];
    Patient -> Room [label="1:0..1"];
    
    Doctor -> Appointment [label="1:M"];
    Doctor -> MedicalRecord [label="1:M"];
    Doctor -> Prescription [label="1:M"];
    Doctor -> LabTest [label="1:M"];
    Doctor -> Department [label="1:0..1"];
    
    Department -> Room [label="1:M"];
}
"""

# ASCII Relational Schema Diagram
ascii_relational_diagram = """
================================================================================
              RELATIONAL MAPPING DIAGRAM - Hospital Management DBMS
================================================================================

TABLE STRUCTURE AND SCHEMA DETAILS

================================================================================
1. PATIENT TABLE
================================================================================

+----------------------------------+
| PATIENT                          |
+----------------------------------+
| PatientID (PK, INT, AUTO_INCREMENT) |
| Name (VARCHAR(100), NOT NULL)    |
| Age (INT)                        |
| Gender (VARCHAR(10))             |
| Address (VARCHAR(255))           |
| Phone (VARCHAR(15))              |
+----------------------------------+

Relationships:
  • 1:M to Appointment
  • 1:M to MedicalRecord
  • 1:M to Billing
  • 1:M to Payment
  • 1:1 to PaymentStatus
  • 1:M to Prescription
  • 1:M to LabTest
  • 1:0..1 to Room (Optional)

================================================================================
2. DOCTOR TABLE
================================================================================

+----------------------------------+
| DOCTOR                           |
+----------------------------------+
| DoctorID (PK, INT, AUTO_INCREMENT)|
| Name (VARCHAR(100), NOT NULL)    |
| Specialization (VARCHAR(100))    |
| Phone (VARCHAR(15))              |
+----------------------------------+

Relationships:
  • 1:M to Appointment
  • 1:M to MedicalRecord
  • 1:M to Prescription
  • 1:M to LabTest
  • 1:0..1 to Department (As HeadDoctor)

================================================================================
3. APPOINTMENT TABLE
================================================================================

+----------------------------------+
| APPOINTMENT                      |
+----------------------------------+
| AppointmentID (PK, INT, AI)      |
| PatientID (FK) → Patient         |
| DoctorID (FK) → Doctor           |
| AppointmentDate (DATE)           |
+----------------------------------+

Primary Key: AppointmentID
Foreign Keys:
  • PatientID REFERENCES Patient(PatientID) ON DELETE CASCADE
  • DoctorID REFERENCES Doctor(DoctorID) ON DELETE CASCADE

Purpose: Links patients with doctors at specific times

================================================================================
4. MEDICALRECORD TABLE
================================================================================

+----------------------------------+
| MEDICALRECORD                    |
+----------------------------------+
| RecordID (PK, INT, AI)           |
| PatientID (FK) → Patient         |
| DoctorID (FK) → Doctor           |
| Diagnosis (VARCHAR(255))         |
| Treatment (VARCHAR(255))         |
+----------------------------------+

Primary Key: RecordID
Foreign Keys:
  • PatientID REFERENCES Patient(PatientID) ON DELETE CASCADE
  • DoctorID REFERENCES Doctor(DoctorID) ON DELETE CASCADE

Purpose: Stores diagnosis and treatment information

================================================================================
5. BILLING TABLE
================================================================================

+----------------------------------+
| BILLING                          |
+----------------------------------+
| BillID (PK, INT, AI)             |
| PatientID (FK) → Patient         |
| Amount (DECIMAL(10,2))           |
| BillingDate (DATE)               |
+----------------------------------+

Primary Key: BillID
Foreign Key:
  • PatientID REFERENCES Patient(PatientID) ON DELETE CASCADE

Purpose: Tracks all charges and bills generated

================================================================================
6. PAYMENT TABLE
================================================================================

+----------------------------------+
| PAYMENT                          |
+----------------------------------+
| PaymentID (PK, INT, AI)          |
| PatientID (FK) → Patient         |
| AmountPaid (DECIMAL(10,2))       |
| PaymentDate (DATE)               |
+----------------------------------+

Primary Key: PaymentID
Foreign Key:
  • PatientID REFERENCES Patient(PatientID) ON DELETE CASCADE

Trigger: TR_UPDATE_PAYMENT_STATUS fires AFTER INSERT
Purpose: Records payment transactions

================================================================================
7. USERS TABLE
================================================================================

+----------------------------------+
| USERS                            |
+----------------------------------+
| user_id (PK, INT, AI)            |
| username (VARCHAR(100), UNIQUE)  |
| password_hash (VARCHAR(255))     |
| role (ENUM: admin/doctor/staff)  |
+----------------------------------+

Primary Key: user_id
Unique Constraint: username
Purpose: Authentication and role management

Default User: admin (password: admin123 SHA-256 hashed)

================================================================================
8. PAYMENTSTATUS TABLE
================================================================================

+----------------------------------+
| PAYMENTSTATUS                    |
+----------------------------------+
| PatientID (PK, FK) → Patient     |
| LatestBillAmount (DECIMAL(10,2)) |
| PaymentComplete (BOOLEAN, DEFAULT FALSE) |
+----------------------------------+

Primary Key: PatientID (also Foreign Key)
Purpose: Tracks payment completion status

Auto-updated by: TR_UPDATE_PAYMENT_STATUS trigger

================================================================================
9. PRESCRIPTION TABLE
================================================================================

+----------------------------------+
| PRESCRIPTION                     |
+----------------------------------+
| PrescriptionID (PK, INT, AI)     |
| PatientID (FK) → Patient         |
| DoctorID (FK) → Doctor           |
| MedicineName (VARCHAR(100))      |
| Dosage (VARCHAR(50))             |
| Frequency (VARCHAR(50))          |
| StartDate (DATE)                 |
| EndDate (DATE)                   |
| Notes (VARCHAR(255))             |
+----------------------------------+

Primary Key: PrescriptionID
Foreign Keys:
  • PatientID REFERENCES Patient(PatientID) ON DELETE CASCADE
  • DoctorID REFERENCES Doctor(DoctorID) ON DELETE CASCADE

Trigger: TR_LOG_PRESCRIPTION_INSERT fires AFTER INSERT
Purpose: Medication prescription management

================================================================================
10. DEPARTMENT TABLE
================================================================================

+----------------------------------+
| DEPARTMENT                       |
+----------------------------------+
| DepartmentID (PK, INT, AI)       |
| DepartmentName (VARCHAR(100), UNIQUE) |
| HeadDoctor (FK) → Doctor         |
| Phone (VARCHAR(15))              |
+----------------------------------+

Primary Key: DepartmentID
Foreign Key:
  • HeadDoctor REFERENCES Doctor(DoctorID) ON DELETE SET NULL

Unique Constraint: DepartmentName
Purpose: Hospital organizational structure

================================================================================
11. ROOM TABLE
================================================================================

+----------------------------------+
| ROOM                             |
+----------------------------------+
| RoomID (PK, INT, AI)             |
| RoomNumber (VARCHAR(20), UNIQUE) |
| RoomType (ENUM: General/ICU/Private/Semi-Private) |
| Capacity (INT)                   |
| IsOccupied (BOOLEAN, DEFAULT FALSE) |
| CurrentPatientID (FK) → Patient  |
| DepartmentID (FK) → Department   |
+----------------------------------+

Primary Key: RoomID
Foreign Keys:
  • CurrentPatientID REFERENCES Patient(PatientID) ON DELETE SET NULL
  • DepartmentID REFERENCES Department(DepartmentID) ON DELETE SET NULL

Trigger: TR_LOG_ROOM_OCCUPANCY fires AFTER UPDATE
Purpose: Hospital room and occupancy management

================================================================================
12. LABTEST TABLE
================================================================================

+----------------------------------+
| LABTEST                          |
+----------------------------------+
| TestID (PK, INT, AI)             |
| PatientID (FK) → Patient         |
| DoctorID (FK) → Doctor           |
| TestName (VARCHAR(100))          |
| TestDate (DATE)                  |
| Result (VARCHAR(255))            |
| Status (ENUM: Pending/Completed/Cancelled) |
| Notes (VARCHAR(255))             |
+----------------------------------+

Primary Key: TestID
Foreign Keys:
  • PatientID REFERENCES Patient(PatientID) ON DELETE CASCADE
  • DoctorID REFERENCES Doctor(DoctorID) ON DELETE CASCADE

Trigger: TR_ADD_LAB_TEST_CHARGE fires AFTER UPDATE (Status = 'Completed')
         Auto-inserts $500 billing record

Purpose: Laboratory test management with auto-billing

================================================================================
13. TRIGGERACTIONLOG TABLE
================================================================================

+----------------------------------+
| TRIGGERACTIONLOG                 |
+----------------------------------+
| LogID (PK, INT, AI)              |
| TriggerName (VARCHAR(100))       |
| ActionType (VARCHAR(50): INSERT/UPDATE) |
| TableName (VARCHAR(100))         |
| RecordID (INT)                   |
| OldValue (VARCHAR(255))          |
| NewValue (VARCHAR(255))          |
| ActionTimestamp (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP) |
| PatientID (INT)                  |
+----------------------------------+

Primary Key: LogID
No Foreign Keys (Audit table)
Purpose: Complete audit trail for all triggered actions

Populated by 4 Triggers:
  • TR_UPDATE_PAYMENT_STATUS
  • TR_LOG_PRESCRIPTION_INSERT
  • TR_LOG_ROOM_OCCUPANCY
  • TR_ADD_LAB_TEST_CHARGE


================================================================================
COMPLETE FOREIGN KEY RELATIONSHIPS MATRIX
================================================================================

Source Table       → Target Table       Column           Constraint Rule
─────────────────────────────────────────────────────────────────────────
Patient            ← Appointment        PatientID        CASCADE
Patient            ← MedicalRecord      PatientID        CASCADE
Patient            ← Billing            PatientID        CASCADE
Patient            ← Payment            PatientID        CASCADE
Patient            ← PaymentStatus      PatientID        CASCADE
Patient            ← Prescription       PatientID        CASCADE
Patient            ← LabTest            PatientID        CASCADE
Patient            ← Room               CurrentPatientID SET NULL

Doctor             ← Appointment        DoctorID         CASCADE
Doctor             ← MedicalRecord      DoctorID         CASCADE
Doctor             ← Prescription       DoctorID         CASCADE
Doctor             ← LabTest            DoctorID         CASCADE
Doctor             ← Department         HeadDoctor       SET NULL

Department         ← Room               DepartmentID     SET NULL


================================================================================
DATA TYPE SPECIFICATIONS
================================================================================

Type                    Usage                           Examples
─────────────────────────────────────────────────────────────────────────
INT                     Numeric IDs, counts, age        PatientID, Age, Capacity
AUTO_INCREMENT          Primary keys                    All *ID fields
VARCHAR(n)              Text fields (variable length)   Name, Address, Phone
DECIMAL(10,2)           Currency/billing amounts        Amount, AmountPaid
DATE                    Specific dates                  BillingDate, TestDate
DATETIME                Date and time                   AppointmentDate (optional)
TIMESTAMP               Automatic timestamp             ActionTimestamp
BOOLEAN                 True/False values               IsOccupied, PaymentComplete
ENUM                    Fixed set of values             RoomType, Status, role


================================================================================
CONSTRAINT SUMMARY
================================================================================

Constraint Type          Tables Using It              Purpose
─────────────────────────────────────────────────────────────────────────
PRIMARY KEY              All 13 tables                Unique row identification
AUTO_INCREMENT           All ID columns               Sequential ID generation
FOREIGN KEY              11 tables                    Referential integrity
UNIQUE                   3 tables (username,          Prevent duplicates
                         DepartmentName, RoomNumber)
NOT NULL                 Key attributes               Ensure critical data
CHECK                    Implicit via ENUM            Valid value range
DEFAULT                  Multiple fields              Default values
ON DELETE CASCADE        Most patient FKs             Child record deletion
ON DELETE SET NULL       Optional FKs                 Preserve records


================================================================================
CARDINALITY AND RELATIONSHIPS SUMMARY
================================================================================

Relationship Type       Source          Target          Cardinality
─────────────────────────────────────────────────────────────────────────
Appointment            Patient         Doctor          M:M (via Appointment table)
Medical Treatment      Patient         Doctor          M:M (via MedicalRecord)
Prescription           Patient         Doctor          M:M (via Prescription)
Lab Testing            Patient         Doctor          M:M (via LabTest)
Billing                Patient         Bill Amount     1:M
Payment                Patient         Payment Records 1:M
Payment Tracking       Patient         PaymentStatus   1:1
Room Occupancy         Patient         Room            1:0..1 (Optional)
Department Head        Doctor          Department      1:0..1 (Optional)
Rooms                  Department      Room            1:M


================================================================================
NORMALIZATION VERIFICATION
================================================================================

FIRST NORMAL FORM (1NF):
  ✓ All attributes contain atomic (indivisible) values
  ✓ No repeating groups or arrays
  ✓ Each row has unique identifier (Primary Key)

SECOND NORMAL FORM (2NF):
  ✓ In 1NF
  ✓ No partial dependencies
  ✓ All non-key attributes fully depend on primary key
  ✓ No separate keys from incomplete primary key

THIRD NORMAL FORM (3NF):
  ✓ In 2NF
  ✓ No transitive dependencies
  ✓ Non-key attributes depend only on primary key
  ✓ No non-key attribute dependencies on other non-keys

RESULT: All 13 tables are normalized to 3NF ✓


================================================================================
SAMPLE QUERIES USING RELATIONAL STRUCTURE
================================================================================

1. Get all appointments for a patient:
   SELECT a.AppointmentID, d.Name, a.AppointmentDate
   FROM Appointment a
   JOIN Patient p ON a.PatientID = p.PatientID
   JOIN Doctor d ON a.DoctorID = d.DoctorID
   WHERE p.PatientID = 1;

2. Calculate patient balance:
   SELECT p.Name,
          SUM(b.Amount) as TotalBilled,
          SUM(pa.AmountPaid) as TotalPaid,
          SUM(b.Amount) - SUM(pa.AmountPaid) as Balance
   FROM Patient p
   LEFT JOIN Billing b ON p.PatientID = b.PatientID
   LEFT JOIN Payment pa ON p.PatientID = pa.PatientID
   GROUP BY p.PatientID;

3. Get room occupancy status:
   SELECT r.RoomNumber, r.RoomType, p.Name as CurrentPatient
   FROM Room r
   LEFT JOIN Patient p ON r.CurrentPatientID = p.PatientID
   WHERE r.DepartmentID = 1;

4. Track prescription history:
   SELECT p.Name, pr.MedicineName, pr.Dosage, pr.Frequency, pr.StartDate, pr.EndDate
   FROM Prescription pr
   JOIN Patient p ON pr.PatientID = p.PatientID
   WHERE pr.PatientID = 1
   ORDER BY pr.StartDate DESC;

5. Generate billing report:
   SELECT p.Name, COUNT(b.BillID) as BillCount, SUM(b.Amount) as TotalBilled
   FROM Patient p
   LEFT JOIN Billing b ON p.PatientID = b.PatientID
   GROUP BY p.PatientID;


================================================================================
KEY DESIGN DECISIONS
================================================================================

1. Separation of PaymentStatus and Payment tables:
   - Payment: All transactions (history)
   - PaymentStatus: Current status (auto-updated by trigger)
   - Benefit: Historical tracking and real-time status

2. Cascading Deletes on Patient:
   - Deleting a patient removes all related appointments, bills, etc.
   - Ensures referential integrity
   - Prevents orphaned records

3. ON DELETE SET NULL for Optional FKs:
   - Department.HeadDoctor: Doctor can be deleted without removing department
   - Room.CurrentPatientID: Patient can be discharged without deleting room
   - Room.DepartmentID: Room remains even if department deleted

4. Triggers for Automatic Actions:
   - Auto-update payment status
   - Auto-billing for completed lab tests
   - Audit trail for all changes

5. ENUM Types for Status Fields:
   - Room Status: General, ICU, Private, Semi-Private
   - Lab Test Status: Pending, Completed, Cancelled
   - User Role: admin, doctor, staff
   - Ensures data consistency

6. UNIQUE Constraints on Natural Keys:
   - username (prevent duplicate logins)
   - DepartmentName (prevent duplicate departments)
   - RoomNumber (prevent duplicate room numbers)

7. Decimal for Currency:
   - DECIMAL(10,2) for all monetary amounts
   - Ensures accurate financial calculations
   - Prevents floating-point rounding errors


================================================================================
DATA INTEGRITY RULES
================================================================================

1. Referential Integrity:
   - Every PatientID in Billing must exist in Patient
   - Every DoctorID in Appointment must exist in Doctor
   - Enforced by FOREIGN KEY constraints

2. Domain Integrity:
   - Age must be positive integer
   - Amount must be non-negative decimal
   - Phone must be valid format (checked by application)

3. Entity Integrity:
   - Every table has PRIMARY KEY
   - No NULL values in PRIMARY KEY
   - Each row uniquely identifiable

4. Key Integrity:
   - No duplicate values in UNIQUE columns
   - username, DepartmentName, RoomNumber all unique

5. Temporal Integrity:
   - ActionTimestamp auto-filled by database
   - Ensures audit trail accuracy


================================================================================
END OF RELATIONAL MAPPING DIAGRAM
================================================================================
"""

# Save diagrams
def save_relational_diagrams():
    # Save ASCII diagram
    with open('RELATIONAL_MAPPING_ASCII.txt', 'w', encoding='utf-8') as f:
        f.write(ascii_relational_diagram)
    print("[OK] Relational Mapping ASCII saved: RELATIONAL_MAPPING_ASCII.txt")
    
    # Save DOT format
    with open('RELATIONAL_MAPPING.dot', 'w', encoding='utf-8') as f:
        f.write(relational_diagram_dot)
    print("[OK] Relational Mapping DOT saved: RELATIONAL_MAPPING.dot")
    
    # Generate PNG
    try:
        subprocess.run(['dot', '-Tpng', 'RELATIONAL_MAPPING.dot', '-o', 'RELATIONAL_MAPPING.png'], 
                      check=True, capture_output=True)
        print("[OK] Relational Mapping PNG generated: RELATIONAL_MAPPING.png")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("[INFO] Graphviz not installed. PNG not generated.")
    
    # Generate SVG
    try:
        subprocess.run(['dot', '-Tsvg', 'RELATIONAL_MAPPING.dot', '-o', 'RELATIONAL_MAPPING.svg'], 
                      check=True, capture_output=True)
        print("[OK] Relational Mapping SVG generated: RELATIONAL_MAPPING.svg")
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

if __name__ == "__main__":
    print("Generating Relational Mapping Diagrams...")
    print("=" * 70)
    save_relational_diagrams()
    print("=" * 70)
    print("\nRelational Mapping generation complete!")
    print("\nGenerated files:")
    print("  1. RELATIONAL_MAPPING_ASCII.txt - Complete relational schema")
    print("  2. RELATIONAL_MAPPING.dot - Graphviz format")
    if os.path.exists('RELATIONAL_MAPPING.png'):
        print("  3. RELATIONAL_MAPPING.png - Visual diagram (PNG)")
    if os.path.exists('RELATIONAL_MAPPING.svg'):
        print("  4. RELATIONAL_MAPPING.svg - Visual diagram (SVG)")
