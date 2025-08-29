from flask import Flask, render_template, request, redirect, url_for, g, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecretkey"
DATABASE = "community_connect.db"

# ---------- DB Helpers ----------
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    if not os.path.exists(DATABASE):
        with app.app_context():
            db = get_db()
            with open("schema.sql", "r") as f:
                db.executescript(f.read())
            with open("seed.sql", "r") as f:
                db.executescript(f.read())
            db.commit()

# ---------- Login Required Decorator ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ---------- Auth Routes ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db = get_db()
        user = db.execute("SELECT * FROM Volunteers WHERE Email=?", (request.form["Email"],)).fetchone()
        if user and check_password_hash(user["Password"], request.form["Password"]):
            session["user_id"] = user["VolunteerID"]
            session["email"] = user["Email"]
            flash("Logged in successfully.", "success")
            return redirect(url_for("index"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db = get_db()
        first = request.form.get("FirstName")
        last = request.form.get("LastName")
        email = request.form.get("Email")
        password = request.form.get("Password")
        if not first or not last or not email or not password:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("register"))
        hashed = generate_password_hash(password)
        phone = request.form.get("Phone")
        address = request.form.get("Address")
        dob = request.form.get("DateOfBirth")
        availability = request.form.get("Availability")
        emergency = request.form.get("EmergencyContact")
        profile_photo = None
        if "ProfilePhoto" in request.files:
            file = request.files["ProfilePhoto"]
            if file.filename:
                filename = file.filename
                file.save(os.path.join("static/uploads", filename))
                profile_photo = filename
        try:
            db.execute(
                """INSERT INTO Volunteers 
                (FirstName, LastName, Email, Password, Phone, Address, DateOfBirth, Availability, ProfilePhoto, EmergencyContact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (first, last, email, hashed, phone, address, dob, availability, profile_photo, emergency)
            )
            db.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already exists.", "error")
            return redirect(url_for("register"))
    return render_template("register.html")

# ---------- Main ----------
@app.route("/")
@login_required
def index():
    return render_template("index.html")

# ---------- CRUD Routes ----------

# --- Volunteers ---
@app.route("/volunteers")
@login_required
def list_volunteers():
    db = get_db()
    volunteers = db.execute("SELECT * FROM Volunteers").fetchall()
    return render_template("volunteers.html", volunteers=volunteers)

@app.route("/volunteers/add", methods=["GET", "POST"])
@login_required
def add_volunteer():
    if request.method == "POST":
        db = get_db()
        db.execute(
            """INSERT INTO Volunteers 
            (FirstName, LastName, Email, Phone, Address, DateOfBirth, Availability, ProfilePhoto, EmergencyContact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                request.form["FirstName"],
                request.form["LastName"],
                request.form["Email"],
                request.form.get("Phone"),
                request.form.get("Address"),
                request.form.get("DateOfBirth"),
                request.form.get("Availability"),
                request.form.get("ProfilePhoto"),
                request.form.get("EmergencyContact"),
            ),
        )
        db.commit()
        flash("Volunteer added successfully.", "success")
        return redirect(url_for("list_volunteers"))
    return render_template("add_volunteer.html")

@app.route("/volunteers/<int:id>/edit", methods=["GET", "POST"])
@login_required
def update_volunteer(id):
    db = get_db()
    volunteer = db.execute("SELECT * FROM Volunteers WHERE VolunteerID=?", (id,)).fetchone()
    if request.method == "POST":
        db.execute(
            """UPDATE Volunteers 
               SET FirstName=?, LastName=?, Email=?, Phone=?, Address=?, DateOfBirth=?, Availability=?, ProfilePhoto=?, EmergencyContact=?
               WHERE VolunteerID=?""",
            (
                request.form["FirstName"],
                request.form["LastName"],
                request.form["Email"],
                request.form.get("Phone"),
                request.form.get("Address"),
                request.form.get("DateOfBirth"),
                request.form.get("Availability"),
                request.form.get("ProfilePhoto"),
                request.form.get("EmergencyContact"),
                id
            )
        )
        db.commit()
        flash("Volunteer updated successfully.", "success")
        return redirect(url_for("list_volunteers"))
    return render_template("update_volunteer.html", volunteer=volunteer)

@app.route("/volunteers/<int:id>/delete", methods=["POST"])
@login_required
def delete_volunteer(id):
    db = get_db()
    db.execute("DELETE FROM Volunteers WHERE VolunteerID=?", (id,))
    db.commit()
    flash("Volunteer deleted successfully.", "success")
    return redirect(url_for("list_volunteers"))

# --- Organisations ---
@app.route("/organisations")
@login_required
def list_orgs():
    db = get_db()
    orgs = db.execute("SELECT * FROM Organisations").fetchall()
    return render_template("organisations.html", orgs=orgs)

@app.route("/organisations/add", methods=["GET", "POST"])
@login_required
def add_org():
    if request.method == "POST":
        db = get_db()
        db.execute(
            """INSERT INTO Organisations 
            (Name, Description, ContactPerson, Email, Password, Phone, Address, Website, Logo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                request.form["Name"],
                request.form.get("Description"),
                request.form.get("ContactPerson"),
                request.form.get("Email"),
                request.form.get("Password"),
                request.form.get("Phone"),
                request.form.get("Address"),
                request.form.get("Website"),
                request.form.get("Logo")
            )
        )
        db.commit()
        flash("Organisation added successfully.", "success")
        return redirect(url_for("list_orgs"))
    return render_template("add_org.html")

@app.route("/organisations/<int:id>/edit", methods=["GET", "POST"])
@login_required
def update_org(id):
    db = get_db()
    org = db.execute("SELECT * FROM Organisations WHERE OrganisationID=?", (id,)).fetchone()
    if request.method == "POST":
        db.execute(
            """UPDATE Organisations
               SET Name=?, Description=?, ContactPerson=?, Email=?, Password=?, Phone=?, Address=?, Website=?, Logo=?
               WHERE OrganisationID=?""",
            (
                request.form["Name"],
                request.form.get("Description"),
                request.form.get("ContactPerson"),
                request.form.get("Email"),
                request.form.get("Password"),
                request.form.get("Phone"),
                request.form.get("Address"),
                request.form.get("Website"),
                request.form.get("Logo"),
                id
            )
        )
        db.commit()
        flash("Organisation updated successfully.", "success")
        return redirect(url_for("list_orgs"))
    return render_template("update_org.html", org=org)

@app.route("/organisations/<int:id>/delete", methods=["POST"])
@login_required
def delete_org(id):
    db = get_db()
    db.execute("DELETE FROM Organisations WHERE OrganisationID=?", (id,))
    db.commit()
    flash("Organisation deleted successfully.", "success")
    return redirect(url_for("list_orgs"))

# --- Events ---
@app.route("/events")
@login_required
def list_events():
    db = get_db()
    events = db.execute("SELECT * FROM Events").fetchall()
    return render_template("events.html", events=events)

@app.route("/events/add", methods=["GET", "POST"])
@login_required
def add_event():
    db = get_db()
    orgs = db.execute("SELECT * FROM Organisations").fetchall()
    if request.method == "POST":
        db.execute(
            """INSERT INTO Events 
            (OrganisationID, Name, Description, Date, StartTime, EndTime, Location, Status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                request.form["OrganisationID"],
                request.form["Name"],
                request.form.get("Description"),
                request.form.get("Date"),
                request.form.get("StartTime"),
                request.form.get("EndTime"),
                request.form.get("Location"),
                request.form.get("Status")
            )
        )
        db.commit()
        flash("Event added successfully.", "success")
        return redirect(url_for("list_events"))
    return render_template("add_event.html", orgs=orgs)

@app.route("/events/<int:id>/edit", methods=["GET", "POST"])
@login_required
def update_event(id):
    db = get_db()
    event = db.execute("SELECT * FROM Events WHERE EventID=?", (id,)).fetchone()
    orgs = db.execute("SELECT * FROM Organisations").fetchall()
    if request.method == "POST":
        db.execute(
            """UPDATE Events 
               SET OrganisationID=?, Name=?, Description=?, Date=?, StartTime=?, EndTime=?, Location=?, Status=?
               WHERE EventID=?""",
            (
                request.form["OrganisationID"],
                request.form["Name"],
                request.form.get("Description"),
                request.form.get("Date"),
                request.form.get("StartTime"),
                request.form.get("EndTime"),
                request.form.get("Location"),
                request.form.get("Status"),
                id
            )
        )
        db.commit()
        flash("Event updated successfully.", "success")
        return redirect(url_for("list_events"))
    return render_template("update_event.html", event=event, orgs=orgs)

@app.route("/events/<int:id>/delete", methods=["POST"])
@login_required
def delete_event(id):
    db = get_db()
    db.execute("DELETE FROM Events WHERE EventID=?", (id,))
    db.commit()
    flash("Event deleted successfully.", "success")
    return redirect(url_for("list_events"))

# --- Roles ---
@app.route("/roles")
@login_required
def list_roles():
    db = get_db()
    roles = db.execute("SELECT * FROM Roles").fetchall()
    return render_template("roles.html", roles=roles)

@app.route("/roles/add", methods=["GET", "POST"])
@login_required
def add_role():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO Roles (Name, Description) VALUES (?, ?)",
            (request.form["Name"], request.form.get("Description"))
        )
        db.commit()
        flash("Role added successfully.", "success")
        return redirect(url_for("list_roles"))
    return render_template("add_role.html")

@app.route("/roles/<int:id>/edit", methods=["GET", "POST"])
@login_required
def update_role(id):
    db = get_db()
    role = db.execute("SELECT * FROM Roles WHERE RoleID=?", (id,)).fetchone()
    if request.method == "POST":
        db.execute(
            "UPDATE Roles SET Name=?, Description=? WHERE RoleID=?",
            (request.form["Name"], request.form.get("Description"), id)
        )
        db.commit()
        flash("Role updated successfully.", "success")
        return redirect(url_for("list_roles"))
    return render_template("update_role.html", role=role)

@app.route("/roles/<int:id>/delete", methods=["POST"])
@login_required
def delete_role(id):
    db = get_db()
    db.execute("DELETE FROM Roles WHERE RoleID=?", (id,))
    db.commit()
    flash("Role deleted successfully.", "success")
    return redirect(url_for("list_roles"))

# --- Skills ---
@app.route("/skills")
@login_required
def list_skills():
    db = get_db()
    skills = db.execute("SELECT * FROM Skills").fetchall()
    return render_template("skills.html", skills=skills)

@app.route("/skills/add", methods=["GET", "POST"])
@login_required
def add_skill():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO Skills (Name, Description) VALUES (?, ?)",
            (request.form["Name"], request.form.get("Description"))
        )
        db.commit()
        flash("Skill added successfully.", "success")
        return redirect(url_for("list_skills"))
    return render_template("add_skill.html")

@app.route("/skills/<int:id>/edit", methods=["GET", "POST"])
@login_required
def update_skill(id):
    db = get_db()
    skill = db.execute("SELECT * FROM Skills WHERE SkillID=?", (id,)).fetchone()
    if request.method == "POST":
        db.execute(
            "UPDATE Skills SET Name=?, Description=? WHERE SkillID=?",
            (request.form["Name"], request.form.get("Description"), id)
        )
        db.commit()
        flash("Skill updated successfully.", "success")
        return redirect(url_for("list_skills"))
    return render_template("update_skill.html", skill=skill)

@app.route("/skills/<int:id>/delete", methods=["POST"])
@login_required
def delete_skill(id):
    db = get_db()
    db.execute("DELETE FROM Skills WHERE SkillID=?", (id,))
    db.commit()
    flash("Skill deleted successfully.", "success")
    return redirect(url_for("list_skills"))

# --- Signups ---
@app.route("/signups")
@login_required
def list_signups():
    db = get_db()
    signups = db.execute(
        """SELECT s.SignupID, v.FirstName || ' ' || v.LastName AS VolunteerName,
                  e.Name AS EventName, r.Name AS RoleName, s.Status
           FROM Signups s
           JOIN Volunteers v ON s.VolunteerID = v.VolunteerID
           JOIN Events e ON s.EventID = e.EventID
           JOIN Roles r ON s.RoleID = r.RoleID"""
    ).fetchall()
    return render_template("signups.html", signups=signups)

@app.route("/signups/add", methods=["GET", "POST"])
@login_required
def add_signup():
    db = get_db()
    volunteers = db.execute("SELECT * FROM Volunteers").fetchall()
    events = db.execute("SELECT * FROM Events").fetchall()
    roles = db.execute("SELECT * FROM Roles").fetchall()
    if request.method == "POST":
        db.execute(
            "INSERT INTO Signups (VolunteerID, EventID, RoleID, Status) VALUES (?, ?, ?, ?)",
            (
                request.form["VolunteerID"],
                request.form["EventID"],
                request.form["RoleID"],
                request.form.get("Status")
            )
        )
        db.commit()
        flash("Signup added successfully.", "success")
        return redirect(url_for("list_signups"))
    return render_template("add_signup.html", volunteers=volunteers, events=events, roles=roles)

# --- Signups Edit ---
@app.route("/signups/<int:id>/edit", methods=["GET", "POST"])
@login_required
def update_signup(id):
    db = get_db()
    signup = db.execute("SELECT * FROM Signups WHERE SignupID=?", (id,)).fetchone()
    volunteers = db.execute("SELECT * FROM Volunteers").fetchall()
    events = db.execute("SELECT * FROM Events").fetchall()
    roles = db.execute("SELECT * FROM Roles").fetchall()

    if request.method == "POST":
        db.execute(
            """UPDATE Signups
               SET VolunteerID=?, EventID=?, RoleID=?, Status=?
               WHERE SignupID=?""",
            (
                request.form["VolunteerID"],
                request.form["EventID"],
                request.form["RoleID"],
                request.form["Status"],
                id
            )
        )
        db.commit()
        return redirect(url_for("list_signups"))

    return render_template("update_signup.html", signup=signup, volunteers=volunteers, events=events, roles=roles)


@app.route("/signups/<int:id>/delete", methods=["POST"])
@login_required
def delete_signup(id):
    db = get_db()
    db.execute("DELETE FROM Signups WHERE SignupID=?", (id,))
    db.commit()
    flash("Signup deleted successfully.", "success")
    return redirect(url_for("list_signups"))

# ---------- Main ----------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
