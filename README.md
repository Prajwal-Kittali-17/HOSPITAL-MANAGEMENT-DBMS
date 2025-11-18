# Hospital Management DBMS

A comprehensive hospital management system built with **Streamlit**, **Python**, and **MySQL**. Features complete CRUD operations, real-time analytics, and database triggers/procedures/functions.

## Features

### 1. **Authentication**

- Secure login with SHA-256 password hashing
- Role-based access (admin, doctor, staff)
- Session management

### 2. **Dashboard**

- **Key Metrics:** Total Patients, Doctors, Appointments
- **Daily Summary:** Billing and Payment totals for selected date
- **All-Time Totals:** Total billing and payments across all records
- **Outstanding Balances:** Patient-wise balance report using `FN_GET_PATIENT_BALANCE` function

### 3. **Patient Management**

- View all patients
- Add new patient (Name, Age, Gender, Address, Phone)
- Delete patient (with cascading deletes for appointments, billing, payments)

### 4. **Doctor Management**

- View all doctors with specialization
- Remove doctor (cascade-deletes associated appointments and records)

### 5. **Appointments**

- **View All:** Display appointments with patient and doctor names
- **Upcoming Appointments:** Filter next 10 upcoming appointments
- **Add:** Schedule new appointments
- **Delete:** Remove appointments via dropdown selection

### 6. **Appointment Analytics & Scheduling**

- **Appointments by Doctor:** Count total appointments per doctor
- **Appointments by Patient:** Count total appointments per patient
- **Doctor Schedule:** View detailed appointment list for each doctor with dates

### 7. **Billing Management** _(Full CRUD)_

- **View All Bills:** Display all billing records
- **Patient Billing History:** View all bills for a specific patient with total
- **Add Bill:** Create new bill for a patient
- **Update Bill:** Modify existing bill amount
- **Delete Bill:** Remove bill records

### 8. **Payment Management** _(Full CRUD)_

- **View All Payments:** Display all payment records
- **Patient Payment History:** View all payments from a specific patient with total
- **Add Payment:** Record new payment (triggers `TR_UPDATE_PAYMENT_STATUS`)
- **Update Payment:** Modify payment amount
- **Delete Payment:** Remove payment records

### 9. **Medical Records Management** _(Full CRUD)_

- **View All Records:** Display diagnosis and treatment for all patients
- **Add Record:** Create new medical record for patient by doctor
- **Update Record:** Modify diagnosis and treatment details
- **Delete Record:** Remove medical records

### 10. **Prescription Management** _(New - Full CRUD)_

- **View All:** Display all prescriptions with medicine, dosage, frequency
- **Add Prescription:** Create prescription for patient by doctor (medicine, dosage, duration, notes)
- **Delete Prescription:** Remove prescriptions
- **Automatic Logging:** `TR_LOG_PRESCRIPTION_INSERT` trigger logs all prescription additions

### 11. **Lab Tests Management** _(New - Full CRUD)_

- **View All Tests:** Display all lab tests with status (Pending/Completed/Cancelled)
- **Add Test:** Create lab test for patient
- **Update Status & Result:** Mark tests as completed and add results
- **Automatic Billing:** `TR_ADD_LAB_TEST_CHARGE` trigger automatically charges $500 when test is completed

### 12. **Hospital Rooms & Occupancy** _(New)_

- **View All Rooms:** Display room number, type, capacity, department, occupancy status
- **Check-in Patient:** Assign patient to vacant room (triggers room occupancy log)
- **Check-out Patient:** Release patient from room (triggers room vacancy log)
- **Occupancy Tracking:** `TR_LOG_ROOM_OCCUPANCY` trigger monitors all room status changes

### 13. **Departments Management** _(New)_

- **View Departments:** Display department name, head doctor, total rooms, occupied rooms
- **Add Department:** Create new department with head doctor
- **Department Workload View:** See appointments and room utilization per department

### 14. **Trigger Logs & Monitoring** _(NEW - Displays All Trigger Events)_

- **Real-Time Action Log:** View all automatic actions triggered by database events (payments, lab tests, room changes, prescriptions)
- **Event Breakdown:** Count of events per trigger with last fired timestamp
- **Active Triggers:** List all triggers currently in database with their event types
- **Clear Logs:** Admin option to clear trigger action logs
- **Triggers Displayed:**
  - `TR_UPDATE_PAYMENT_STATUS`: Fires when payment added (updates payment status)
  - `TR_LOG_PRESCRIPTION_INSERT`: Fires when prescription created
  - `TR_LOG_ROOM_OCCUPANCY`: Fires when room occupancy changes
  - `TR_ADD_LAB_TEST_CHARGE`: Fires when lab test completed (auto-bills patient)

### 15. **Database Objects** _(Displays Backend Logic)_

- **Triggers:** View all triggers in the database with detailed definitions
- **Routines:** View all stored functions and procedures with return types
- **Function Call:** Interactive call to `FN_GET_PATIENT_BALANCE(patient_id)`
- **Procedure Call:** Interactive call to `SP_ADD_NEW_DOCTOR` to add doctor via stored procedure

## Database Schema

### Tables

- **Patient:** PatientID, Name, Age, Gender, Address, Phone
- **Doctor:** DoctorID, Name, Specialization, Phone
- **Appointment:** AppointmentID, PatientID, DoctorID, AppointmentDate
- **MedicalRecord:** RecordID, PatientID, DoctorID, Diagnosis, Treatment
- **Billing:** BillID, PatientID, Amount, BillingDate
- **Payment:** PaymentID, PatientID, AmountPaid, PaymentDate
- **PaymentStatus:** PatientID, LatestBillAmount, PaymentComplete (tracks payment status)
- **Users:** user_id, username, password_hash, role
- **Prescription:** PrescriptionID, PatientID, DoctorID, MedicineName, Dosage, Frequency, StartDate, EndDate, Notes
- **Department:** DepartmentID, DepartmentName, HeadDoctor, Phone
- **Room:** RoomID, RoomNumber, RoomType, Capacity, IsOccupied, CurrentPatientID, DepartmentID
- **LabTest:** TestID, PatientID, DoctorID, TestName, TestDate, Result, Status, Notes
- **TriggerActionLog:** LogID, TriggerName, ActionType, TableName, RecordID, OldValue, NewValue, ActionTimestamp, PatientID

### Triggers

1. **`TR_UPDATE_PAYMENT_STATUS`** - AFTER INSERT ON Payment

   - Updates PaymentStatus table when payment is made
   - Sets PaymentComplete = TRUE if paid amount >= billed amount

2. **`TR_LOG_PRESCRIPTION_INSERT`** - AFTER INSERT ON Prescription

   - Logs prescription creation to TriggerActionLog
   - Records medicine name, dosage, and patient info

3. **`TR_LOG_ROOM_OCCUPANCY`** - AFTER UPDATE ON Room

   - Logs room occupancy status changes to TriggerActionLog
   - Tracks when rooms become occupied or vacant

4. **`TR_ADD_LAB_TEST_CHARGE`** - AFTER UPDATE ON LabTest
   - Auto-charges $500 to patient billing when lab test status changes to 'Completed'
   - Creates new billing entry automatically
   - Logs the charge to TriggerActionLog

### Functions

- **`FN_GET_PATIENT_BALANCE(p_id INT)`** - Returns DECIMAL(10,2) → Computes (Total Billed - Total Paid)

### Procedures

- **`SP_ADD_NEW_DOCTOR(n VARCHAR(100), s VARCHAR(100), p VARCHAR(15))`** - Inserts doctor and returns the inserted record

### Views

- **PatientAppointmentView:** Patient appointments with doctor and billing info
- **PatientRoomView:** Patients currently occupying hospital rooms
- **DepartmentWorkloadView:** Department capacity and appointment statistics

## Installation & Setup

### Prerequisites

- Python 3.8+
- MySQL Server running
- Streamlit
- mysql-connector-python
- pandas

### Step 1: Clone/Download the Project

```bash
cd "c:\Users\prajw\OneDrive\Desktop\SEMESTER 5\DataBase Management System\MINI PROJECT\Final Project\HOSPITAL-MANAGEMENT-DBMS"
```

### Step 2: Create Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Initialize Database

The first time you run the app, it will attempt to create missing DB objects (tables, triggers, functions, procedures). Or manually initialize with:

```powershell
python .\scripts\init_db.py
```

**Note:** Ensure your MySQL user (default: `root`) has permissions to CREATE TRIGGER, CREATE FUNCTION, CREATE PROCEDURE.

### Step 5: Configure Database Connection

Edit `db_config.py` and set your MySQL credentials:

```python
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_PASSWORD",   # Change to your MySQL password
    database="hospital_management",
    auth_plugin="mysql_native_password"
)
```

### Step 6: Run the Application

```powershell
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`.

### Step 7: Login

Default login credentials (created during DB init):

- **Username:** admin
- **Password:** admin123

(Password is hashed with SHA-256 in the database)

## File Structure

```
HOSPITAL-MANAGEMENT-DBMS/
├── db_config.py                # MySQL connection configuration
├── main.py                     # Streamlit app (all UI pages)
├── Hospital_Management.sql     # SQL schema and initial data
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── scripts/
│   └── init_db.py             # Script to initialize DB objects from SQL
├── utils/
│   ├── db_helpers.py          # DB connection utilities
│   └── __pycache__/
└── __pycache__/
```

## Usage Examples

### Example 1: Add a Patient

1. Login with admin/admin123
2. Go to **Patients**
3. Fill form and click "Add"

### Example 2: View Patient Billing History

1. Go to **Billing**
2. Under "Patient Billing History," select patient
3. See all bills and total billed amount

### Example 3: Check Patient Balance

1. Go to **DB Objects**
2. Under "Function: Get Patient Balance," select patient
3. Click "Get Balance" to see outstanding amount

### Example 4: View Doctor Schedule

1. Go to **Appointment Stats**
2. Under "Doctor Availability," select doctor
3. View all appointments for that doctor

### Example 5: Track Payment Status

1. Add a bill to a patient
2. Add a payment that covers the bill
3. The trigger `TR_UPDATE_PAYMENT_STATUS` automatically updates the status
4. Go to **Dashboard** → "Outstanding Balances" to confirm balance is 0 or negative

## Troubleshooting

### Error: "FUNCTION hospital_management.FN_GET_PATIENT_BALANCE does not exist"

**Solution:** Run `python .\scripts\init_db.py` to create missing DB objects, or ensure your DB user has CREATE FUNCTION privileges.

### Error: "Access denied for user 'root'@'localhost'"

**Solution:** Check MySQL credentials in `db_config.py`. Ensure MySQL server is running.

### Streamlit shows "No patients found" or "No doctors found"

**Solution:** The database might not have sample data. Run `scripts/init_db.py` to populate initial data from `Hospital_Management.sql`.

### Changes don't appear after adding/deleting records

**Solution:** Streamlit may be caching. Click the refresh icon in the Streamlit UI or restart the app.

## Database Objects (Triggers & Procedures)

### TR_UPDATE_PAYMENT_STATUS Trigger

When a payment is recorded, this trigger:

1. Sums total paid for the patient
2. Compares against billed amount
3. Sets `PaymentComplete = TRUE` if fully paid, `FALSE` otherwise
4. **Visible in UI:** Go to **DB Objects** → "Triggers in Database"

### FN_GET_PATIENT_BALANCE Function

Computes outstanding balance for a patient:

```sql
SELECT FN_GET_PATIENT_BALANCE(1);  -- Returns balance for Patient ID 1
```

**Used in UI:**

- Dashboard → Outstanding Balances
- DB Objects → Function Call section

### SP_ADD_NEW_DOCTOR Procedure

Adds a new doctor and returns the inserted record:

```sql
CALL SP_ADD_NEW_DOCTOR('Dr. John', 'Cardiology', '9999999999');
```

**Used in UI:** DB Objects → Procedure: Add New Doctor

## Complete Feature List

| Feature               | Module            | CRUD       | Status |
| --------------------- | ----------------- | ---------- | ------ |
| Patient Management    | Patients          | C, R, D    | ✅     |
| Doctor Management     | Doctors           | R, D       | ✅     |
| Appointments          | Appointments      | C, R, D    | ✅     |
| Appointment Analytics | Appointment Stats | R          | ✅     |
| Billing               | Billing           | C, R, U, D | ✅     |
| Payments              | Payments          | C, R, U, D | ✅     |
| Medical Records       | Medical Records   | C, R, U, D | ✅     |
| DB Objects            | DB Objects        | R          | ✅     |
| Triggers              | DB Objects        | R          | ✅     |
| Stored Functions      | DB Objects        | R, Call    | ✅     |
| Stored Procedures     | DB Objects        | R, Call    | ✅     |

## Notes

- All patient/doctor IDs are auto-incremented
- Passwords are hashed using SHA-256
- Foreign key constraints ensure referential integrity (ON DELETE CASCADE)
- The app calls `ensure_db_objects()` on first Dashboard load to create missing DB objects if needed
- Date fields use YYYY-MM-DD format (MySQL DATE type)
- **All triggers are fully functional and displayed in the "Trigger Logs" page**
- **Trigger actions are automatically logged to TriggerActionLog table for audit trails**

## Triggers Implemented

1. **TR_UPDATE_PAYMENT_STATUS** - Automatically updates payment status when payment is recorded
2. **TR_LOG_PRESCRIPTION_INSERT** - Logs all prescription creations with medicine details
3. **TR_LOG_ROOM_OCCUPANCY** - Tracks all room occupancy changes (check-in/check-out)
4. **TR_ADD_LAB_TEST_CHARGE** - Auto-charges $500 when lab test is completed

All triggers are **visible in real-time** in the Trigger Logs page!

## Future Enhancements

- Email notifications for appointments
- SMS reminders
- Insurance claim management
- Discharge summaries
- Lab test kit inventory
- Export reports to PDF/Excel
- User role enforcement (currently all features visible to all roles)
- Advanced analytics and charts
- Staff scheduling

## License

This project is for educational purposes (University Mini Project).

## Support

For issues or questions, contact the project maintainer.
