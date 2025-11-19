"""
Generate ER Diagram for Hospital Management DBMS
Uses graphviz to create a professional ER diagram
"""

import os
import subprocess

# ER Diagram in Graphviz DOT format
er_diagram_dot = """
digraph ERDiagram {
    rankdir=LR;
    node [shape=box, style=filled, fillcolor=lightblue, fontname="Arial"];
    edge [fontname="Arial", fontsize=10];
    
    // Entity Definitions
    Patient [label="Patient\n\nPatientID (PK)\nName\nAge\nGender\nAddress\nPhone", fillcolor="#FFE6E6"];
    Doctor [label="Doctor\n\nDoctorID (PK)\nName\nSpecialization\nPhone", fillcolor="#FFE6E6"];
    Appointment [label="Appointment\n\nAppointmentID (PK)\nPatientID (FK)\nDoctorID (FK)\nAppointmentDate", fillcolor="#E6F3FF"];
    MedicalRecord [label="MedicalRecord\n\nRecordID (PK)\nPatientID (FK)\nDoctorID (FK)\nDiagnosis\nTreatment", fillcolor="#E6F3FF"];
    Billing [label="Billing\n\nBillID (PK)\nPatientID (FK)\nAmount\nBillingDate", fillcolor="#E6F3FF"];
    Payment [label="Payment\n\nPaymentID (PK)\nPatientID (FK)\nAmountPaid\nPaymentDate", fillcolor="#E6F3FF"];
    PaymentStatus [label="PaymentStatus\n\nPatientID (PK)\nLatestBillAmount\nPaymentComplete", fillcolor="#E6F3FF"];
    Users [label="Users\n\nuser_id (PK)\nusername (UNIQUE)\npassword_hash\nrole", fillcolor="#FFE6E6"];
    Prescription [label="Prescription\n\nPrescriptionID (PK)\nPatientID (FK)\nDoctorID (FK)\nMedicineName\nDosage\nFrequency\nStartDate\nEndDate\nNotes", fillcolor="#E6F3FF"];
    Department [label="Department\n\nDepartmentID (PK)\nDepartmentName (UNIQUE)\nHeadDoctor (FK)\nPhone", fillcolor="#FFE6E6"];
    Room [label="Room\n\nRoomID (PK)\nRoomNumber (UNIQUE)\nRoomType (ENUM)\nCapacity\nIsOccupied\nCurrentPatientID (FK)\nDepartmentID (FK)", fillcolor="#E6F3FF"];
    LabTest [label="LabTest\n\nTestID (PK)\nPatientID (FK)\nDoctorID (FK)\nTestName\nTestDate\nResult\nStatus (ENUM)\nNotes", fillcolor="#E6F3FF"];
    TriggerLog [label="TriggerActionLog\n\nLogID (PK)\nTriggerName\nActionType\nTableName\nRecordID\nOldValue\nNewValue\nActionTimestamp\nPatientID", fillcolor="#E6F6E6"];
    
    // Relationships - Patient as central entity
    Patient -> Appointment [label="1:M\nSchedules"];
    Patient -> MedicalRecord [label="1:M\nHas"];
    Patient -> Billing [label="1:M\nReceives"];
    Patient -> Payment [label="1:M\nMakes"];
    Patient -> PaymentStatus [label="1:1\nTracked By"];
    Patient -> Prescription [label="1:M\nReceives"];
    Patient -> LabTest [label="1:M\nUndergoes"];
    Patient -> Room [label="1:0..1\nOccupies"];
    
    // Relationships - Doctor
    Doctor -> Appointment [label="1:M\nHas"];
    Doctor -> MedicalRecord [label="1:M\nTreats"];
    Doctor -> Prescription [label="1:M\nPrescribes"];
    Doctor -> LabTest [label="1:M\nOrders"];
    Doctor -> Department [label="1:0..1\nHeads"];
    
    // Relationships - Department & Room
    Department -> Room [label="1:M\nContains"];
    
    // Relationships - Logging
    Appointment -> TriggerLog [label="0:M\nLogged"];
    Payment -> TriggerLog [label="0:M\nLogged"];
    Prescription -> TriggerLog [label="0:M\nLogged"];
    Room -> TriggerLog [label="0:M\nLogged"];
    LabTest -> TriggerLog [label="0:M\nLogged"];
    
    // Legend
    Legend [label="Legend\n\nRed: Core Entities\nBlue: Junction/Transaction Tables\nGreen: Audit Table\n\nPK: Primary Key\nFK: Foreign Key\n1:M: One-to-Many\n1:1: One-to-One\n0:M: Zero-to-Many", 
            shape=box, style=filled, fillcolor="#FFFACD", fontsize=9, labeljust="l"];
}
"""

# Alternative ASCII ER Diagram representation
ascii_er_diagram = """
================================================================================
                    ER DIAGRAM - Hospital Management DBMS
================================================================================

ENTITIES AND RELATIONSHIPS:

                                    ┌─────────────────────────────────────────┐
                                    │           CORE ENTITIES                 │
                                    └─────────────────────────────────────────┘

                    ┌─────────────────────────────────────────────────────────────────────────┐
                    │                                                                         │
                    │                                                                         │
        ┌───────────┴──────────┐                                           ┌──────────────────┴───────┐
        │                      │                                           │                          │
    ┌─────────────┐        ┌────────────┐        ┌──────────────┐      ┌─────────┐           ┌──────────┐
    │   PATIENT   │        │   DOCTOR   │        │ APPOINTMENT  │      │ BILLING │           │ PAYMENT  │
    ├─────────────┤        ├────────────┤        ├──────────────┤      ├─────────┤           ├──────────┤
    │ PatientID✱  │        │ DoctorID✱  │        │ AppointID✱   │      │ BillID✱ │           │ PaymentID✱
    │ Name        │        │ Name       │        │ PatientID✱ FK├──────┤ PatientID✱├─────────┤ PatientID✱
    │ Age         │        │ Specializ. │        │ DoctorID✱ FK ├────┐ │ Amount   │         │ AmountPaid
    │ Gender      │        │ Phone      │        │ AppointDate  │    │ │ BillingD.│    ┌────┤ PaymentD.
    │ Address     │        │            │        └──────────────┘    │ └─────────┘    │    └──────────┘
    │ Phone       │        │            │                            │               │
    └─────────────┘        └────────────┘                            │               │
        │        │             │        │                            │               │
        │        │             │        │                            │               │
        │        │         1:M │        │ 1:M                        │               │
        │        │             │        └──────────────┐             │               │
        │        │             └──────────────────────┤─────────────┴───────────────┘
        │        │                                    │
        │        │                          ┌─────────┴──────────┐
        │        │                          │                    │
        │        │                    ┌─────────────────┐   ┌──────────────┐
        │        │                    │ MEDICAL RECORD  │   │ PRESCRIPTION │
        │        │                    ├─────────────────┤   ├──────────────┤
        │        │                    │ RecordID✱       │   │ PrescID✱     │
        │        │                    │ PatientID✱ FK   │   │ PatientID✱FK │
        │        │                    │ DoctorID✱ FK    │   │ DoctorID✱ FK │
        │        │                    │ Diagnosis       │   │ MedicineName │
        │        │                    │ Treatment       │   │ Dosage       │
        │        │                    └─────────────────┘   │ Frequency    │
        │        │                                          │ StartDate    │
        │        │                                          │ EndDate      │
        │        │                                          └──────────────┘
        │        │
        │        │                              ┌────────────────────────────────┐
        │        │                              │      RESOURCE MANAGEMENT       │
        │        │                              └────────────────────────────────┘
        │        │
        │        │                    ┌──────────────────┐      ┌──────────────┐
        │        │                    │  DEPARTMENT      │      │     ROOM     │
        │        └────────────────────┤                  │      ├──────────────┤
        │                             │ DepartmentID✱    │      │ RoomID✱      │
        │                             │ DepartmentName   ├──1:M─┤ RoomNumber   │
        │                             │ HeadDoctor✱ FK   │      │ RoomType     │
        │                             │ Phone            │      │ Capacity     │
        │                             └──────────────────┘      │ IsOccupied   │
        │                                      ▲                │ CurPatientFK │
        │                                      │                │ DepartmentFK │
        │                                      │                └──────────────┘
        │                                      │
        └──────────────────────────────────────┘
                                     1:0..1
                               (Patient occupies Room)


        ┌──────────────────────┐                   ┌───────────────────────────┐
        │   LAB TESTS          │                   │   PAYMENT STATUS          │
        ├──────────────────────┤                   ├───────────────────────────┤
        │ TestID✱              │                   │ PatientID✱ FK             │
        │ PatientID✱ FK        ├───1:M────────1:1──┤ LatestBillAmount          │
        │ DoctorID✱ FK         │                   │ PaymentComplete           │
        │ TestName             │                   └───────────────────────────┘
        │ TestDate             │
        │ Result               │                   ┌──────────────────────────┐
        │ Status (ENUM)        │                   │   USERS (AUTH)           │
        │ Notes                │                   ├──────────────────────────┤
        └──────────────────────┘                   │ user_id✱                 │
                                                   │ username (UNIQUE)        │
                                                   │ password_hash            │
                                                   │ role (ENUM)              │
                                                   └──────────────────────────┘


================================================================================
                         TRIGGER ACTION LOG (AUDIT TRAIL)
================================================================================

        ┌──────────────────────────────────────────────────────────────┐
        │              TRIGGER ACTION LOG                              │
        ├──────────────────────────────────────────────────────────────┤
        │ LogID✱                                                       │
        │ TriggerName       (Links to: Appointment, Payment, Rx, Room) │
        │ ActionType        (INSERT/UPDATE)                            │
        │ TableName         (Source table)                             │
        │ RecordID          (Affected record)                          │
        │ OldValue          (Previous value)                           │
        │ NewValue          (New value)                                │
        │ ActionTimestamp   (AUTO: CURRENT_TIMESTAMP)                  │
        │ PatientID         (Associated patient)                       │
        └──────────────────────────────────────────────────────────────┘

        Logs from 4 Active Triggers:
        • TR_UPDATE_PAYMENT_STATUS    → Logs payment updates
        • TR_LOG_PRESCRIPTION_INSERT  → Logs new prescriptions
        • TR_LOG_ROOM_OCCUPANCY       → Logs room changes
        • TR_ADD_LAB_TEST_CHARGE      → Logs auto-billing


================================================================================
                           CARDINALITY SUMMARY
================================================================================

ONE-TO-MANY (1:M) Relationships:
┌─────────────────────────────────────────────────────────────────────────┐
│ Patient (1) → (M) Appointment       │ Patient (1) → (M) Billing         │
│ Patient (1) → (M) MedicalRecord     │ Patient (1) → (M) Payment         │
│ Patient (1) → (M) Prescription      │ Patient (1) → (M) LabTest         │
│                                                                         │
│ Doctor (1) → (M) Appointment        │ Doctor (1) → (M) MedicalRecord   │
│ Doctor (1) → (M) Prescription       │ Doctor (1) → (M) LabTest         │
│                                                                         │
│ Department (1) → (M) Room                                              │
│ Schedule (1) → (M) Seat_Booking (if applicable)                        │
└─────────────────────────────────────────────────────────────────────────┘

ONE-TO-ONE (1:1) Relationships:
┌─────────────────────────────────────────────────────────────────────────┐
│ Patient (1) ←→ (1) PaymentStatus                                        │
│ Doctor (1) ←→ (0..1) Department (as HeadDoctor)                        │
└─────────────────────────────────────────────────────────────────────────┘

ZERO-OR-ONE-TO-MANY (0:M or 1:M) Relationships:
┌─────────────────────────────────────────────────────────────────────────┐
│ Patient (1) ←→ (0..1) Room (Patient occupies one room or none)         │
└─────────────────────────────────────────────────────────────────────────┘


================================================================================
                    FOREIGN KEY CONSTRAINTS MAPPING
================================================================================

Parent Table         Child Table              FK Column          Constraint Rule
─────────────────────────────────────────────────────────────────────────────
Patient              Appointment              PatientID          CASCADE
Patient              MedicalRecord            PatientID          CASCADE
Patient              Billing                  PatientID          CASCADE
Patient              Payment                  PatientID          CASCADE
Patient              PaymentStatus            PatientID          CASCADE
Patient              Prescription             PatientID          CASCADE
Patient              LabTest                  PatientID          CASCADE
Patient              Room                     CurrentPatientID   SET NULL

Doctor               Appointment              DoctorID           CASCADE
Doctor               MedicalRecord            DoctorID           CASCADE
Doctor               Prescription             DoctorID           CASCADE
Doctor               LabTest                  DoctorID           CASCADE
Doctor               Department               HeadDoctor         SET NULL

Department           Room                     DepartmentID       SET NULL

Schedule             Seat_Booking             schedule_id        CASCADE

Seat_Booking         Payment                  seat_booking_id    CASCADE

Seat_Booking         Cancellation             seat_booking_id    CASCADE


================================================================================
                          NORMALIZATION ANALYSIS
================================================================================

FIRST NORMAL FORM (1NF):
✓ All attributes contain atomic (indivisible) values
✓ No repeating groups in any table
✓ Each table has a primary key

SECOND NORMAL FORM (2NF):
✓ Table is in 1NF
✓ No partial dependencies on composite keys
✓ All non-key attributes depend on the entire primary key

THIRD NORMAL FORM (3NF):
✓ Table is in 2NF
✓ No transitive dependencies
✓ Non-key attributes depend only on primary key, not on other non-key attributes

RESULT: All 13 tables are NORMALIZED to 3NF


================================================================================
                        BUSINESS RULES ENFORCED
================================================================================

Data Integrity:
1. Primary Key Constraints: Ensure unique identification of records
2. Foreign Key Constraints: Maintain referential integrity
3. UNIQUE Constraints: Prevent duplicate entries (username, RoomNumber, DepartmentName)
4. NOT NULL Constraints: Ensure critical data is always present
5. CHECK Constraints: Implicitly through ENUM types

Validation Rules:
1. Age: Must be > 0
2. Capacity: Must be > 0
3. Amount: Must be >= 0
4. Room Status: ENUM (General, ICU, Private, Semi-Private)
5. Lab Test Status: ENUM (Pending, Completed, Cancelled)
6. Booking Status: ENUM (Confirmed, Pending, Cancelled)
7. Payment Status: ENUM (Paid, Unpaid)
8. User Role: ENUM (admin, doctor, staff)

Cascading Rules:
1. DELETE Patient → Deletes all related Appointments, Bills, Payments, Medical Records
2. DELETE Doctor → Deletes all related Appointments, Medical Records, Prescriptions, Lab Tests
3. DELETE Department → Sets Room.DepartmentID to NULL (soft delete)
4. DELETE Room → Patient record remains (no cascade on optional FK)


================================================================================
                           TRIGGER DESIGN
================================================================================

TRIGGER 1: TR_UPDATE_PAYMENT_STATUS
  Event: AFTER INSERT ON Payment
  Action: Update PaymentStatus table
  Purpose: Automatic payment completion status tracking
  Logged: To TriggerActionLog

TRIGGER 2: TR_LOG_PRESCRIPTION_INSERT
  Event: AFTER INSERT ON Prescription
  Action: Insert audit record to TriggerActionLog
  Purpose: Prescription audit trail
  Logged: To TriggerActionLog

TRIGGER 3: TR_LOG_ROOM_OCCUPANCY
  Event: AFTER UPDATE ON Room (IsOccupied change)
  Action: Insert audit record to TriggerActionLog
  Purpose: Room occupancy history tracking
  Logged: To TriggerActionLog

TRIGGER 4: TR_ADD_LAB_TEST_CHARGE
  Event: AFTER UPDATE ON LabTest (Status = 'Completed')
  Action: Auto-insert billing record ($500 charge)
  Purpose: Automatic revenue capture
  Logged: To TriggerActionLog


================================================================================
                      ENTITY DESCRIPTION SUMMARY
================================================================================

PATIENT (Core Entity)
  Role: Central entity storing all patient information
  Relationships: Hub entity with 1:M relationships to most other tables
  Key Operations: Add patient, view history, generate bills, track appointments

DOCTOR (Core Entity)
  Role: Medical professional information
  Relationships: Participates in Appointments, Medical Records, Prescriptions, Lab Tests
  Key Operations: Doctor registration, view workload, schedule appointments

APPOINTMENT (Transaction Entity)
  Role: Links patients with doctors at specific times
  Relationships: M:1 to both Patient and Doctor
  Key Operations: Schedule appointment, view upcoming, analytics by doctor/patient

MEDICAL RECORD (Transaction Entity)
  Role: Treatment history and diagnosis information
  Relationships: M:1 to Patient and Doctor
  Key Operations: Create record, update treatment, view history

BILLING (Financial Entity)
  Role: Tracks all charges to patients
  Relationships: M:1 to Patient
  Key Operations: Generate bill, track outstanding, payment reconciliation

PAYMENT (Financial Entity)
  Role: Records all payment transactions
  Relationships: M:1 to Patient, triggers PaymentStatus update
  Key Operations: Record payment, auto-update status, generate receipts

PRESCRIPTION (Medical Entity)
  Role: Medication management
  Relationships: M:1 to Patient and Doctor
  Key Operations: Create prescription, log audit trail, track duration

DEPARTMENT (Resource Entity)
  Role: Hospital organizational structure
  Relationships: 1:M to Rooms, 1:0..1 to Doctor (Head)
  Key Operations: Create department, assign head, manage resources

ROOM (Resource Entity)
  Role: Bed/room management and occupancy
  Relationships: M:1 to Department, optional to Patient
  Key Operations: Check-in patient, check-out, track availability

LABTEST (Medical Entity)
  Role: Laboratory test management with auto-billing
  Relationships: M:1 to Patient and Doctor
  Key Operations: Create test, update result, track status, auto-bill on completion

PAYMENTSTATUS (Status Entity)
  Role: Payment completion tracking
  Relationships: 1:1 to Patient
  Key Operations: Auto-update on payment, track balance, generate reports

USERS (Authentication Entity)
  Role: System user management
  Relationships: Independent entity
  Key Operations: Login, role management, authentication

TRIGGERACTIONLOG (Audit Entity)
  Role: System-wide audit trail
  Relationships: Logs from multiple tables via triggers
  Key Operations: View audit trail, analyze trigger frequency, compliance reporting


================================================================================
                    ER DIAGRAM GENERATION NOTES
================================================================================

This ER diagram was created using the following conventions:

Color Coding:
  - Red Boxes:   Core/Primary Entities (Patient, Doctor, Users, Department)
  - Blue Boxes:  Transaction/Junction Entities (Appointment, Medical Record, Billing, etc.)
  - Green Boxes: Audit/Log Entities (TriggerActionLog)

Notation:
  ✱ = Primary Key (PK)
  FK = Foreign Key Reference
  1:M = One-to-Many relationship
  1:1 = One-to-One relationship
  0..1 = Optional (zero or one) relationship

Relationship Types:
  Solid Lines = Strong mandatory relationships
  Dashed Lines = Optional relationships
  Line Direction = Data dependency direction

The diagram shows all 13 entities and their interconnections, with clear
indication of primary keys, foreign keys, and relationship cardinalities.

================================================================================
"""

# Save the ASCII diagram to file
def save_diagrams():
    # Save ASCII diagram
    with open('ER_DIAGRAM_ASCII.txt', 'w', encoding='utf-8') as f:
        f.write(ascii_er_diagram)
    print("[OK] ASCII ER Diagram saved: ER_DIAGRAM_ASCII.txt")
    
    # Save DOT format for Graphviz (optional - requires graphviz installed)
    with open('ER_DIAGRAM.dot', 'w', encoding='utf-8') as f:
        f.write(er_diagram_dot)
    print("[OK] Graphviz DOT format saved: ER_DIAGRAM.dot")
    
    # Try to generate PNG from DOT if graphviz is installed
    try:
        subprocess.run(['dot', '-Tpng', 'ER_DIAGRAM.dot', '-o', 'ER_DIAGRAM.png'], 
                      check=True, capture_output=True)
        print("[OK] ER Diagram PNG generated: ER_DIAGRAM.png")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("[INFO] Graphviz not installed. Using ASCII diagram only.")
        print("  To generate PNG: Install graphviz and run: dot -Tpng ER_DIAGRAM.dot -o ER_DIAGRAM.png")
    
    # Try to generate SVG from DOT if graphviz is installed
    try:
        subprocess.run(['dot', '-Tsvg', 'ER_DIAGRAM.dot', '-o', 'ER_DIAGRAM.svg'], 
                      check=True, capture_output=True)
        print("[OK] ER Diagram SVG generated: ER_DIAGRAM.svg")
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

if __name__ == "__main__":
    print("Generating ER Diagrams for Hospital Management DBMS...")
    print("=" * 70)
    save_diagrams()
    print("=" * 70)
    print("\nER Diagram generation complete!")
    print("\nGenerated files:")
    print("  1. ER_DIAGRAM_ASCII.txt - Detailed ASCII representation")
    print("  2. ER_DIAGRAM.dot - Graphviz format for further customization")
    if os.path.exists('ER_DIAGRAM.png'):
        print("  3. ER_DIAGRAM.png - Visual diagram (PNG format)")
    if os.path.exists('ER_DIAGRAM.svg'):
        print("  4. ER_DIAGRAM.svg - Visual diagram (SVG format)")
    print("\nOpen ER_DIAGRAM_ASCII.txt to view the detailed ER diagram!")
