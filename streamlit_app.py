import streamlit as st
import requests
import pandas as pd
from datetime import date
import google.generativeai as genai
import datetime
from dateutil.relativedelta import relativedelta
from streamlit_qrcode_scanner import qrcode_scanner
import streamlit.components.v1 as components
import altair as alt
import plotly.express as px

# ... baki saare imports jo aapke paas hain ...

# 1. Sabse pehle Page Config (Ye hamesha top par hona chahiye)
st.set_page_config(page_title="School Management System", layout="wide")
API_BASE = "http://127.0.0.1:8000/api"

# 2. Session State Initialize karna (Taki login yaad rahe)
if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = False
if "user_token" not in st.session_state:
    st.session_state["user_token"] = ""


def apply_professional_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Source+Serif+4:wght@600&display=swap');

        :root {
            --bg: #f4f7fb;
            --panel: #ffffff;
            --ink: #0f172a;
            --muted: #475569;
            --line: #dbe3ef;
            --brand: #0f766e;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 8%, #dff6f2 0%, transparent 34%),
                radial-gradient(circle at 88% 4%, #fff1dc 0%, transparent 30%),
                linear-gradient(180deg, #f8fbff 0%, var(--bg) 70%);
            color: var(--ink);
            font-family: "Manrope", sans-serif;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        section[data-testid="stSidebar"] * {
            color: #e2e8f0 !important;
        }

        .hero-title {
            font-family: "Source Serif 4", serif;
            color: #0b172a;
            margin-bottom: 0.15rem;
            letter-spacing: 0.2px;
        }

        .hero-subtitle {
            color: var(--muted);
            margin-bottom: 1rem;
        }

        .metric-card {
            background: linear-gradient(180deg, #ffffff 0%, #f9fcff 100%);
            border: 1px solid var(--line);
            border-left: 4px solid var(--brand);
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
            min-height: 120px;
        }

        .metric-label {
            color: #64748b;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .metric-value {
            color: #0f172a;
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.1;
            margin-top: 6px;
        }

        .metric-note {
            color: #0f766e;
            font-size: 0.8rem;
            margin-top: 8px;
        }

        .section-title {
            font-size: 1rem;
            color: #0f172a;
            font-weight: 700;
            margin: 0.2rem 0 0.8rem 0;
        }

        .stButton > button {
            border-radius: 10px;
            font-weight: 700;
        }

        @media (max-width: 768px) {
            .metric-value { font-size: 1.6rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_professional_theme()

# ----------------- LOGIN PAGE -----------------
def show_login():
    left, center, right = st.columns([1, 1.3, 1])
    with center:
        st.markdown("<h1 class='hero-title'>School ERP Console</h1>", unsafe_allow_html=True)
        st.markdown("<p class='hero-subtitle'>Secure admin access for operations, academics and analytics.</p>", unsafe_allow_html=True)
        with st.container(border=True):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Sign In", use_container_width=True, type="primary"):
                try:
                    res = requests.post(
                        f"{API_BASE}/login/",
                        json={"username": username, "password": password},
                    )
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state["is_logged_in"] = True
                        st.session_state["user_token"] = data["token"]
                        st.success("Login successful.")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                except Exception as e:
                    if "RerunData" in str(type(e)) or "RerunException" in str(type(e)):
                        raise e
                    st.error(f"Backend server is offline. Error: {e}")

# ----------------- MAIN APP DASHBOARD -----------------
def show_main_app():
    # --- 1. SIDEBAR TOP: LOGO & BRANDING ---
    with st.sidebar:
        # Logo Image (Check karein ki logo.png aapke folder mein ho)
        try:
            st.image("media/logo.png", use_container_width=True)
        except:
            st.markdown("GLOBAL ACADEMY") # Agar image na mile toh text dikhega
    
    # Sidebar ke baaki menu items ke baad niche ek divider
    st.sidebar.markdown("---")
    
    # Logout Button with Red Color and Icon
    # type="primary" use karne se ye Red ya themed color mein highlight ho jayega
    if st.sidebar.button("Logout", type="primary", use_container_width=True):
        st.session_state["is_logged_in"] = False
        st.session_state.clear() # Ye session saaf kar dega security ke liye
        st.rerun()
# ---------------- SIDEBAR MENU -----------------
    st.sidebar.markdown("### School Operations")
    menu = st.sidebar.radio(
        "Navigate",
        ["Dashboard", "Admission", "Staff", "Academics", "Attendance", "Accounts", "Examination", "School LLM"]
    )
# ---------------- DASHBOARD PAGE ----------------
    if menu == "Dashboard":
        st.markdown("<h1 class='hero-title'>School Command Center</h1>", unsafe_allow_html=True)
        st.markdown("<p class='hero-subtitle'>Real-time institutional metrics and operational insights.</p>", unsafe_allow_html=True)

        try:
            res = requests.get(f"{API_BASE}/dashboard-stats/")
            if res.status_code == 200:
                stats = res.json()
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(
                        f"""
                        <div class='metric-card'>
                            <div class='metric-label'>Total Students</div>
                            <div class='metric-value'>{stats['total_students']}</div>
                            <div class='metric-note'>Updated from live database</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c2:
                    st.markdown(
                        f"""
                        <div class='metric-card'>
                            <div class='metric-label'>Today's Attendance</div>
                            <div class='metric-value'>{stats['attendance_percent']}%</div>
                            <div class='metric-note'>{stats['present_today']} present today</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c3:
                    st.markdown(
                        f"""
                        <div class='metric-card'>
                            <div class='metric-label'>Total Staff</div>
                            <div class='metric-value'>{stats['total_staff']}</div>
                            <div class='metric-note'>Active workforce snapshot</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        except Exception:
            st.error("Unable to load dashboard stats.")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("<div class='section-title'>Section-wise Attendance</div>", unsafe_allow_html=True)
            try:
                res = requests.get(f"{API_BASE}/dashboard/today-attendance/")
                if res.status_code == 200:
                    df = pd.DataFrame(res.json())
                    chart = (
                        alt.Chart(df)
                        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
                        .encode(
                            x=alt.X("class:N", axis=alt.Axis(labelColor="#334155", title=None)),
                            y=alt.Y("present:Q", axis=alt.Axis(labelColor="#334155", title="Present Students")),
                            color=alt.Color(
                                "section:N",
                                scale=alt.Scale(range=["#0f766e", "#d97706", "#0284c7", "#b45309"]),
                            ),
                            tooltip=["class", "section", "present"],
                        )
                        .properties(height=330)
                        .configure_view(strokeOpacity=0)
                    )
                    st.altair_chart(chart, use_container_width=True)
            except Exception:
                st.warning("Unable to load attendance analytics.")

        with col_right:
            st.markdown("<div class='section-title'>Class-wise Fee Distribution</div>", unsafe_allow_html=True)
            try:
                res = requests.get(f"{API_BASE}/dashboard/class-income/")
                if res.status_code == 200:
                    df = pd.DataFrame(res.json())
                    fig = px.pie(
                        df,
                        names="class",
                        values="collected",
                        hole=0.58,
                        color_discrete_sequence=["#0f766e", "#d97706", "#0284c7", "#7c3aed", "#b45309"],
                    )
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        legend_font_color="#334155",
                        margin=dict(t=0, b=0, l=0, r=0),
                        annotations=[
                            dict(
                                text="Fees",
                                x=0.5,
                                y=0.5,
                                font_size=20,
                                showarrow=False,
                                font_color="#0f172a",
                            )
                        ],
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception:
                st.warning("Unable to load financial data.")


    # ---------------- ADMISSION PAGE ----------------
    elif menu == "Admission":
        st.title("📝 Student Admission Form")
        API_BASE = "http://127.0.0.1:8000/api"

        # ---- FETCH CLASSES FROM BACKEND ----
        class_res = requests.get(f"{API_BASE}/classes/")
        class_data = class_res.json()

        # Example label:  "Class 5 - A"
        class_map = {f"{c['name']} - {c['section']}": c for c in class_data}

        with st.form("admission_form"):

            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Student Name")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                dob = st.date_input("Student DOB")
                admission_date = st.date_input("Admission Date", value=date.today())
                # 🔹 DYNAMIC CLASS SELECT
                selected_class_label = st.selectbox(
                    "Class",
                    class_map.keys()
                )

                # backend object
                selected_class = class_map[selected_class_label]

                # 🔹 SECTION automatically
                student_class = selected_class["name"]
                section = selected_class["section"]

                # st.info(f"Selected Section: **{section}**")

            with col2:
                father_name = st.text_input("Father Name")
                father_phone = st.text_input("Phone Number (10 digits)", 
                max_chars=10,
                help="Enter 10 digit mobile number")

                if father_phone:
                    if len(father_phone) != 10 or not father_phone.isdigit():
                        st.error("❌ Please enter exactly 10 digits")
                    else:
                        st.success("✅ Valid phone number")
                        
                mother_name = st.text_input("Mother Name")
                mother_phone = st.text_input("Mother Phone")
                address = st.text_input("Address")
                student_document = st.file_uploader(
                        "Upload Student Document (PDF only)",
                        type=["pdf"]
    )

            remarks = st.text_area("Remarks")

            submit = st.form_submit_button("Submit Admission")

            if submit:
                if not name or not father_name or not mother_name:
                    st.warning("⚠️ Please fill all required fields")
                else:
                    # Backend data preparation
                    selected_class = class_map[selected_class_label]
                    student_class = selected_class["name"]
                    section = selected_class["section"]

                    payload = {
                        "name": name,
                        "gender": gender,
                        "dob": str(dob),
                        "admission_date": str(admission_date),
                        "student_class": student_class,
                        "section": section,
                        "father_name": father_name,
                        "father_phone": father_phone,
                        "mother_name": mother_name,
                        "mother_phone": mother_phone,
                        "address": address,
                        "remarks": remarks,
                    }

                    files = {}
                    if student_document:
                        files["document"] = student_document

                    # API Call sirf tabhi hogi jab button dabega
                    with st.spinner("Saving data..."):
                        res = requests.post(
                            f"{API_BASE}/students/create/",
                            data=payload,
                            files=files
                        )

                    if res.status_code == 200:
                        st.success("🎉 Student admission saved successfully!")
                    else:
                        st.error(f"❌ Failed to save: {res.text}")

    # ---------------- STAFF PAGE ----------------
    elif menu == "Staff":
        st.title("👨‍🏫 Staff Registration Form")

        with st.form("staff_form"):

            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Staff Name")
                phone = st.text_input("Phone Number (10 digits)", 
                max_chars=10,
                help="Enter 10 digit mobile number")

                if phone:
                    if len(phone) != 10 or not phone.isdigit():
                        st.error("❌ Please enter exactly 10 digits")
                    else:
                        st.success("✅ Valid phone number")

                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                today = datetime.date.today()
                min_birth_date = today - relativedelta(years=18)
                max_birth_date = today - relativedelta(years=60)
                dob = st.date_input(
                "Select Date of Birth",
                value=min_birth_date,  # Default 18 years ago set karein
                min_value=max_birth_date,  # Optional: maximum age limit
                max_value=min_birth_date,  # Minimum age limit (18 years)
                format="DD/MM/YYYY",
                help=f"Student must be at least 18 years old. Select date before {min_birth_date.strftime('%d/%m/%Y')}"
            )
                aadhaar = st.text_input("Aadhaar Card Number")
                joining_date = st.date_input("Joining Date", value=date.today())

            with col2:
                father_name = st.text_input("Father Name")
                marital_status = st.selectbox(
                    "Marital Status",
                    ["Single", "Married", "Other"]
                )
                role = st.selectbox(
                    "Staff Role",
                    ["Teacher", "Principal", "Security Guard", "Cleaner", "Other"]
                )

                staff_document = st.file_uploader(
                    "Upload Staff Document (PDF only)",
                    type=["pdf"]
                )

            remarks = st.text_area("Remarks")

            submit_staff = st.form_submit_button("Submit Staff Details")

        if submit_staff:
            if not name or not father_name:
                st.warning("Please fill all required fields")
                st.stop()
            payload = {
                "name": name,
                "phone": phone,
                "gender": gender,
                "dob": str(dob),
                "aadhaar": aadhaar,
                "joining_date": str(joining_date),
                "father_name": father_name,
                "marital_status": marital_status,
                "role": role,
                "remarks": remarks,
            }

            API_BASE = "http://127.0.0.1:8000/api"

            files = {}
            if staff_document:
                files["document"] = staff_document

            # 🔥 always send request — doc ho ya na ho
            response = requests.post(
                f"{API_BASE}/staff/create/",
                data=payload,
                files=files
            )

            if response.status_code == 200:
                st.success("🎉 Staff saved successfully!")
            else:
                st.error("❌ Failed to save staff")
                st.write(response.text)


    # ---------- ACADEMICS ----------
    elif menu == "Academics":


        st.title("📚 Academics")

        academic_option = st.radio(
            "Academics Options",
            [
                "Subject Creation",
                "Class Creation",
                "Class Time Table",
                "Promote"
                
            ],
            horizontal=True
        )

        # ----- SUBJECT CREATION -----
        if academic_option == "Subject Creation":
            st.subheader("📘 Subject Creation")

            subject_name = st.text_input("Subject Name")

            if st.button("Add Subject"):
                if not subject_name:
                    st.warning("Please enter subject name")
                else:
                    response = requests.post(
                        "http://127.0.0.1:8000/api/subjects/create/",
                        json={"name": subject_name}
                    )

                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"Subject '{data['name']}' added successfully")
                    else:
                        st.error("Something went wrong")

        # ----- CLASS CREATION -----
        elif academic_option == "Class Creation":
            st.subheader("🏫 Class Creation")

            col1, col2 = st.columns(2)

            with col1:
                class_name = st.text_input("Class Name", placeholder="e.g. Class 5")
                section = st.text_input("Section", placeholder="A / B / C")

            with col2:
                response = requests.get("http://127.0.0.1:8000/api/subjects/")
                subject_data = response.json()
                subject_map = {s["name"]: s["id"] for s in subject_data}
                subjects = st.multiselect(
                    "Select Subjects",
                    list(subject_map.keys()))


                st.markdown("---")

            if st.button("Create Class"):
                if not class_name or not section:
                    st.warning("Class Name and Section are required")
                elif not subjects:
                    st.warning("Please select at least one subject")
                else:
                    subject_ids = [subject_map[s] for s in subjects]
                    payload={"name": class_name,
                            "section": section,
                            "subjects": subject_ids}
                    res = requests.post(
                        "http://127.0.0.1:8000/api/class/create/",
                        json=payload)
                    if res.status_code == 200:
                        st.success("Class created successfully")
                    else:
                        st.error("Failed to create class")  


    #---------------- TIME TABLE ----------------
        elif academic_option == "Class Time Table":
            st.subheader("⏰ Class Time Table")
            API_BASE = "http://127.0.0.1:8000/api"

            # ---------- SESSION STATE ----------
            if "show_timetable" not in st.session_state:
                st.session_state.show_timetable = False

            # ---------- FETCH CLASSES ----------
            class_res = requests.get(f"{API_BASE}/classes/")
            class_data = class_res.json()

            class_map = {f"{c['name']} - {c['section']}": c["id"] for c in class_data}

            col1, col2 = st.columns(2)

            with col1:
                selected_class_label = st.selectbox("Select Class *", class_map.keys())

            with col2:
                selected_section = selected_class_label.split("-")[1].strip()

            # ---------- OPEN BUTTON ----------
            if st.button("Open Time Table"):
                st.session_state.show_timetable = True

            st.markdown("---")

            # ---------- TIME TABLE UI ----------
            if st.session_state.show_timetable:

                class_id = class_map[selected_class_label]

                # 🔹 Fetch subjects of class
                subject_res = requests.get(
                    f"{API_BASE}/class-subjects/{class_id}/"
                )

                subject_data = subject_res.json()
                subjects = [s["subject_name"] for s in subject_data]

                if not subjects:
                    st.warning("No subjects assigned to this class")
                    st.stop()

                teacher_res = requests.get(f"{API_BASE}/teachers/")
                teacher_data = teacher_res.json()
                teachers = [""] + [t["name"] for t in teacher_data]

                # ---------- DAYS ----------
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                tabs = st.tabs(days)

                periods_per_day = len(subjects)

                for day_index, day in enumerate(days):
                    with tabs[day_index]:
                        st.markdown(f"### 📅 {day}")

                        timetable_payload = []

                        for i in range(periods_per_day):
                            st.markdown(f"**Period {i+1}**")

                            c1, c2, c3, c4 = st.columns(4)

                            with c1:
                                subject = st.selectbox(
                                    "Subject",
                                    subjects,
                                    key=f"{day}_sub_{i}"
                                )

                            with c2:
                                teacher = st.selectbox(
                                    "Teacher",
                                    teachers,
                                    key=f"{day}_teacher_{i}"
                                )

                            with c3:
                                time_from = st.time_input(
                                    "Time From",
                                    key=f"{day}_from_{i}"
                                )

                            with c4:
                                time_to = st.time_input(
                                    "Time To",
                                    key=f"{day}_to_{i}"
                                )

                            timetable_payload.append({
                                "day": day,
                                "period": i + 1,
                                "subject": subject,
                                "teacher": teacher,
                                "time_from": str(time_from),
                                "time_to": str(time_to),
                            })

                            st.markdown("---")

                        # ---------- SAVE ----------
                        if st.button(f"Save {day} Time Table", key=f"save_{day}"):

                            payload = {
                                "class_id": class_id,
                                "section": selected_section,
                                "day": day,
                                "periods": timetable_payload
                            }

                            res = requests.post(
                                f"{API_BASE}/save-timetable/",
                                json=payload
                            )

                            if res.status_code == 200:
                                st.success(f"{day} timetable saved successfully ✅")
                            else:
                                st.error("❌ Failed to save timetable")


        # ----- PROMOTE STUDENTS -----
        elif academic_option == "Promote":
            st.subheader("⬆️ Promote Students")
            API_BASE = "http://127.0.0.1:8000/api"

            # Fetch Classes
            class_res = requests.get(f"{API_BASE}/classes/")
            class_data = class_res.json()
            class_map = {f"{c['name']} - {c['section']}": c["id"] for c in class_data}

            col1, col2 = st.columns(2)
            with col1:
                current_class_label = st.selectbox("Current Class (from)", list(class_map.keys()))
            with col2:
                target_class_label = st.selectbox("Target Class (to)", list(class_map.keys()))

            current_class_id = class_map[current_class_label]
            target_class_id = class_map[target_class_label]
            target_section = target_class_label.split("-")[1].strip()

            # Load Students
            if st.button("📥 Load Students"):
                res = requests.get(f"{API_BASE}/students/", params={"class_id": current_class_id})
                if res.status_code == 200:
                    st.session_state["promote_students"] = res.json()
                    # Naye students aate hi purani selection clear karein
                    st.session_state["selected_labels"] = [f"{s['name']} (ID:{s['id']})" for s in res.json()]
                else:
                    st.error("Failed to load students")

            students = st.session_state.get("promote_students", [])

            if students:
                student_labels = [f"{s['name']} (ID:{s['id']})" for s in students]
                student_map = {label: s["id"] for label, s in zip(student_labels, students)}

                # UI for Select All / Unselect All
                c_a, c_b = st.columns(2)
                if c_a.button("✅ Select All"):
                    st.session_state["student_multi"] = student_labels
                    st.rerun()
                if c_b.button("❌ Unselect All"):
                    st.session_state["student_multi"] = []
                    st.rerun()

                selected_labels = st.multiselect(
                    "Select Students",
                    options=student_labels,
                    key="student_multi" # State management automatic ho jayegi
                )

                st.write(f"Selected: **{len(selected_labels)} / {len(students)}**")

                if st.button("🚀 Promote Selected Students", type="primary"):
                    if not selected_labels:
                        st.warning("Please select at least one student")
                    else:
                        selected_ids = [student_map[l] for l in selected_labels]
                        payload = {
                            "student_ids": selected_ids,
                            "target_class_id": target_class_id,
                            "target_section": target_section
                        }
                        r = requests.post(f"{API_BASE}/students/promote/", json=payload)
                        if r.status_code == 200:
                            st.success("🎉 Promotion Successful!")
                            st.session_state["promote_students"] = [] # Clear list after success
                            st.rerun()
                        else:
                            st.error(f"Error: {r.text}")

    # ...existing code...
        
     
    # ------------------------------------------------------
    elif menu == "Attendance":
        st.title("🎟️ Smart QR Attendance")

        # Scanner setup

        # 1. Scanner UI
        st.subheader("📷 Scan Student QR")
        # Jaise hi scan hoga, ye variable update hoga
        scanned_id = qrcode_scanner(key='qr_attendance_scanner')

        # 2. Processing Logic
        if scanned_id:  
            # Check: Kya ye ID abhi process hui hai? (Taaki loop na bane)
            if "last_id" not in st.session_state or st.session_state.last_id != scanned_id:
                
                API_URL = "http://127.0.0.1:8000/api/mark-attendance/"
                
                try:
                    # Python ke zariye API call (CORS ki zaroorat nahi padegi)
                    res = requests.post(API_URL, json={"student_id": scanned_id.strip()})
                    
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.last_id = scanned_id # ID lock kar dein
                        
                        st.balloons()
                        st.success(f"✅ Attendance Marked: {data.get('name')}")
                        
                        # Display Student Card
                        st.markdown(f"""
                            <div style="background-color: #d4edda; padding: 20px; border-radius: 10px; border-left: 8px solid #28a745;">
                                <h2 style="color: #155724; margin: 0;">{data.get('name')}</h2>
                                <p style="color: #155724; font-size: 18px;">
                                    <b>Class:</b> {data.get('class')} | <b>Roll:</b> {data.get('roll')}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"❌ Error: {res.json().get('message')}")
                        st.session_state.last_id = scanned_id # Error par bhi lock karein taaki spam na ho
                        
                except Exception as e:
                    st.error(f"📡 Connection Error: {e}")

        # 3. Next Student Button (Scanner Reset)
        if st.button("🔄 Next Student"):
            st.session_state.last_id = None
            st.rerun()





    # ---------------- SCHOOL LLM PAGE ----------------
    elif menu == "School LLM":
        st.title("🤖 AI School Query Assistant")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # --- Show previous messages ---
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # --- User Input Box (chat style) ---
        user_query = st.chat_input("Ask anything about school data...")

        if user_query:
            # show immediately in UI
            st.session_state.chat_history.append({"role": "user", "content": user_query})

            with st.chat_message("user"):
                st.markdown(user_query)

            with st.chat_message("assistant"):
                with st.spinner("Gemini soch raha hai..."):
                    try:
                        response = requests.post(
                            "http://127.0.0.1:8000/api/ai-db-query/",
                            json={"query": user_query}
                        )

                        if response.status_code == 200:
                            res = response.json()

                            answer = res.get("answer", "No answer found.")
                            sql_q  = res.get("sql", "")
                            table  = res.get("result", [])

                            # assistant reply text
                            st.markdown(f"**💡 Answer**\n\n{answer}")

                            # show sql (collapsible)
                            if sql_q:
                                with st.expander("See Generated SQL"):
                                    st.code(sql_q, language="sql")

                            # show data table if exists
                            if table:
                                df = pd.DataFrame(table)
                                st.dataframe(df)

                            # save assistant message in chat
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": answer
                            })

                        else:
                            st.error(f"Backend Error: {response.text}")

                    except Exception as e:
                        st.error(f"Connection Error: {e}")


    elif menu == "Accounts":  

        
        st.title("💰 Accounts Manager")
        tab1, tab2, tab3 = st.tabs(["💵 Fees Collection", "📉 Expense Tracker", "📊 Summary"])

        with tab1:
            s_id = st.text_input("Student ID Enter Karein", placeholder="Example: 100234567", key="fee_scan")

            if s_id:
                try:
                    # Student details fetch karna
                    res = requests.get(f"http://127.0.0.1:8000/api/get-fee/{s_id.strip()}/")
                    
                    if res.status_code == 200:
                        data = res.json()
                        st.success(f"📌 **Student:** {data['name']} | **Class:** {data['class']}")
                        
                        fixed_fee = float(data['monthly_fee'])

                        with st.form("fee_form", clear_on_submit=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                month = st.selectbox("Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
                                year = st.number_input("Year", value=2026)
                            with col2:
                                st.write(f"Standard Fee: **₹{fixed_fee}**")
                                amount_paid = st.number_input("Amount Paid (₹)", min_value=0.0, step=100.0)
                            
                            # Real-time due calculation (Display only)
                            current_due = max(0.0, fixed_fee - amount_paid)
                            st.warning(f"Estimated Balance: ₹{current_due}")

                            if st.form_submit_button("Submit Payment"):
                                payload = {
                                    "student_id": s_id,
                                    "amount_paid": amount_paid,
                                    "month": month,
                                    "year": year,
                                    "fixed_fee":fixed_fee
                                }
                                save_res = requests.post("http://127.0.0.1:8000/api/save-fee/", json=payload)
                                
                                if save_res.status_code == 200:
                                    st.balloons()
                                    result = save_res.json()
                                    st.success(f"Success! Due Amount: ₹{result['due']}")
                                else:
                                    st.error("Payment failed. Please check server logs.")
                    else:
                        st.error("Student not found!")
                except Exception as e:
                    st.error("Connection Error: Backend server offline.")

        with tab2:
            st.info("Expense Tracker coming soon...")
        with tab3:  
            st.info("Summary Dashboard coming soon...")



    elif menu == "Examination":
        st.title("📝 Examination Management")
        tab1, tab2 = st.tabs(["🆕 Create Exam", "✍️ Fill Marks"])
        API_BASE = "http://127.0.0.1:8000/api"

        with tab1:
            st.subheader("Create Exam Schedule")
            
            # Basic Info
            col1, col2 = st.columns([1, 1])
            with col1:
                exam_name = st.text_input("Exam Name", placeholder="e.g. Unit Test 1")
            with col2:
                try:
                    class_res = requests.get(f"{API_BASE}/classes/")
                    unique_classes = sorted(list(set([c['name'] for c in class_res.json()])))
                    selected_class = st.selectbox("Select Class", unique_classes)
                except:
                    st.error("Backend offline hai")
                    selected_class = None

            if selected_class and exam_name:
                st.markdown(f"#### 📚 Subjects for {selected_class}")
                st.caption("Har subject ki details niche bharein:")
                
                # Subjects fetch (Dummy list if API fails)
                try:
                    sub_res = requests.get(f"{API_BASE}/subjects/?class_name={selected_class}")
                    subjects = [s['name'] for s in sub_res.json()]
                except:
                    subjects = ["Mathematics", "Science", "English", "Hindi"]

                exam_data_list = []

                # --- Mobile Friendly Card Layout ---
                for sub in subjects:
                    # Har subject ke liye ek clean 'Expander' ya 'Container'
                    with st.container(border=True):
                        st.markdown(f"**📖 {sub}**") # Subject Name Header
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            ex_date = st.date_input(f"Date", key=f"date_{sub}")
                        with c2:
                            ex_time = st.time_input(f"Time", key=f"time_{sub}")
                        
                        c3, c4 = st.columns([1, 2])
                        with c3:
                            t_marks = st.number_input(f"Total Marks", min_value=1, value=100, key=f"marks_{sub}")
                        with c4:
                            desc = st.text_input(f"Description / Syllabus", placeholder="e.g. Chapter 1-3", key=f"desc_{sub}")

                        exam_data_list.append({
                            "subject": sub,
                            "date": str(ex_date),
                            "time": str(ex_time),
                            "total_marks": t_marks,
                            "description": desc
                        })

                st.markdown("---")
                if st.button("🚀 Create Exam & Schedule", use_container_width=True, type="primary"):
                    payload = {
                        "exam_name": exam_name,
                        "class_name": selected_class,
                        "schedule": exam_data_list
                    }
                    # Backend call
                    res = requests.post(f"{API_BASE}/exams/create-bulk/", json=payload)
                    if res.status_code == 201:
                        st.success(f"✅ Exam Schedule for {exam_name} created!")
                    else:
                        st.error("Kuch galti hui hai!")

        # ---------------- TAB 2: FILL MARKS ----------------
        with tab2:
            st.subheader("✍️ Enter Student Marks")

            # 1. Select Exam (Backend se fetch karke)
            try:
                exam_res = requests.get(f"{API_BASE}/exams/")
                exams_list = exam_res.json()
                exam_map = {f"{e['exam_name']} ({e['class_name']})": e for e in exams_list}
                selected_exam_label = st.selectbox("Select Exam", [""] + list(exam_map.keys()))
            except:
                st.error("Exams load nahi ho paye")
                selected_exam_label = ""

            if selected_exam_label:
                target_exam = exam_map[selected_exam_label]
                
                col_a, col_b = st.columns(2)
                
                # 2. Select Specific Section (Class 1-A, 1-B etc.)
                with col_a:
                    class_res = requests.get(f"{API_BASE}/classes/")
                    # Filter classes jo selected exam ki class se match karti hon
                    all_sections = [f"{c['name']} - {c['section']}" for c in class_res.json() 
                                    if c['name'] == target_exam['class_name']]
                    selected_section = st.selectbox("Select Section", all_sections)

                # 3. Select Subject (Jo us exam schedule mein hain)
                with col_b:
                    subjects_in_exam = [s['subject'] for s in target_exam['schedule']]
                    selected_subject = st.selectbox("Select Subject", subjects_in_exam)

                st.divider()

                # 4. Fetch Students of that Section
                if selected_section:
                    # API Call: Student list based on class and section
                    # Example URL: /api/students/?class_section=Class 1 - A
                    std_res = requests.get(f"{API_BASE}/students/", params={"section_full": selected_section})
                    
                    if std_res.status_code == 200:
                        students = std_res.json()
                        
                        if not students:
                            st.warning("Is section mein koi students nahi mile.")
                        else:
                            st.write(f"### 📋 Marks Entry: {selected_subject}")
                            st.caption(f"Max Marks: {next(s['total_marks'] for s in target_exam['schedule'] if s['subject'] == selected_subject)}")
                            
                            # Marks Data Collector
                            marks_payload = []

                            # Mobile-friendly list entry
                            for std in students:
                                with st.container(border=True):
                                    r1, r2 = st.columns([2, 1])
                                    with r1:
                                        st.write(f"**{std['name']}**")
                                        st.caption(f"Roll No: {std.get('roll_number', 'N/A')}")
                                    with r2:
                                        # Marks input field
                                        m_score = st.number_input(f"Marks", min_value=0.0, max_value=200.0, key=f"m_{std['id']}")
                                        
                                    marks_payload.append({
                                        "student_id": std['id'],
                                        "marks": m_score
                                    })

                            st.divider()
                            if st.button("💾 Save All Marks", use_container_width=True, type="primary"):
                                final_data = {
                                    "exam_id": target_exam['id'],
                                    "subject": selected_subject,
                                    "section": selected_section,
                                    "marks_list": marks_payload
                                }
                                # Send to backend
                                post_res = requests.post(f"{API_BASE}/marks/save-bulk/", json=final_data)
                                if post_res.status_code == 200:
                                    st.success("Marks saved successfully! 🎉")
                                    st.balloons()
                                else:
                                    st.error("Save karne mein dikkat aayi.")


if not st.session_state["is_logged_in"]:
    show_login()
else:
    show_main_app()
