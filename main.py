import streamlit as st
import hashlib
from utils.db_helpers import fetch_one, fetch_all, execute_query

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

    st.subheader("Patients Overview")
    df = fetch_all("SELECT * FROM Patient")
    st.dataframe(df)


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

    df = fetch_all("SELECT * FROM Doctor ORDER BY DoctorID")
    st.dataframe(df)


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

    # Delete
    st.subheader("Delete Appointment")
    appt_id = st.number_input("AppointmentID", min_value=1)
    if st.button("Delete Appointment"):
        execute_query("DELETE FROM Appointment WHERE AppointmentID=%s", (appt_id,))
        st.success("Deleted successfully.")
        st.rerun()


# -----------------------------
# Billing Page (Add / View Bills)
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

    st.subheader("Add Bill")
    patients = fetch_all("SELECT PatientID, Name FROM Patient")
    pmap = {row["Name"]: row["PatientID"] for _, row in patients.iterrows()}

    pname = st.selectbox("Select patient", list(pmap.keys()))
    amount = st.number_input("Amount", min_value=0.0)
    bdate = st.date_input("Billing Date")

    if st.button("Add Bill"):
        execute_query(
            "INSERT INTO Billing (PatientID, Amount, BillingDate) VALUES (%s, %s, %s)",
            (pmap[pname], amount, bdate)
        )
        st.success("Bill Added!")
        st.rerun()


# -----------------------------
# Payments Page (Add / View)
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

    st.subheader("Add Payment")
    patients = fetch_all("SELECT PatientID, Name FROM Patient")
    pmap = {row["Name"]: row["PatientID"] for _, row in patients.iterrows()}

    pname = st.selectbox("Patient", list(pmap.keys()))
    amount = st.number_input("Amount Paid", min_value=0.0)
    pdate = st.date_input("Payment Date")

    if st.button("Add Payment"):
        execute_query(
            "INSERT INTO Payment (PatientID, AmountPaid, PaymentDate) VALUES (%s, %s, %s)",
            (pmap[pname], amount, pdate)
        )
        st.success("Payment Added!")
        st.rerun()


# -----------------------------
# Sidebar
# -----------------------------
def sidebar_menu():
    with st.sidebar:
        st.title("Navigation")

        st.session_state.page = st.radio(
            "Go to:",
            ["Dashboard", "Patients", "Doctors", "Appointments", "Billing", "Payments"]
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
    elif st.session_state.page == "Billing":
        billing_page()
    elif st.session_state.page == "Payments":
        payments_page()


if __name__ == "__main__":
    main()
