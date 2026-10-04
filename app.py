import os
from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import mysql.connector

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from functools import wraps


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


app = Flask(__name__)

app.secret_key = os.getenv(
    "LIFELINK_SECRET_KEY"
)


# =========================================================
# DATABASE
# =========================================================

DB_PASSWORD = os.getenv(
    "LIFELINK_DB_PASSWORD"
)


def get_db_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=DB_PASSWORD,
        database="lifelink"
    )


# =========================================================
# LOGIN PROTECTION
# =========================================================

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login first.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        return f(*args, **kwargs)

    return decorated_function


def donor_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login first.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        if session.get("role") != "donor":

            flash(
                "Donor access required.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        return f(*args, **kwargs)

    return decorated_function


def hospital_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "hospital_id" not in session:

            flash(
                "Please login as hospital.",
                "error"
            )

            return redirect(
                url_for("hospital_login")
            )

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if (
            "user_id" not in session
            or session.get("role") != "admin"
        ):

            flash(
                "Admin access required.",
                "error"
            )

            return redirect(
                url_for("admin_login")
            )

        return f(*args, **kwargs)

    return decorated_function


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# DONOR REGISTRATION
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        blood_group = request.form.get(
            "blood_group",
            ""
        ).strip()

        city = request.form.get(
            "city",
            ""
        ).strip()

        if not all([
            name,
            email,
            phone,
            password,
            blood_group,
            city
        ]):

            flash(
                "Please fill all fields.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            existing = cursor.fetchone()

            if existing:

                flash(
                    "Email already registered.",
                    "error"
                )

                return redirect(
                    url_for("register")
                )

            hashed_password = generate_password_hash(
                password
            )

            cursor.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    phone,
                    password,
                    role,
                    blood_group,
                    city,
                    is_available
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    'donor',
                    %s,
                    %s,
                    TRUE
                )
                """,
                (
                    name,
                    email,
                    phone,
                    hashed_password,
                    blood_group,
                    city
                )
            )

            conn.commit()

            flash(
                "Registration successful. Please login.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        finally:

            cursor.close()
            conn.close()

    return render_template(
        "register.html"
    )


# =========================================================
# PATIENT REGISTRATION
# =========================================================

@app.route(
    "/patient-register",
    methods=["GET", "POST"]
)
def patient_register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        city = request.form.get(
            "city",
            ""
        ).strip()

        if not all([
            name,
            email,
            phone,
            password,
            city
        ]):

            flash(
                "Please fill all fields.",
                "error"
            )

            return redirect(
                url_for("patient_register")
            )

        hashed_password = generate_password_hash(
            password
        )

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            existing = cursor.fetchone()

            if existing:

                flash(
                    "Email already registered.",
                    "error"
                )

                return redirect(
                    url_for("patient_register")
                )

            cursor.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    phone,
                    password,
                    role,
                    city,
                    is_available
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    'patient',
                    %s,
                    FALSE
                )
                """,
                (
                    name,
                    email,
                    phone,
                    hashed_password,
                    city
                )
            )

            conn.commit()

            flash(
                "Patient registration successful. Please login.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        except mysql.connector.Error as e:

            conn.rollback()

            print(
                "Patient Registration Error:",
                e
            )

            flash(
                "Patient registration failed.",
                "error"
            )

        finally:

            cursor.close()
            conn.close()

    return render_template(
        "patient_register.html"
    )


# =========================================================
# USER LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        conn = get_db_connection()
        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            user = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if user:

            try:

                password_valid = check_password_hash(
                    user["password"],
                    password
                )

            except Exception:

                password_valid = False

            if password_valid:

                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                session["name"] = user["name"]
                session["email"] = user["email"]
                session["role"] = user["role"]

                if user["role"] == "donor":

                    return redirect(
                        url_for("donor_dashboard")
                    )

                if user["role"] == "patient":

                    return redirect(
                        url_for("home")
                    )

                if user["role"] == "admin":

                    return redirect(
                        url_for("admin_dashboard")
                    )

        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template(
        "login.html"
    )


# =========================================================
# DONOR DASHBOARD
# =========================================================

@app.route("/donor-dashboard")
@donor_required
def donor_dashboard():

    donor_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                phone,
                blood_group,
                city,
                is_available
            FROM users
            WHERE id = %s
            """,
            (donor_id,)
        )

        donor = cursor.fetchone()

        if not donor:

            session.clear()

            flash(
                "Donor account not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        cursor.execute(
            """
            SELECT
                br.id,
                br.blood_group,
                br.units_required,
                br.urgency,
                br.patient_name,
                br.contact_phone,
                br.city,
                br.status,
                br.created_at,

                dr.id AS response_id,
                dr.response,
                dr.responded_at

            FROM donor_responses dr

            INNER JOIN blood_requests br
                ON dr.request_id = br.id

            WHERE dr.donor_id = %s

            ORDER BY
                CASE
                    WHEN br.urgency = 'critical'
                        THEN 1
                    WHEN br.urgency = 'urgent'
                        THEN 2
                    ELSE 3
                END,
                br.created_at DESC
            """,
            (donor_id,)
        )

        requests = cursor.fetchall()

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM donor_responses dr

            INNER JOIN blood_requests br
                ON dr.request_id = br.id

            WHERE dr.donor_id = %s
              AND dr.response = 'pending'
              AND br.status IN ('pending', 'matched')
            """,
            (donor_id,)
        )

        notification_count = cursor.fetchone()[
            "count"
        ]

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM donor_responses dr

            INNER JOIN blood_requests br
                ON dr.request_id = br.id

            WHERE dr.donor_id = %s
              AND dr.response = 'pending'
              AND br.urgency = 'critical'
              AND br.status IN ('pending', 'matched')
            """,
            (donor_id,)
        )

        critical_count = cursor.fetchone()[
            "count"
        ]

        return render_template(
            "donor_dashboard.html",
            donor=donor,
            requests=requests,
            notification_count=notification_count,
            critical_count=critical_count
        )

    finally:

        cursor.close()
        conn.close()


# =========================================================
# DONOR AVAILABILITY
# =========================================================

@app.route(
    "/toggle-availability",
    methods=["POST"]
)
@donor_required
def toggle_availability():

    donor_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT is_available
            FROM users
            WHERE id = %s
            """,
            (donor_id,)
        )

        donor = cursor.fetchone()

        if not donor:

            flash(
                "Donor not found.",
                "error"
            )

            return redirect(
                url_for("donor_dashboard")
            )

        new_status = not bool(
            donor["is_available"]
        )

        cursor.execute(
            """
            UPDATE users
            SET is_available = %s
            WHERE id = %s
            """,
            (
                new_status,
                donor_id
            )
        )

        conn.commit()

        if new_status:

            flash(
                "You are now available for blood requests.",
                "success"
            )

        else:

            flash(
                "You are now unavailable for new requests.",
                "success"
            )

        return redirect(
            url_for("donor_dashboard")
        )

    finally:

        cursor.close()
        conn.close()


# =========================================================
# DONOR ACCEPT / DECLINE
# =========================================================

@app.route(
    "/respond-request/<int:response_id>/<action>",
    methods=["POST"]
)
@donor_required
def respond_request(
    response_id,
    action
):

    if action not in [
        "accepted",
        "declined"
    ]:

        flash(
            "Invalid response.",
            "error"
        )

        return redirect(
            url_for("donor_dashboard")
        )

    donor_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                dr.id,
                dr.request_id,
                dr.response,
                br.status

            FROM donor_responses dr

            INNER JOIN blood_requests br
                ON dr.request_id = br.id

            WHERE dr.id = %s
              AND dr.donor_id = %s
            """,
            (
                response_id,
                donor_id
            )
        )

        response = cursor.fetchone()

        if not response:

            flash(
                "Request response not found.",
                "error"
            )

            return redirect(
                url_for("donor_dashboard")
            )

        if response["response"] != "pending":

            flash(
                "You have already responded to this request.",
                "error"
            )

            return redirect(
                url_for("donor_dashboard")
            )

        cursor.execute(
            """
            UPDATE donor_responses

            SET
                response = %s,
                responded_at = NOW()

            WHERE id = %s
              AND donor_id = %s
            """,
            (
                action,
                response_id,
                donor_id
            )
        )

        conn.commit()

        if action == "accepted":

            flash(
                "You accepted the blood request. "
                "Waiting for hospital approval.",
                "success"
            )

        else:

            flash(
                "You declined the blood request.",
                "success"
            )

        return redirect(
            url_for("donor_dashboard")
        )

    finally:

        cursor.close()
        conn.close()


# =========================================================
# FIND BLOOD
# =========================================================

@app.route(
    "/find-blood",
    methods=["GET", "POST"]
)
def find_blood():

    donors = []

    if request.method == "POST":

        blood_group = request.form.get(
            "blood_group",
            ""
        ).strip()

        city = request.form.get(
            "city",
            ""
        ).strip()

        conn = get_db_connection()
        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    blood_group,
                    city,
                    phone

                FROM users

                WHERE role = 'donor'
                  AND blood_group = %s
                  AND city = %s
                  AND is_available = TRUE

                ORDER BY name
                """,
                (
                    blood_group,
                    city
                )
            )

            donors = cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    return render_template(
        "find_blood.html",
        donors=donors
    )


# =========================================================
# REQUEST BLOOD
# =========================================================

@app.route(
    "/request-blood",
    methods=["GET", "POST"]
)
@login_required
def request_blood():

    conn = get_db_connection()
    cursor = conn.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                id,
                name,
                city,
                address

            FROM hospitals

            WHERE is_verified = TRUE

            ORDER BY name
            """
        )

        hospitals = cursor.fetchall()

    finally:

        cursor.close()
        conn.close()

    if request.method == "POST":

        patient_name = request.form.get(
            "patient_name",
            ""
        ).strip()

        blood_group = request.form.get(
            "blood_group",
            ""
        ).strip()

        units_required = request.form.get(
            "units_required",
            ""
        ).strip()

        hospital_id = request.form.get(
            "hospital_id",
            ""
        ).strip()

        city = request.form.get(
            "city",
            ""
        ).strip()

        urgency = request.form.get(
            "urgency",
            "urgent"
        ).strip()

        contact_phone = request.form.get(
            "contact_phone",
            ""
        ).strip()

        if not all([
            patient_name,
            blood_group,
            units_required,
            hospital_id,
            city,
            urgency,
            contact_phone
        ]):

            flash(
                "Please fill all required fields.",
                "error"
            )

            return redirect(
                url_for("request_blood")
            )

        try:

            units_required = int(
                units_required
            )

        except ValueError:

            flash(
                "Units required must be a number.",
                "error"
            )

            return redirect(
                url_for("request_blood")
            )

        if units_required <= 0:

            flash(
                "Units required must be greater than 0.",
                "error"
            )

            return redirect(
                url_for("request_blood")
            )

        if urgency not in [
            "normal",
            "urgent",
            "critical"
        ]:

            flash(
                "Invalid urgency.",
                "error"
            )

            return redirect(
                url_for("request_blood")
            )

        conn = get_db_connection()
        cursor = conn.cursor(
            dictionary=True
        )

        try:

            # -------------------------------------------------
            # VERIFY SELECTED HOSPITAL
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    is_verified

                FROM hospitals

                WHERE id = %s
                  AND is_verified = TRUE
                """,
                (hospital_id,)
            )

            hospital = cursor.fetchone()

            if not hospital:

                flash(
                    "Selected hospital is not verified.",
                    "error"
                )

                return redirect(
                    url_for("request_blood")
                )

            # -------------------------------------------------
            # CREATE BLOOD REQUEST
            # -------------------------------------------------

            cursor.execute(
                """
                INSERT INTO blood_requests
                (
                    requester_id,
                    hospital_id,
                    blood_group,
                    units_required,
                    urgency,
                    patient_name,
                    contact_phone,
                    city
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    session["user_id"],
                    hospital_id,
                    blood_group,
                    units_required,
                    urgency,
                    patient_name,
                    contact_phone,
                    city
                )
            )

            request_id = cursor.lastrowid

            # -------------------------------------------------
            # FIND MATCHING DONORS
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT
                    id

                FROM users

                WHERE role = 'donor'
                  AND blood_group = %s
                  AND city = %s
                  AND is_available = TRUE
                """,
                (
                    blood_group,
                    city
                )
            )

            matching_donors = cursor.fetchall()

            notified_count = 0

            # -------------------------------------------------
            # CREATE DONOR RESPONSES
            # -------------------------------------------------

            for donor in matching_donors:

                cursor.execute(
                    """
                    INSERT INTO donor_responses
                    (
                        request_id,
                        donor_id,
                        response
                    )

                    VALUES
                    (
                        %s,
                        %s,
                        'pending'
                    )
                    """,
                    (
                        request_id,
                        donor["id"]
                    )
                )

                notified_count += 1

            conn.commit()

            flash(
                f"Blood request #{request_id} created successfully. "
                f"{notified_count} matching donor(s) notified.",
                "success"
            )

            return redirect(
                url_for(
                    "request_status",
                    request_id=request_id
                )
            )

        finally:

            cursor.close()
            conn.close()

    return render_template(
        "request_blood.html",
        hospitals=hospitals
    )


# =========================================================
# REQUEST STATUS
# =========================================================

@app.route(
    "/request-status/<int:request_id>"
)
def request_status(request_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()
    cursor = conn.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                br.*,
                h.name AS hospital_name,
                h.is_verified AS hospital_verified

            FROM blood_requests br

            LEFT JOIN hospitals h
                ON br.hospital_id = h.id

            WHERE br.id = %s
            """,
            (request_id,)
        )

        blood_request = cursor.fetchone()

        if not blood_request:

            return (
                "Blood request not found",
                404
            )

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total,

                SUM(
                    CASE
                        WHEN response = 'accepted'
                        THEN 1
                        ELSE 0
                    END
                ) AS accepted,

                SUM(
                    CASE
                        WHEN response = 'pending'
                        THEN 1
                        ELSE 0
                    END
                ) AS pending,

                SUM(
                    CASE
                        WHEN response = 'declined'
                        THEN 1
                        ELSE 0
                    END
                ) AS declined

            FROM donor_responses

            WHERE request_id = %s
            """,
            (request_id,)
        )

        stats = cursor.fetchone()

        total = stats["total"] or 0
        accepted = stats["accepted"] or 0
        pending = stats["pending"] or 0
        declined = stats["declined"] or 0

        return render_template(
            "request_status.html",
            blood_request=blood_request,
            total=total,
            accepted=accepted,
            pending=pending,
            declined=declined
        )

    finally:

        cursor.close()
        conn.close()


# =========================================================
# MY REQUESTS
# =========================================================

@app.route("/my-requests")
@login_required
def my_requests():

    conn = get_db_connection()
    cursor = conn.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                br.*,
                h.name AS hospital_name,
                h.is_verified AS hospital_verified

            FROM blood_requests br

            LEFT JOIN hospitals h
                ON br.hospital_id = h.id

            WHERE br.requester_id = %s

            ORDER BY br.created_at DESC
            """,
            (
                session["user_id"],
            )
        )

        requests = cursor.fetchall()

        return render_template(
            "my_requests.html",
            requests=requests
        )

    finally:

        cursor.close()
        conn.close()


# =========================================================
# HOSPITAL REGISTRATION
# =========================================================

@app.route(
    "/hospital-register",
    methods=["GET", "POST"]
)
def hospital_register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        address = request.form.get(
            "address",
            ""
        ).strip()

        city = request.form.get(
            "city",
            ""
        ).strip()

        if not all([
            name,
            email,
            phone,
            password,
            address,
            city
        ]):

            flash(
                "Please fill all fields.",
                "error"
            )

            return redirect(
                url_for("hospital_register")
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT id
                FROM hospitals
                WHERE email = %s
                """,
                (email,)
            )

            existing = cursor.fetchone()

            if existing:

                flash(
                    "Hospital email already registered.",
                    "error"
                )

                return redirect(
                    url_for("hospital_register")
                )

            hashed_password = generate_password_hash(
                password
            )

            cursor.execute(
                """
                INSERT INTO hospitals
                (
                    name,
                    email,
                    password,
                    phone,
                    address,
                    city,
                    is_verified
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    FALSE
                )
                """,
                (
                    name,
                    email,
                    hashed_password,
                    phone,
                    address,
                    city
                )
            )

            conn.commit()

            flash(
                "Hospital registered. "
                "Wait for admin verification.",
                "success"
            )

            return redirect(
                url_for("hospital_login")
            )

        finally:

            cursor.close()
            conn.close()

    return render_template(
        "hospital_register.html"
    )


# =========================================================
# HOSPITAL LOGIN
# =========================================================

@app.route(
    "/hospital-login",
    methods=["GET", "POST"]
)
def hospital_login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        conn = get_db_connection()
        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM hospitals
                WHERE email = %s
                """,
                (email,)
            )

            hospital = cursor.fetchone()

            if hospital:

                stored_password = hospital.get(
                    "password"
                )

                if stored_password:

                    try:

                        valid = check_password_hash(
                            stored_password,
                            password
                        )

                    except Exception:

                        valid = False

                    if valid:

                        session["hospital_id"] = hospital["id"]
                        session["hospital_name"] = hospital["name"]

                        return redirect(
                            url_for("hospital_dashboard")
                        )

            flash(
                "Invalid hospital email or password.",
                "error"
            )

        finally:

            cursor.close()
            conn.close()

    return render_template(
        "hospital_login.html"
    )


# =========================================================
# HOSPITAL DASHBOARD
# =========================================================

@app.route("/hospital-dashboard")
@hospital_required
def hospital_dashboard():

    hospital_id = session["hospital_id"]

    conn = get_db_connection()
    cursor = conn.cursor(
        dictionary=True
    )

    try:

        # -------------------------------------------------
        # HOSPITAL DETAILS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM hospitals
            WHERE id = %s
            """,
            (hospital_id,)
        )

        hospital = cursor.fetchone()

        if not hospital:

            session.pop(
                "hospital_id",
                None
            )

            session.pop(
                "hospital_name",
                None
            )

            flash(
                "Hospital account not found.",
                "error"
            )

            return redirect(
                url_for("hospital_login")
            )

        # -------------------------------------------------
        # REQUESTS + DONOR
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                br.*,

                u.name AS requester_name,

                h.name AS hospital_name,

                h.is_verified AS hospital_verified,

                (
                    SELECT d.name

                    FROM donor_responses dr

                    INNER JOIN users d
                        ON dr.donor_id = d.id

                    WHERE dr.request_id = br.id
                      AND dr.response = 'accepted'

                    ORDER BY dr.responded_at ASC

                    LIMIT 1

                ) AS donor_name,

                (
                    SELECT d.phone

                    FROM donor_responses dr

                    INNER JOIN users d
                        ON dr.donor_id = d.id

                    WHERE dr.request_id = br.id
                      AND dr.response = 'accepted'

                    ORDER BY dr.responded_at ASC

                    LIMIT 1

                ) AS donor_phone,

                (
                    SELECT d.blood_group

                    FROM donor_responses dr

                    INNER JOIN users d
                        ON dr.donor_id = d.id

                    WHERE dr.request_id = br.id
                      AND dr.response = 'accepted'

                    ORDER BY dr.responded_at ASC

                    LIMIT 1

                ) AS donor_blood_group

            FROM blood_requests br

            INNER JOIN users u
                ON br.requester_id = u.id

            LEFT JOIN hospitals h
                ON br.hospital_id = h.id

            WHERE br.hospital_id = %s

            ORDER BY br.created_at DESC
            """,
            (hospital_id,)
        )

        requests = cursor.fetchall()

        # -------------------------------------------------
        # STATISTICS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM blood_requests

            WHERE hospital_id = %s
            """,
            (hospital_id,)
        )

        total_requests = cursor.fetchone()[
            "total"
        ]

        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM blood_requests

            WHERE hospital_id = %s
              AND status = 'pending'
            """,
            (hospital_id,)
        )

        pending_requests = cursor.fetchone()[
            "total"
        ]

        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM blood_requests

            WHERE hospital_id = %s
              AND status = 'matched'
            """,
            (hospital_id,)
        )

        matched_requests = cursor.fetchone()[
            "total"
        ]

        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM blood_requests

            WHERE hospital_id = %s
              AND status = 'fulfilled'
            """,
            (hospital_id,)
        )

        fulfilled_requests = cursor.fetchone()[
            "total"
        ]

        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM blood_requests

            WHERE hospital_id = %s
              AND status = 'cancelled'
            """,
            (hospital_id,)
        )

        cancelled_requests = cursor.fetchone()[
            "total"
        ]

        return render_template(
            "hospital_dashboard.html",
            hospital=hospital,
            requests=requests,
            total_requests=total_requests,
            pending_requests=pending_requests,
            matched_requests=matched_requests,
            fulfilled_requests=fulfilled_requests,
            cancelled_requests=cancelled_requests
        )

    finally:

        cursor.close()
        conn.close()


# =========================================================
# HOSPITAL APPROVE / MATCH
# =========================================================

@app.route(
    "/hospital/request/<int:request_id>/approve",
    methods=["POST"]
)
@hospital_required
def hospital_approve_request(
    request_id
):

    hospital_id = session["hospital_id"]

    conn = get_db_connection()
    cursor = conn.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                id,
                status

            FROM blood_requests

            WHERE id = %s
              AND hospital_id = %s
            """,
            (
                request_id,
                hospital_id
            )
        )

        blood_request = cursor.fetchone()

        if not blood_request:

            flash(
                "Request not found.",
                "error"
            )

            return redirect(
                url_for("hospital_dashboard")
            )

        if blood_request["status"] != "pending":

            flash(
                "Only pending requests can be approved.",
                "error"
            )

            return redirect(
                url_for("hospital_dashboard")
            )

        cursor.execute(
            """
            SELECT COUNT(*) AS accepted_count

            FROM donor_responses

            WHERE request_id = %s
              AND response = 'accepted'
            """,
            (request_id,)
        )

        accepted_count = cursor.fetchone()[
            "accepted_count"
        ]

        if accepted_count == 0:

            flash(
                "No donor has accepted this request yet.",
                "error"
            )

            return redirect(
                url_for("hospital_dashboard")
            )

        cursor.execute(
            """
            UPDATE blood_requests

            SET status = 'matched'

            WHERE id = %s
              AND hospital_id = %s
              AND status = 'pending'
            """,
            (
                request_id,
                hospital_id
            )
        )

        conn.commit()

        flash(
            "Request approved and matched successfully.",
            "success"
        )

        return redirect(
            url_for("hospital_dashboard")
        )

    finally:

        cursor.close()
        conn.close()


# =========================================================
# HOSPITAL REJECT / CANCEL
# =========================================================

@app.route(
    "/hospital/request/<int:request_id>/reject",
    methods=["POST"]
)
@hospital_required
def hospital_reject_request(
    request_id
):

    hospital_id = session["hospital_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            UPDATE blood_requests

            SET status = 'cancelled'

            WHERE id = %s
              AND hospital_id = %s
              AND status IN ('pending', 'matched')
            """,
            (
                request_id,
                hospital_id
            )
        )

        conn.commit()

        flash(
            "Blood request cancelled.",
            "success"
        )

        return redirect(
            url_for("hospital_dashboard")
        )

    finally:

        cursor.close()
        conn.close()


# =========================================================
# HOSPITAL FULFILL
# =========================================================

@app.route(
    "/hospital/request/<int:request_id>/fulfill",
    methods=["POST"]
)
@hospital_required
def hospital_fulfill_request(
    request_id
):

    hospital_id = session["hospital_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            UPDATE blood_requests

            SET status = 'fulfilled'

            WHERE id = %s
              AND hospital_id = %s
              AND status = 'matched'
            """,
            (
                request_id,
                hospital_id
            )
        )

        conn.commit()

        flash(
            "Blood request marked as fulfilled.",
            "success"
        )

        return redirect(
            url_for("hospital_dashboard")
        )

    finally:

        cursor.close()
        conn.close()


# =========================================================
# HOSPITAL LOGOUT
# =========================================================

@app.route("/hospital-logout")
def hospital_logout():

    session.pop(
        "hospital_id",
        None
    )

    session.pop(
        "hospital_name",
        None
    )

    flash(
        "Hospital logged out successfully.",
        "success"
    )

    return redirect(
        url_for("hospital_login")
    )


# =========================================================
# USER LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("home")
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route(
    "/admin-login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not email or not password:

            flash(
                "Please enter admin email and password.",
                "error"
            )

            return render_template(
                "admin_login.html"
            )

        conn = get_db_connection()
        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    email,
                    password,
                    role

                FROM users

                WHERE email = %s
                  AND role = 'admin'

                LIMIT 1
                """,
                (email,)
            )

            admin = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if admin:

            try:

                password_valid = check_password_hash(
                    admin["password"],
                    password
                )

            except Exception as e:

                print(
                    "Admin password verification error:",
                    e
                )

                password_valid = False

            if password_valid:

                session["user_id"] = admin["id"]
                session["user_name"] = admin["name"]
                session["name"] = admin["name"]
                session["email"] = admin["email"]
                session["role"] = "admin"

                return redirect(
                    url_for("admin_dashboard")
                )

        flash(
            "Invalid admin email or password.",
            "error"
        )

    return render_template(
        "admin_login.html"
    )


# =========================================================
# ADMIN VERIFY HOSPITAL
# =========================================================

@app.route(
    "/admin/hospital/<int:hospital_id>/verify",
    methods=["POST"]
)
@admin_required
def admin_verify_hospital(
    hospital_id
):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            UPDATE hospitals

            SET is_verified = TRUE

            WHERE id = %s
            """,
            (hospital_id,)
        )

        conn.commit()

        flash(
            "Hospital verified successfully.",
            "success"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    finally:

        cursor.close()
        conn.close()


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin-dashboard")
@admin_required
def admin_dashboard():

    conn = get_db_connection()
    cursor = conn.cursor(
        dictionary=True
    )

    try:

        # -------------------------------------------------
        # USERS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM users
            """
        )

        total_users = cursor.fetchone()[
            "total"
        ]

        # -------------------------------------------------
        # DONORS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM users

            WHERE role = 'donor'
            """
        )

        total_donors = cursor.fetchone()[
            "total"
        ]

        # -------------------------------------------------
        # HOSPITALS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM hospitals
            """
        )

        total_hospitals = cursor.fetchone()[
            "total"
        ]

        # -------------------------------------------------
        # REQUESTS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM blood_requests
            """
        )

        total_requests = cursor.fetchone()[
            "total"
        ]

        # -------------------------------------------------
        # HOSPITAL LIST
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                phone,
                address,
                city,
                is_verified,
                created_at

            FROM hospitals

            ORDER BY created_at DESC
            """
        )

        hospitals = cursor.fetchall()

        # -------------------------------------------------
        # DONOR LIST
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                phone,
                blood_group,
                city,
                is_available,
                created_at

            FROM users

            WHERE role = 'donor'

            ORDER BY created_at DESC
            """
        )

        donors = cursor.fetchall()

        # -------------------------------------------------
        # BLOOD REQUEST LIST
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                br.id,
                br.patient_name,
                br.blood_group,
                br.units_required,
                br.urgency,
                br.city,
                br.contact_phone,
                br.status,
                br.created_at,

                u.name AS requester_name,

                h.name AS hospital_name,

                h.is_verified AS hospital_verified

            FROM blood_requests br

            INNER JOIN users u
                ON br.requester_id = u.id

            LEFT JOIN hospitals h
                ON br.hospital_id = h.id

            ORDER BY br.created_at DESC
            """
        )

        blood_requests = cursor.fetchall()

        # -------------------------------------------------
        # REQUEST STATISTICS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM blood_requests

            WHERE status = 'pending'
            """
        )

        pending_requests = cursor.fetchone()[
            "total"
        ]

        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM blood_requests

            WHERE status = 'matched'
            """
        )

        matched_requests = cursor.fetchone()[
            "total"
        ]

        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM blood_requests

            WHERE status = 'fulfilled'
            """
        )

        fulfilled_requests = cursor.fetchone()[
            "total"
        ]

        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM blood_requests

            WHERE status = 'cancelled'
            """
        )

        cancelled_requests = cursor.fetchone()[
            "total"
        ]

        # -------------------------------------------------
        # HOSPITAL VERIFICATION STATISTICS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM hospitals

            WHERE is_verified = TRUE
            """
        )

        verified_hospitals = cursor.fetchone()[
            "total"
        ]

        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM hospitals

            WHERE is_verified = FALSE
            """
        )

        pending_hospitals = cursor.fetchone()[
            "total"
        ]

        return render_template(
            "admin_dashboard.html",

            total_users=total_users,
            total_donors=total_donors,
            total_hospitals=total_hospitals,
            total_requests=total_requests,

            hospitals=hospitals,
            donors=donors,
            blood_requests=blood_requests,

            pending_requests=pending_requests,
            matched_requests=matched_requests,
            fulfilled_requests=fulfilled_requests,
            cancelled_requests=cancelled_requests,

            verified_hospitals=verified_hospitals,
            pending_hospitals=pending_hospitals
        )

    finally:

        cursor.close()
        conn.close()


# =========================================================
# ADMIN REQUEST DETAILS
# =========================================================

@app.route(
    "/admin/request/<int:request_id>"
)
@admin_required
def admin_request_details(
    request_id
):

    conn = get_db_connection()
    cursor = conn.cursor(
        dictionary=True
    )

    try:

        # -------------------------------------------------
        # REQUEST DETAILS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                br.*,

                u.name AS requester_name,
                u.email AS requester_email,
                u.phone AS requester_phone,

                h.name AS hospital_name,
                h.email AS hospital_email,
                h.phone AS hospital_phone,
                h.address AS hospital_address,
                h.city AS hospital_city,

                /*
                 IMPORTANT:
                 Both aliases are included so existing
                 templates can use either variable.
                */

                h.is_verified AS hospital_verified,
                h.is_verified AS is_verified

            FROM blood_requests br

            INNER JOIN users u
                ON br.requester_id = u.id

            LEFT JOIN hospitals h
                ON br.hospital_id = h.id

            WHERE br.id = %s
            """,
            (request_id,)
        )

        blood_request = cursor.fetchone()

        if not blood_request:

            flash(
                "Blood request not found.",
                "error"
            )

            return redirect(
                url_for("admin_dashboard")
            )

        # -------------------------------------------------
        # DONOR RESPONSES
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                dr.id,
                dr.response,
                dr.responded_at,
                dr.created_at,

                u.name AS donor_name,
                u.email AS donor_email,
                u.phone AS donor_phone,
                u.blood_group,
                u.city,
                u.is_available

            FROM donor_responses dr

            INNER JOIN users u
                ON dr.donor_id = u.id

            WHERE dr.request_id = %s

            ORDER BY

                CASE
                    WHEN dr.response = 'accepted'
                        THEN 1

                    WHEN dr.response = 'pending'
                        THEN 2

                    ELSE 3
                END,

                dr.created_at DESC
            """,
            (request_id,)
        )

        donor_responses = cursor.fetchall()

        return render_template(
            "admin_request_details.html",

            blood_request=blood_request,

            donor_responses=donor_responses
        )

    finally:

        cursor.close()
        conn.close()


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin-logout")
def admin_logout():

    session.clear()

    flash(
        "Admin logged out successfully.",
        "success"
    )

    return redirect(
        url_for("admin_login")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )