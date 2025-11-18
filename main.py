import streamlit as st
import hashlib
import pandas as pd
from utils.db_helpers import fetch_one, fetch_all, execute_query, call_procedure, call_function, ensure_db_objects

st.set_page_config(page_title="Hospital Management", layout="wide")


# -----------------------------
# Helpers
# -----------------------------
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# -----------------------------
# Login Page
# -----------------------------
def login_page():
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        hp = hash_password(password)
        row = fetch_one(
            "SELECT username, role FROM Users WHERE username=%s AND password_hash=%s",
            (username, hp)
        )

        if row:
            st.session_state.logged_in = True
            st.session_state.username = row[0]
            st.session_state.role = row[1]
            st.rerun()
        else:
            st.error("Invalid credentials")


# -----------------------------
# Dashboard
# -----------------------------
def dashboard_page():
    st.title("Hospital Management Dashboard")
    st.write(f"Welcome, {st.session_state.username} ({st.session_state.role})")

    # Ensure DB objects exist before showing metrics
    try:
        ensure_db_objects()
    except Exception as e:
        st.warning(f"DB objects ensure failed: {e}")

    st.subheader("Overview Metrics")
    try:
        total_patients = fetch_one("SELECT COUNT(*) FROM Patient")[0]
    except Exception:
        total_patients = 'N/A'
    try:
        total_doctors = fetch_one("SELECT COUNT(*) FROM Doctor")[0]
    except Exception:
        total_doctors = 'N/A'
    try:
        total_appointments = fetch_one("SELECT COUNT(*) FROM Appointment")[0]
    except Exception:
        total_appointments = 'N/A'

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Patients", total_patients)
    c2.metric("Total Doctors", total_doctors)
    c3.metric("Total Appointments", total_appointments)

    st.subheader("Patients Overview")
    df = fetch_all("SELECT * FROM Patient")
    st.dataframe(df)

    st.subheader("Billing / Payments Summary")
    bdate = st.date_input("Select date for daily totals")
    try:
        total_billing_day = fetch_one("SELECT IFNULL(SUM(Amount),0) FROM Billing WHERE BillingDate=%s", (bdate,))[0]
    except Exception:
        total_billing_day = 'N/A'
    try:
        total_payment_day = fetch_one("SELECT IFNULL(SUM(AmountPaid),0) FROM Payment WHERE PaymentDate=%s", (bdate,))[0]
    except Exception:
        total_payment_day = 'N/A'

    c4, c5 = st.columns(2)
    c4.metric(f"Total Billing on {bdate}", total_billing_day)
    c5.metric(f"Total Payments on {bdate}", total_payment_day)

    # Overall totals
    try:
        total_billing_all = fetch_one("SELECT IFNULL(SUM(Amount),0) FROM Billing")[0]
    except Exception:
        total_billing_all = 'N/A'
    try:
        total_payments_all = fetch_one("SELECT IFNULL(SUM(AmountPaid),0) FROM Payment")[0]
    except Exception:
        total_payments_all = 'N/A'

    c6, c7 = st.columns(2)
    c6.metric("Total Billing (All Time)", total_billing_all)
    c7.metric("Total Payments (All Time)", total_payments_all)

    # Unpaid / Outstanding balances
    st.subheader("Outstanding Balances")
    try:
        out_df = fetch_all("SELECT P.PatientID, P.Name, IFNULL(FN_GET_PATIENT_BALANCE(P.PatientID),0) AS Balance FROM Patient P ORDER BY Balance DESC")
        if not out_df.empty:
            st.dataframe(out_df)
        else:
            st.info("No outstanding balances")
    except Exception as e:
        st.error(f"Could not load outstanding balances: {e}")


# -----------------------------
# Patients Page (Full CRUD)
# -----------------------------
def patients_page():
    st.title("Patient Management")

    df = fetch_all("SELECT * FROM Patient ORDER BY PatientID")
    st.dataframe(df)

    st.subheader("Add Patient")
    with st.form("add_patient", clear_on_submit=True):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        address = st.text_input("Address")
        phone = st.text_input("Phone")
        submit = st.form_submit_button("Add")

    if submit:
        execute_query(
            "INSERT INTO Patient (Name, Age, Gender, Address, Phone) VALUES (%s, %s, %s, %s, %s)",
            (name, age, gender, address, phone)
        )
        st.success("Patient Added!")
        st.rerun()

    st.subheader("Delete Patient")
    del_id = st.number_input("Enter PatientID to delete", min_value=1)
    if st.button("Delete"):
        execute_query("DELETE FROM Patient WHERE PatientID=%s", (del_id,))
        st.success("Patient Deleted.")
        st.rerun()


# -----------------------------
# Doctors Page
# -----------------------------
def doctors_page():
    st.title("Doctors List")
    try:
        ensure_db_objects()
    except Exception:
        pass

    df = fetch_all("SELECT * FROM Doctor ORDER BY DoctorID")
    st.dataframe(df)

    st.subheader("Remove Doctor")
    try:
        doctor_df = fetch_all("SELECT DoctorID, Name FROM Doctor ORDER BY DoctorID")
        doc_map = {row['Name']: row['DoctorID'] for _, row in doctor_df.iterrows()}
        if doc_map:
            sel = st.selectbox("Select doctor to remove", list(doc_map.keys()))
            if st.button("Remove Doctor"):
                execute_query("DELETE FROM Doctor WHERE DoctorID=%s", (doc_map[sel],))
                st.success(f"Doctor {sel} removed.")
                st.rerun()
        else:
            st.info("No doctors available to remove.")
    except Exception as e:
        st.error(f"Error preparing doctor removal: {e}")


# -----------------------------
# Appointments Page (Add / View / Delete)
# -----------------------------
def appointments_page():
    st.title("Appointment Management")

    st.subheader("All Appointments")
    df = fetch_all("""
        SELECT 
            A.AppointmentID,
            P.Name AS Patient,
            D.Name AS Doctor,
            A.AppointmentDate
        FROM Appointment A
        JOIN Patient P ON A.PatientID = P.PatientID
        JOIN Doctor D ON A.DoctorID = D.DoctorID
        ORDER BY AppointmentDate DESC
    """)
    st.dataframe(df)

    # Upcoming appointments
    st.subheader("Upcoming Appointments")
    upcoming = fetch_all("SELECT A.AppointmentID, P.Name AS Patient, D.Name AS Doctor, A.AppointmentDate FROM Appointment A JOIN Patient P ON A.PatientID=P.PatientID JOIN Doctor D ON A.DoctorID=D.DoctorID WHERE A.AppointmentDate >= CURDATE() ORDER BY A.AppointmentDate LIMIT 10")
    if not upcoming.empty:
        st.table(upcoming)
    else:
        st.info("No upcoming appointments")

    # Add appointment
    st.subheader("Add Appointment")

    patient_df = fetch_all("SELECT PatientID, Name FROM Patient")
    doctor_df = fetch_all("SELECT DoctorID, Name FROM Doctor")

    patient_map = {row["Name"]: row["PatientID"] for _, row in patient_df.iterrows()}
    doctor_map = {row["Name"]: row["DoctorID"] for _, row in doctor_df.iterrows()}

    pname = st.selectbox("Select Patient", list(patient_map.keys()))
    dname = st.selectbox("Select Doctor", list(doctor_map.keys()))
    date = st.date_input("Appointment Date")

    if st.button("Add Appointment"):
        execute_query(
            "INSERT INTO Appointment (PatientID, DoctorID, AppointmentDate) VALUES (%s, %s, %s)",
            (patient_map[pname], doctor_map[dname], date)
        )
        st.success("Appointment Added!")
        st.rerun()

    # Delete by selection
    st.subheader("Delete Appointment")
    try:
        appts = fetch_all("SELECT AppointmentID, CONCAT(P.Name, ' - ', D.Name, ' (', AppointmentDate, ')') AS label FROM Appointment A JOIN Patient P ON A.PatientID=P.PatientID JOIN Doctor D ON A.DoctorID=D.DoctorID ORDER BY AppointmentDate DESC")
        appt_map = {row['label']: row['AppointmentID'] for _, row in appts.iterrows()}
        if appt_map:
            sel_label = st.selectbox("Select appointment to delete", list(appt_map.keys()))
            if st.button("Delete Selected Appointment"):
                execute_query("DELETE FROM Appointment WHERE AppointmentID=%s", (appt_map[sel_label],))
                st.success("Appointment deleted.")
                st.rerun()
        else:
            st.info("No appointments to delete")
    except Exception as e:
        st.error(f"Error loading appointments: {e}")


# -----------------------------
# Billing Page (Full CRUD)
# -----------------------------
def billing_page():
    st.title("Billing Management")

    st.subheader("All Bills")
    df = fetch_all("""
        SELECT 
            B.BillID,
            P.Name AS Patient,
            B.Amount,
            B.BillingDate
        FROM Billing B
        JOIN Patient P ON B.PatientID = P.PatientID
        ORDER BY B.BillingDate DESC
    """)
    st.dataframe(df)

    # Patient-wise billing history
    st.subheader("Patient Billing History")
    try:
        patients = fetch_all("SELECT PatientID, Name FROM Patient")
        pmap = {row["Name"]: row["PatientID"] for _, row in patients.iterrows()}
        if pmap:
            sel_patient = st.selectbox("Select patient for history", list(pmap.keys()), key="billing_hist_select")
            pid = pmap[sel_patient]
            hist = fetch_all("""
                SELECT BillID, Amount, BillingDate FROM Billing 
                WHERE PatientID=%s ORDER BY BillingDate DESC
            """, (pid,))
            if not hist.empty:
                st.dataframe(hist)
                total = hist['Amount'].sum()
                st.info(f"Total billed to {sel_patient}: {total}")
            else:
                st.info(f"No bills for {sel_patient}")
        else:
            st.info("No patients found")
    except Exception as e:
        st.error(f"Error loading billing history: {e}")

    st.subheader("Add Bill")
    patients = fetch_all("SELECT PatientID, Name FROM Patient")
    pmap = {row["Name"]: row["PatientID"] for _, row in patients.iterrows()}

    pname = st.selectbox("Select patient", list(pmap.keys()), key="add_bill_select")
    amount = st.number_input("Amount", min_value=0.0, key="add_bill_amount")
    bdate = st.date_input("Billing Date", key="add_bill_date")

    if st.button("Add Bill"):
        execute_query(
            "INSERT INTO Billing (PatientID, Amount, BillingDate) VALUES (%s, %s, %s)",
            (pmap[pname], amount, bdate)
        )
        st.success("Bill Added!")
        st.rerun()

    # Update bill
    st.subheader("Update Bill")
    try:
        bills = fetch_all("SELECT BillID, CONCAT('Bill #', BillID, ' - $', Amount, ' on ', BillingDate) AS label FROM Billing ORDER BY BillingDate DESC")
        bill_map = {row['label']: row['BillID'] for _, row in bills.iterrows()}
        if bill_map:
            sel_bill = st.selectbox("Select bill to update", list(bill_map.keys()), key="upd_bill_select")
            bid = bill_map[sel_bill]
            new_amount = st.number_input("New Amount", min_value=0.0, key="upd_bill_amount")
            if st.button("Update Bill"):
                execute_query("UPDATE Billing SET Amount=%s WHERE BillID=%s", (new_amount, bid))
                st.success("Bill updated!")
                st.rerun()
        else:
            st.info("No bills to update")
    except Exception as e:
        st.error(f"Error updating bill: {e}")

    # Delete bill
    st.subheader("Delete Bill")
    try:
        bills = fetch_all("SELECT BillID, CONCAT('Bill #', BillID, ' - $', Amount, ' on ', BillingDate) AS label FROM Billing ORDER BY BillingDate DESC")
        bill_map = {row['label']: row['BillID'] for _, row in bills.iterrows()}
        if bill_map:
            sel_bill = st.selectbox("Select bill to delete", list(bill_map.keys()), key="del_bill_select")
            if st.button("Delete Bill"):
                execute_query("DELETE FROM Billing WHERE BillID=%s", (bill_map[sel_bill],))
                st.success("Bill deleted!")
                st.rerun()
        else:
            st.info("No bills to delete")
    except Exception as e:
        st.error(f"Error deleting bill: {e}")


# -----------------------------
# Payments Page (Add / View / Update)
# -----------------------------
def payments_page():
    st.title("Payments Management")

    st.subheader("All Payments")
    df = fetch_all("""
        SELECT 
            Pay.PaymentID,
            P.Name AS Patient,
            Pay.AmountPaid,
            Pay.PaymentDate
        FROM Payment Pay
        JOIN Patient P ON Pay.PatientID = P.PatientID
        ORDER BY Pay.PaymentDate DESC
    """)
    st.dataframe(df)

    # Patient payment history
    st.subheader("Patient Payment History")
    try:
        patients = fetch_all("SELECT PatientID, Name FROM Patient")
        pmap = {row["Name"]: row["PatientID"] for _, row in patients.iterrows()}
        if pmap:
            sel_patient = st.selectbox("Select patient for payment history", list(pmap.keys()), key="pay_hist_select")
            pid = pmap[sel_patient]
            hist = fetch_all("""
                SELECT PaymentID, AmountPaid, PaymentDate FROM Payment 
                WHERE PatientID=%s ORDER BY PaymentDate DESC
            """, (pid,))
            if not hist.empty:
                st.dataframe(hist)
                total = hist['AmountPaid'].sum()
                st.info(f"Total paid by {sel_patient}: {total}")
            else:
                st.info(f"No payments from {sel_patient}")
        else:
            st.info("No patients found")
    except Exception as e:
        st.error(f"Error loading payment history: {e}")

    st.subheader("Add Payment")
    patients = fetch_all("SELECT PatientID, Name FROM Patient")
    pmap = {row["Name"]: row["PatientID"] for _, row in patients.iterrows()}

    pname = st.selectbox("Patient", list(pmap.keys()), key="add_pay_select")
    amount = st.number_input("Amount Paid", min_value=0.0, key="add_pay_amount")
    pdate = st.date_input("Payment Date", key="add_pay_date")

    if st.button("Add Payment"):
        execute_query(
            "INSERT INTO Payment (PatientID, AmountPaid, PaymentDate) VALUES (%s, %s, %s)",
            (pmap[pname], amount, pdate)
        )
        st.success("Payment Added!")
        st.rerun()

    # Update payment
    st.subheader("Update Payment")
    try:
        payments = fetch_all("SELECT PaymentID, CONCAT('Payment #', PaymentID, ' - $', AmountPaid, ' on ', PaymentDate) AS label FROM Payment ORDER BY PaymentDate DESC")
        pay_map = {row['label']: row['PaymentID'] for _, row in payments.iterrows()}
        if pay_map:
            sel_pay = st.selectbox("Select payment to update", list(pay_map.keys()), key="upd_pay_select")
            pid = pay_map[sel_pay]
            new_amount = st.number_input("New Amount", min_value=0.0, key="upd_pay_amount")
            if st.button("Update Payment"):
                execute_query("UPDATE Payment SET AmountPaid=%s WHERE PaymentID=%s", (new_amount, pid))
                st.success("Payment updated!")
                st.rerun()
        else:
            st.info("No payments to update")
    except Exception as e:
        st.error(f"Error updating payment: {e}")

    # Delete payment
    st.subheader("Delete Payment")
    try:
        payments = fetch_all("SELECT PaymentID, CONCAT('Payment #', PaymentID, ' - $', AmountPaid, ' on ', PaymentDate) AS label FROM Payment ORDER BY PaymentDate DESC")
        pay_map = {row['label']: row['PaymentID'] for _, row in payments.iterrows()}
        if pay_map:
            sel_pay = st.selectbox("Select payment to delete", list(pay_map.keys()), key="del_pay_select")
            if st.button("Delete Payment"):
                execute_query("DELETE FROM Payment WHERE PaymentID=%s", (pay_map[sel_pay],))
                st.success("Payment deleted!")
                st.rerun()
        else:
            st.info("No payments to delete")
    except Exception as e:
        st.error(f"Error deleting payment: {e}")


# -----------------------------
# Medical Records Page (CRUD)
# -----------------------------
def medical_records_page():
    st.title("Medical Records Management")

    st.subheader("All Medical Records")
    df = fetch_all("""
        SELECT 
            M.RecordID,
            P.Name AS Patient,
            D.Name AS Doctor,
            M.Diagnosis,
            M.Treatment
        FROM MedicalRecord M
        JOIN Patient P ON M.PatientID = P.PatientID
        JOIN Doctor D ON M.DoctorID = D.DoctorID
        ORDER BY M.RecordID DESC
    """)
    st.dataframe(df)

    st.subheader("Add Medical Record")
    patients = fetch_all("SELECT PatientID, Name FROM Patient")
    doctors = fetch_all("SELECT DoctorID, Name FROM Doctor")
    
    pmap = {row["Name"]: row["PatientID"] for _, row in patients.iterrows()}
    dmap = {row["Name"]: row["DoctorID"] for _, row in doctors.iterrows()}

    with st.form("add_record", clear_on_submit=True):
        pname = st.selectbox("Select Patient", list(pmap.keys()), key="med_pat")
        dname = st.selectbox("Select Doctor", list(dmap.keys()), key="med_doc")
        diagnosis = st.text_area("Diagnosis")
        treatment = st.text_area("Treatment")
        submit = st.form_submit_button("Add Record")

    if submit:
        execute_query(
            "INSERT INTO MedicalRecord (PatientID, DoctorID, Diagnosis, Treatment) VALUES (%s, %s, %s, %s)",
            (pmap[pname], dmap[dname], diagnosis, treatment)
        )
        st.success("Medical Record Added!")
        st.rerun()

    # Update record
    st.subheader("Update Medical Record")
    try:
        records = fetch_all("SELECT RecordID, CONCAT('Record #', RecordID, ' - ', Diagnosis) AS label FROM MedicalRecord ORDER BY RecordID DESC")
        rec_map = {row['label']: row['RecordID'] for _, row in records.iterrows()}
        if rec_map:
            sel_rec = st.selectbox("Select record to update", list(rec_map.keys()), key="upd_rec_select")
            rid = rec_map[sel_rec]
            new_diagnosis = st.text_area("New Diagnosis", key="upd_rec_diag")
            new_treatment = st.text_area("New Treatment", key="upd_rec_treat")
            if st.button("Update Record"):
                execute_query("UPDATE MedicalRecord SET Diagnosis=%s, Treatment=%s WHERE RecordID=%s", (new_diagnosis, new_treatment, rid))
                st.success("Record updated!")
                st.rerun()
        else:
            st.info("No records to update")
    except Exception as e:
        st.error(f"Error updating record: {e}")

    # Delete record
    st.subheader("Delete Medical Record")
    try:
        records = fetch_all("SELECT RecordID, CONCAT('Record #', RecordID, ' - ', Diagnosis) AS label FROM MedicalRecord ORDER BY RecordID DESC")
        rec_map = {row['label']: row['RecordID'] for _, row in records.iterrows()}
        if rec_map:
            sel_rec = st.selectbox("Select record to delete", list(rec_map.keys()), key="del_rec_select")
            if st.button("Delete Record"):
                execute_query("DELETE FROM MedicalRecord WHERE RecordID=%s", (rec_map[sel_rec],))
                st.success("Record deleted!")
                st.rerun()
        else:
            st.info("No records to delete")
    except Exception as e:
        st.error(f"Error deleting record: {e}")


# -----------------------------
# Appointment Stats Page
# -----------------------------
def appointment_stats_page():
    st.title("Appointment Analytics & Scheduling")

    st.subheader("Appointments by Doctor")
    try:
        doc_appts = fetch_all("""
            SELECT D.Name, COUNT(A.AppointmentID) AS TotalAppointments
            FROM Doctor D
            LEFT JOIN Appointment A ON D.DoctorID = A.DoctorID
            GROUP BY D.DoctorID, D.Name
            ORDER BY TotalAppointments DESC
        """)
        st.dataframe(doc_appts)
    except Exception as e:
        st.error(f"Error loading doctor appointments: {e}")

    st.subheader("Appointments by Patient")
    try:
        pat_appts = fetch_all("""
            SELECT P.Name, COUNT(A.AppointmentID) AS TotalAppointments
            FROM Patient P
            LEFT JOIN Appointment A ON P.PatientID = A.PatientID
            GROUP BY P.PatientID, P.Name
            ORDER BY TotalAppointments DESC
        """)
        st.dataframe(pat_appts)
    except Exception as e:
        st.error(f"Error loading patient appointments: {e}")

    st.subheader("Doctor Availability (Appointment Schedule)")
    try:
        doctors = fetch_all("SELECT DoctorID, Name FROM Doctor")
        dmap = {row["Name"]: row["DoctorID"] for _, row in doctors.iterrows()}
        if dmap:
            sel_doc = st.selectbox("Select Doctor", list(dmap.keys()))
            did = dmap[sel_doc]
            schedule = fetch_all("""
                SELECT AppointmentID, P.Name AS Patient, AppointmentDate
                FROM Appointment A
                JOIN Patient P ON A.PatientID = P.PatientID
                WHERE A.DoctorID=%s
                ORDER BY AppointmentDate ASC
            """, (did,))
            if not schedule.empty:
                st.dataframe(schedule)
            else:
                st.info(f"No appointments scheduled for {sel_doc}")
        else:
            st.info("No doctors available")
    except Exception as e:
        st.error(f"Error loading schedule: {e}")


# -----------------------------
# Prescription Management Page (CRUD)
# -----------------------------
def prescriptions_page():
    st.title("Prescription Management")

    st.subheader("All Prescriptions")
    df = fetch_all("""
        SELECT 
            P.PrescriptionID,
            Pat.Name AS Patient,
            D.Name AS Doctor,
            P.MedicineName,
            P.Dosage,
            P.Frequency,
            P.StartDate,
            P.EndDate
        FROM Prescription P
        JOIN Patient Pat ON P.PatientID = Pat.PatientID
        JOIN Doctor D ON P.DoctorID = D.DoctorID
        ORDER BY P.PrescriptionID DESC
    """)
    st.dataframe(df)

    st.subheader("Add Prescription")
    patients = fetch_all("SELECT PatientID, Name FROM Patient")
    doctors = fetch_all("SELECT DoctorID, Name FROM Doctor")
    pmap = {row["Name"]: row["PatientID"] for _, row in patients.iterrows()}
    dmap = {row["Name"]: row["DoctorID"] for _, row in doctors.iterrows()}

    with st.form("add_prescription", clear_on_submit=True):
        pname = st.selectbox("Patient", list(pmap.keys()), key="presc_pat")
        dname = st.selectbox("Doctor", list(dmap.keys()), key="presc_doc")
        medicine = st.text_input("Medicine Name")
        dosage = st.text_input("Dosage (e.g., 5mg)")
        frequency = st.text_input("Frequency (e.g., Once daily)")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        notes = st.text_area("Notes", height=100)
        submit = st.form_submit_button("Add Prescription")

    if submit:
        execute_query(
            "INSERT INTO Prescription (PatientID, DoctorID, MedicineName, Dosage, Frequency, StartDate, EndDate, Notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (pmap[pname], dmap[dname], medicine, dosage, frequency, start_date, end_date, notes)
        )
        st.success("Prescription Added!")
        st.rerun()

    st.subheader("Delete Prescription")
    try:
        prescriptions = fetch_all("SELECT PrescriptionID, CONCAT('Presc #', PrescriptionID, ' - ', MedicineName) AS label FROM Prescription ORDER BY PrescriptionID DESC")
        presc_map = {row['label']: row['PrescriptionID'] for _, row in prescriptions.iterrows()}
        if presc_map:
            sel = st.selectbox("Select prescription to delete", list(presc_map.keys()), key="del_presc")
            if st.button("Delete Prescription"):
                execute_query("DELETE FROM Prescription WHERE PrescriptionID=%s", (presc_map[sel],))
                st.success("Prescription deleted!")
                st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")


# -----------------------------
# Lab Tests Management Page (CRUD)
# -----------------------------
def lab_tests_page():
    st.title("Lab Tests Management")

    st.subheader("All Lab Tests")
    df = fetch_all("""
        SELECT 
            L.TestID,
            Pat.Name AS Patient,
            D.Name AS Doctor,
            L.TestName,
            L.TestDate,
            L.Status,
            L.Result
        FROM LabTest L
        JOIN Patient Pat ON L.PatientID = Pat.PatientID
        JOIN Doctor D ON L.DoctorID = D.DoctorID
        ORDER BY L.TestID DESC
    """)
    st.dataframe(df)

    st.subheader("Add Lab Test")
    patients = fetch_all("SELECT PatientID, Name FROM Patient")
    doctors = fetch_all("SELECT DoctorID, Name FROM Doctor")
    pmap = {row["Name"]: row["PatientID"] for _, row in patients.iterrows()}
    dmap = {row["Name"]: row["DoctorID"] for _, row in doctors.iterrows()}

    with st.form("add_lab_test", clear_on_submit=True):
        pname = st.selectbox("Patient", list(pmap.keys()), key="lab_pat")
        dname = st.selectbox("Doctor", list(dmap.keys()), key="lab_doc")
        test_name = st.text_input("Test Name")
        test_date = st.date_input("Test Date")
        submit = st.form_submit_button("Add Test")

    if submit:
        execute_query(
            "INSERT INTO LabTest (PatientID, DoctorID, TestName, TestDate, Status) VALUES (%s, %s, %s, %s, %s)",
            (pmap[pname], dmap[dname], test_name, test_date, 'Pending')
        )
        st.success("Lab Test Added!")
        st.rerun()

    st.subheader("Update Test Status & Result")
    try:
        tests = fetch_all("SELECT TestID, CONCAT('Test #', TestID, ' - ', TestName, ' (', Status, ')') AS label FROM LabTest ORDER BY TestID DESC")
        test_map = {row['label']: row['TestID'] for _, row in tests.iterrows()}
        if test_map:
            sel = st.selectbox("Select test to update", list(test_map.keys()), key="upd_test")
            tid = test_map[sel]
            status = st.selectbox("Status", ["Pending", "Completed", "Cancelled"])
            result = st.text_area("Result", key="test_result")
            if st.button("Update Test"):
                execute_query("UPDATE LabTest SET Status=%s, Result=%s WHERE TestID=%s", (status, result, tid))
                st.success("Test updated! (Completion may trigger billing)")
                st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")


# -----------------------------
# Rooms & Occupancy Page
# -----------------------------
def rooms_page():
    st.title("Hospital Rooms & Occupancy")

    st.subheader("All Rooms")
    df = fetch_all("""
        SELECT 
            R.RoomID,
            R.RoomNumber,
            R.RoomType,
            R.Capacity,
            D.DepartmentName,
            CASE WHEN R.IsOccupied THEN 'Occupied' ELSE 'Vacant' END AS Status,
            Pat.Name AS CurrentPatient
        FROM Room R
        LEFT JOIN Department D ON R.DepartmentID = D.DepartmentID
        LEFT JOIN Patient Pat ON R.CurrentPatientID = Pat.PatientID
        ORDER BY R.RoomNumber
    """)
    st.dataframe(df)

    st.subheader("Check-in Patient to Room")
    try:
        patients = fetch_all("SELECT PatientID, Name FROM Patient")
        rooms = fetch_all("SELECT RoomID, CONCAT(RoomNumber, ' (', RoomType, ')') AS label FROM Room WHERE IsOccupied=FALSE")
        pmap = {row["Name"]: row["PatientID"] for _, row in patients.iterrows()}
        rmap = {row['label']: row['RoomID'] for _, row in rooms.iterrows()}
        
        if pmap and rmap:
            pname = st.selectbox("Select Patient", list(pmap.keys()), key="room_pat")
            rname = st.selectbox("Select Room", list(rmap.keys()), key="room_sel")
            if st.button("Check In"):
                pid = pmap[pname]
                rid = rmap[rname]
                execute_query("UPDATE Room SET IsOccupied=TRUE, CurrentPatientID=%s WHERE RoomID=%s", (pid, rid))
                st.success(f"Patient checked in! (Trigger logs this action)")
                st.rerun()
        else:
            st.info("No available rooms or patients")
    except Exception as e:
        st.error(f"Error: {e}")

    st.subheader("Check-out Patient from Room")
    try:
        rooms = fetch_all("SELECT RoomID, CONCAT(RoomNumber, ' - ', Pat.Name) AS label FROM Room R JOIN Patient Pat ON R.CurrentPatientID=Pat.PatientID WHERE R.IsOccupied=TRUE")
        rmap = {row['label']: row['RoomID'] for _, row in rooms.iterrows()}
        if rmap:
            rname = st.selectbox("Select Room to Checkout", list(rmap.keys()), key="checkout_room")
            if st.button("Check Out"):
                rid = rmap[rname]
                execute_query("UPDATE Room SET IsOccupied=FALSE, CurrentPatientID=NULL WHERE RoomID=%s", (rid,))
                st.success("Patient checked out!")
                st.rerun()
        else:
            st.info("No occupied rooms")
    except Exception as e:
        st.error(f"Error: {e}")


# -----------------------------
# Departments Page
# -----------------------------
def departments_page():
    st.title("Departments Management")

    st.subheader("All Departments")
    df = fetch_all("""
        SELECT 
            D.DepartmentID,
            D.DepartmentName,
            Doc.Name AS HeadDoctor,
            D.Phone,
            COUNT(DISTINCT R.RoomID) AS TotalRooms
        FROM Department D
        LEFT JOIN Doctor Doc ON D.HeadDoctor = Doc.DoctorID
        LEFT JOIN Room R ON D.DepartmentID = R.DepartmentID
        GROUP BY D.DepartmentID, D.DepartmentName, D.HeadDoctor, Doc.Name, D.Phone
    """)
    st.dataframe(df)

    st.subheader("Add Department")
    doctors = fetch_all("SELECT DoctorID, Name FROM Doctor")
    dmap = {row["Name"]: row["DoctorID"] for _, row in doctors.iterrows()}

    with st.form("add_dept", clear_on_submit=True):
        dept_name = st.text_input("Department Name")
        head_doc = st.selectbox("Head Doctor", list(dmap.keys()), key="head_doc")
        phone = st.text_input("Phone")
        submit = st.form_submit_button("Add Department")

    if submit:
        execute_query(
            "INSERT INTO Department (DepartmentName, HeadDoctor, Phone) VALUES (%s, %s, %s)",
            (dept_name, dmap[head_doc], phone)
        )
        st.success("Department Added!")
        st.rerun()


# -----------------------------
# Trigger Logs & Monitoring Page
# -----------------------------
def trigger_logs_page():
    st.title("Database Triggers - Action Logs & Monitoring")

    st.subheader("Real-Time Trigger Action Log")
    st.info("This shows all automatic actions triggered by database events (payments, lab test completions, room changes, etc.)")
    
    logs = fetch_all("""
        SELECT 
            LogID,
            TriggerName,
            ActionType,
            TableName,
            NewValue,
            ActionTimestamp
        FROM TriggerActionLog
        ORDER BY ActionTimestamp DESC
        LIMIT 50
    """)
    
    if not logs.empty:
        st.dataframe(logs)
    else:
        st.info("No trigger actions logged yet. (Logs appear when: payments are made, lab tests completed, rooms change occupancy, prescriptions added)")

    st.subheader("Trigger Event Breakdown")
    try:
        breakdown = fetch_all("""
            SELECT TriggerName, COUNT(*) AS EventCount, MAX(ActionTimestamp) AS LastFired
            FROM TriggerActionLog
            GROUP BY TriggerName
            ORDER BY EventCount DESC
        """)
        st.dataframe(breakdown)
    except Exception as e:
        st.error(f"Error: {e}")

    st.subheader("Active Triggers in Database")
    try:
        trig_query = """
            SELECT TRIGGER_NAME, EVENT_MANIPULATION AS Event, EVENT_OBJECT_TABLE AS TableName,
                   ACTION_TIMING AS Timing
            FROM information_schema.TRIGGERS
            WHERE TRIGGER_SCHEMA = 'hospital_management'
        """
        trig_df = fetch_all(trig_query)
        st.dataframe(trig_df)
    except Exception as e:
        st.error(f"Could not fetch triggers: {e}")

    st.subheader("Clear Trigger Logs (Admin)")
    if st.button("Clear All Logs", key="clear_logs"):
        execute_query("DELETE FROM TriggerActionLog")
        st.success("Logs cleared!")
        st.rerun()


# -----------------------------
# Sidebar
# -----------------------------
def sidebar_menu():
    with st.sidebar:
        st.title("Navigation")

        st.session_state.page = st.radio(
            "Go to:",
            ["Dashboard", "Patients", "Doctors", "Appointments", "Appointment Stats", 
             "Billing", "Payments", "Medical Records", "Prescriptions", "Lab Tests", 
             "Departments", "Rooms", "Trigger Logs", "DB Objects"]
        )

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()


# -----------------------------
# MAIN
# -----------------------------
def main():
    if not st.session_state.logged_in:
        login_page()
        return

    sidebar_menu()

    if st.session_state.page == "Dashboard":
        dashboard_page()
    elif st.session_state.page == "Patients":
        patients_page()
    elif st.session_state.page == "Doctors":
        doctors_page()
    elif st.session_state.page == "Appointments":
        appointments_page()
    elif st.session_state.page == "Appointment Stats":
        appointment_stats_page()
    elif st.session_state.page == "Billing":
        billing_page()
    elif st.session_state.page == "Payments":
        payments_page()
    elif st.session_state.page == "Medical Records":
        medical_records_page()
    elif st.session_state.page == "Prescriptions":
        prescriptions_page()
    elif st.session_state.page == "Lab Tests":
        lab_tests_page()
    elif st.session_state.page == "Departments":
        departments_page()
    elif st.session_state.page == "Rooms":
        rooms_page()
    elif st.session_state.page == "Trigger Logs":
        trigger_logs_page()
    elif st.session_state.page == "DB Objects":
        db_objects_page()


# -----------------------------
# DB Objects Page
# -----------------------------
def db_objects_page():
    st.title("Database Objects & Routines")

    st.subheader("Triggers in Database")
    try:
        trig_query = """
            SELECT TRIGGER_NAME, EVENT_MANIPULATION AS Event, EVENT_OBJECT_TABLE AS TableName,
                   ACTION_TIMING AS Timing, ACTION_STATEMENT AS Statement
            FROM information_schema.TRIGGERS
            WHERE TRIGGER_SCHEMA = 'hospital_management'
        """
        trig_df = fetch_all(trig_query)
        st.dataframe(trig_df)
    except Exception as e:
        st.error(f"Could not fetch triggers: {e}")

    st.subheader("Routines (Functions / Procedures)")
    try:
        rout_query = """
            SELECT ROUTINE_NAME, ROUTINE_TYPE, DTD_IDENTIFIER AS ReturnType, ROUTINE_DEFINITION
            FROM information_schema.ROUTINES
            WHERE ROUTINE_SCHEMA = 'hospital_management'
        """
        rout_df = fetch_all(rout_query)
        st.dataframe(rout_df)
    except Exception as e:
        st.error(f"Could not fetch routines: {e}")

    st.subheader("Function: Get Patient Balance")
    try:
        patients = fetch_all("SELECT PatientID, Name FROM Patient ORDER BY PatientID")
        pmap = {row['Name']: row['PatientID'] for _, row in patients.iterrows()}
        if pmap:
            pname = st.selectbox("Select patient (to compute balance)", list(pmap.keys()))
            if st.button("Get Balance"):
                pid = pmap[pname]
                try:
                    bal = call_function('FN_GET_PATIENT_BALANCE', (pid,))
                    st.info(f"Patient {pname} (ID {pid}) balance: {bal}")
                except Exception as e:
                    st.error(f"Error calling function: {e}")
        else:
            st.info("No patients found to compute balance.")
    except Exception as e:
        st.error(f"Could not prepare patient list: {e}")

    st.subheader("Procedure: Add New Doctor (SP_ADD_NEW_DOCTOR)")
    with st.form("add_doctor_sp", clear_on_submit=True):
        dname = st.text_input("Doctor Name")
        dspec = st.text_input("Specialization")
        dphone = st.text_input("Phone")
        submit_sp = st.form_submit_button("Add via Stored Procedure")

    if submit_sp:
        if not dname or not dspec:
            st.error("Name and Specialization are required")
        else:
            try:
                results = call_procedure('SP_ADD_NEW_DOCTOR', (dname, dspec, dphone))
                # call_procedure returns list of result sets; show them
                if results:
                    for i, rs in enumerate(results):
                        st.write(f"Result set {i+1}:")
                        try:
                            df = pd.DataFrame(rs)
                            st.dataframe(df)
                        except Exception:
                            st.write(rs)
                else:
                    st.success("Procedure executed (no results returned)")
                st.rerun()
            except Exception as e:
                st.error(f"Error calling stored procedure: {e}")


if __name__ == "__main__":
    main()
