from flask import Flask, render_template, request, redirect, url_for, g, session, flash, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"
DATABASE = "community_connect.db"

# ====================
# DB HELPERS
# ====================

def get_db():
    """Establishes and returns a database connection."""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # This allows accessing columns by name
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Closes the database connection at the end of the request."""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database from schema.sql and seed.sql if they exist."""
    first_time = not os.path.exists(DATABASE)
    with app.app_context():
        db = get_db()
        if first_time:
            if os.path.exists("schema.sql"):
                with open("schema.sql", "r") as f:
                    db.executescript(f.read())
            if os.path.exists("seed.sql"):
                with open("seed.sql", "r") as f:
                    db.executescript(f.read())
            db.commit()

# ====================
# AUTH & ROLE DECORATORS
# ====================

def login_required(f):
    """Decorator to ensure a user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def volunteer_required(f):
    """Decorator to restrict access to volunteers only."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("account_type") != "volunteer":
            flash("Volunteers only.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrapper

def org_required(f):
    """Decorator to restrict access to organizations only."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("account_type") != "organisation":
            flash("Organisations only.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrapper

# ====================
# AUTHENTICATION ROUTES
# ====================

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "volunteer")
        db = get_db()

        if role == "volunteer":
            user = db.execute("SELECT * FROM Volunteers WHERE Email = ?", (email,)).fetchone()
            if user and check_password_hash(user["Password"], password):
                session.clear()
                session["user_id"] = user["VolunteerID"]
                session["email"] = user["Email"]
                session["name"] = user["FirstName"]
                session["account_type"] = "volunteer"
                flash("Logged in as Volunteer.", "success")
                return redirect(url_for("index"))

        elif role == "organisation":
            user = db.execute("SELECT * FROM Organisations WHERE Email = ?", (email,)).fetchone()
            if user and check_password_hash(user["Password"], password):
                session.clear()
                session["user_id"] = user["OrganisationID"]
                session["email"] = user["Email"]
                session["name"] = user["Name"]
                session["account_type"] = "organisation"
                flash("Logged in as Organisation.", "success")
                return redirect(url_for("index"))

        flash("Invalid email, role, or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Handles user logout."""
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

@app.route("/register_select")
def register_select():
    """Renders a page for the user to choose their account type."""
    return render_template("register_select.html")

@app.route("/register_volunteer", methods=["GET", "POST"])
def register_volunteer_page():
    """Renders volunteer registration form and handles submission."""
    if request.method == "POST":
        db = get_db()
        email = request.form["email"].strip()
        
        existing_user = db.execute("SELECT 1 FROM Volunteers WHERE Email = ? UNION ALL SELECT 1 FROM Organisations WHERE Email = ?", (email, email)).fetchone()
        if existing_user:
            flash("An account with that email already exists.", "error")
            return redirect(url_for("register_volunteer_page"))

        availability = 1 if 'availability' in request.form else 0
        password = generate_password_hash(request.form["password"])

        try:
            db.execute(
                """INSERT INTO Volunteers (FirstName, LastName, Email, Password, Phone, Address, DateOfBirth, Availability, EmergencyContact)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (request.form.get("first_name"), request.form.get("last_name"), email, password, request.form.get("phone"), request.form.get("address"), request.form.get("dob"), availability, request.form.get("emergency_contact"))
            )
            db.commit()
            flash("Volunteer registration successful! You can now log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.Error as e:
            db.rollback()
            flash(f"An error occurred during registration: {e}", "error")
            return redirect(url_for("register_volunteer_page"))
    return render_template("register_volunteer.html")

@app.route("/register_organisation", methods=["GET", "POST"])
def register_organisation_page():
    """Renders organisation registration form and handles submission."""
    if request.method == "POST":
        db = get_db()
        email = request.form["email"].strip()
        
        existing_user = db.execute("SELECT 1 FROM Volunteers WHERE Email = ? UNION ALL SELECT 1 FROM Organisations WHERE Email = ?", (email, email)).fetchone()
        if existing_user:
            flash("An account with that email already exists.", "error")
            return redirect(url_for("register_organisation_page"))

        try:
            db.execute(
                """INSERT INTO Organisations (Name, ContactPerson, Email, Password, Phone, Address, Website, Description, Logo)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (request.form.get("name"), request.form.get("contact_person"), email, generate_password_hash(request.form["password"]), request.form.get("phone"), request.form.get("address"), request.form.get("website"), request.form.get("description"), request.form.get("logo"))
            )
            db.commit()
            flash("Organisation registration successful! You can now log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.Error as e:
            db.rollback()
            flash(f"An error occurred during registration: {e}", "error")
            return redirect(url_for("register_organisation_page"))
    return render_template("register_organisation.html")

# ====================
# VOLUNTEER ROUTES
# ====================

@app.route("/volunteer/dashboard")
@login_required
@volunteer_required
def volunteer_dashboard():
    """Displays the volunteer's dashboard."""
    db = get_db()
    signups = db.execute(
        """SELECT s.Status, e.Name AS EventName, e.Date, e.Location, o.Name AS OrgName, s.EventID
           FROM Signups s JOIN Events e ON s.EventID = e.EventID
           JOIN Organisations o ON e.OrganisationID = o.OrganisationID
           WHERE s.VolunteerID = ?
           ORDER BY date(e.Date) ASC""", (session["user_id"],)
    ).fetchall()
    return render_template("volunteer_dashboard.html", signups=signups)

@app.route("/volunteer/account/edit", methods=["GET", "POST"])
@login_required
@volunteer_required
def edit_volunteer_account():
    """Allows volunteers to edit their account information."""
    db = get_db()
    volunteer = db.execute("SELECT * FROM Volunteers WHERE VolunteerID=?", (session["user_id"],)).fetchone()
    if not volunteer:
        flash("Volunteer account not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        db.execute(
            """UPDATE Volunteers SET FirstName=?, LastName=?, Phone=?, Address=?, DateOfBirth=?, Availability=?, ProfilePhoto=?, EmergencyContact=?
               WHERE VolunteerID=?""",
            (request.form["first_name"].strip(), request.form["last_name"].strip(), request.form.get("phone"), request.form.get("address"), request.form.get("dob"), request.form.get("availability"), request.form.get("profile_photo"), request.form.get("emergency_contact"), session["user_id"])
        )
        db.commit()
        session["name"] = request.form["first_name"].strip()
        flash("Account updated successfully.", "success")
        return redirect(url_for("volunteer_dashboard"))
    return render_template("edit_volunteer_account.html", volunteer=volunteer)

@app.route("/volunteer/skills", methods=["GET", "POST"])
@login_required
@volunteer_required
def manage_volunteer_skills():
    """Manages volunteer's skills, allowing them to add or remove existing skills."""
    db = get_db()
    if request.method == "POST":
        skill_id = request.form.get("skill_id")
        if skill_id:
            db.execute("INSERT OR IGNORE INTO VolunteerSkills (VolunteerID, SkillID) VALUES (?, ?)", (session["user_id"], skill_id))
            db.commit()
            flash("Skill added.", "success")
        return redirect(url_for("manage_volunteer_skills"))

    current_skills = db.execute(
        """SELECT s.SkillID, s.Name, s.Description FROM VolunteerSkills vs
           JOIN Skills s ON vs.SkillID = s.SkillID WHERE vs.VolunteerID = ?""", (session["user_id"],)
    ).fetchall()
    all_skills = db.execute("SELECT * FROM Skills").fetchall()
    return render_template("manage_volunteer_skills.html", current_skills=current_skills, all_skills=all_skills)

@app.route("/volunteer/skills/add_new", methods=["POST"])
@login_required
@volunteer_required
def add_new_skill():
    """Handles adding a new skill to the Skills table and linking it to the volunteer."""
    db = get_db()
    new_skill_name = request.form.get("new_skill_name", "").strip()
    new_skill_description = request.form.get("new_skill_description", "").strip()

    if not new_skill_name:
        flash("Skill name cannot be empty.", "error")
        return redirect(url_for("manage_volunteer_skills"))

    try:
        existing_skill = db.execute("SELECT SkillID FROM Skills WHERE Name = ?", (new_skill_name,)).fetchone()
        if existing_skill:
            skill_id = existing_skill["SkillID"]
            flash("This skill already exists. It has been added to your profile.", "info")
        else:
            result = db.execute("INSERT INTO Skills (Name, Description) VALUES (?, ?)", (new_skill_name, new_skill_description))
            skill_id = result.lastrowid
            flash(f"New skill '{new_skill_name}' created and added to your profile.", "success")

        db.execute("INSERT OR IGNORE INTO VolunteerSkills (VolunteerID, SkillID) VALUES (?, ?)", (session["user_id"], skill_id))
        db.commit()
    except sqlite3.Error as e:
        flash(f"An error occurred: {e}", "error")
    return redirect(url_for("manage_volunteer_skills"))

@app.route("/volunteer/skills/<int:skill_id>/delete", methods=["POST"])
@login_required
@volunteer_required
def delete_volunteer_skill(skill_id):
    """Deletes a skill from a volunteer's profile."""
    db = get_db()
    db.execute("DELETE FROM VolunteerSkills WHERE VolunteerID = ? AND SkillID = ?", (session["user_id"], skill_id))
    db.commit()
    flash("Skill removed.", "success")
    return redirect(url_for("manage_volunteer_skills"))

@app.route("/volunteers/<int:volunteer_id>")
@login_required
def view_volunteer_profile(volunteer_id):
    """Displays a volunteer's full profile, including calculated age and skills."""
    db = get_db()
    volunteer = db.execute(
        """SELECT * , (strftime('%Y', 'now') - strftime('%Y', DateOfBirth)) - (CASE WHEN strftime('%m-%d', 'now') < strftime('%m-%d', DateOfBirth) THEN 1 ELSE 0 END) AS Age
           FROM Volunteers WHERE VolunteerID = ?""", (volunteer_id,)
    ).fetchone()
    if not volunteer:
        flash("Volunteer not found.", "error")
        return redirect(url_for("list_volunteers"))

    events_participated = db.execute("SELECT COUNT(*) AS EventsParticipated FROM Signups sup WHERE sup.VolunteerID = ?", (volunteer_id,)).fetchone()
    skills = db.execute(
        """SELECT s.Name, s.Description FROM VolunteerSkills vs
           JOIN Skills s ON vs.SkillID = s.SkillID WHERE vs.VolunteerID = ?""", (volunteer_id,)
    ).fetchall()

    return render_template("view_volunteer_profile.html", volunteer=volunteer, eventsparticipated=events_participated, skills=skills)

# ====================
# ORGANISATION ROUTES
# ====================

@app.route("/organisation/dashboard")
@login_required
@org_required
def organisation_dashboard():
    """Displays the organisation's dashboard."""
    db = get_db()
    events = db.execute("SELECT EventID, Name, Description, Date, Location FROM Events WHERE OrganisationID = ? ORDER BY date(Date) ASC", (session["user_id"],)).fetchall()
    return render_template("organisation_dashboard.html", events=events)

@app.route("/org/account/edit", methods=["GET", "POST"])
@login_required
@org_required
def edit_org_account():
    """Allows an organisation to edit its account information and change its password."""
    db = get_db()
    org = db.execute("SELECT * FROM Organisations WHERE OrganisationID=?", (session["user_id"],)).fetchone()
    if not org:
        flash("Organisation not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        # ... (unchanged logic for updating account and password) ...
        name = request.form["name"]
        description = request.form.get("description")
        phone = request.form.get("phone")
        website = request.form.get("website")
        contact_person = request.form.get("contact_person")
        address = request.form.get("address")
        logo = request.form.get("logo")
        
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        update_query = """UPDATE Organisations SET Name=?, Description=?, Phone=?, Website=?, ContactPerson=?, Address=?, Logo=? WHERE OrganisationID=?"""
        update_params = [name, description, phone, website, contact_person, address, logo, session["user_id"]]

        if new_password:
            if new_password != confirm_password:
                flash("New password and confirmation do not match.", "danger")
                return redirect(url_for("edit_org_account"))
            if not check_password_hash(org['Password'], current_password):
                flash("Incorrect current password.", "danger")
                return redirect(url_for("edit_org_account"))
            
            hashed_password = generate_password_hash(new_password)
            update_query = """UPDATE Organisations SET Name=?, Description=?, Phone=?, Website=?, ContactPerson=?, Address=?, Logo=?, Password=? WHERE OrganisationID=?"""
            update_params = [name, description, phone, website, contact_person, address, logo, hashed_password, session["user_id"]]

        db.execute(update_query, tuple(update_params))
        db.commit()
        
        session["name"] = name
        flash("Account updated successfully.", "success")
        return redirect(url_for("organisation_dashboard"))

    return render_template("edit_org_account.html", org=org)

@app.route("/events/<int:event_id>/signups")
@login_required
@org_required
def view_event_signups(event_id):
    """Allows an organisation to view and manage volunteer signups for a specific event."""
    db = get_db()
    event = db.execute("SELECT * FROM Events WHERE EventID=? AND OrganisationID=?", (event_id, session["user_id"])).fetchone()
    if not event:
        flash("Event not found or not authorised.", "error")
        return redirect(url_for("list_events"))

    signups = db.execute(
        """SELECT s.SignupID, s.Status, v.VolunteerID, v.FirstName, v.LastName, v.Email, v.Phone, r.RoleID, r.Name AS RoleName, r.Description AS RoleDescription
           FROM Signups s
           JOIN Volunteers v ON s.VolunteerID = v.VolunteerID
           LEFT JOIN Roles r ON s.RoleID = r.RoleID
           WHERE s.EventID = ?""", (event_id,)
    ).fetchall()
    
    roles = db.execute("SELECT RoleID, Name FROM Roles").fetchall()
    return render_template("view_signups.html", event=event, signups=signups, roles=roles)

@app.route("/signups/<int:signup_id>/update_status_and_role", methods=["POST"])
@login_required
@org_required
def update_signup_status_and_role(signup_id):
    """Updates a volunteer's signup status and assigns a role."""
    db = get_db()
    signup = db.execute("SELECT * FROM Signups WHERE SignupID = ?", (signup_id,)).fetchone()
    if not signup:
        flash("Signup not found.", "error")
        return redirect(url_for('list_events'))

    event = db.execute("SELECT * FROM Events WHERE EventID = ? AND OrganisationID = ?", (signup["EventID"], session["user_id"])).fetchone()
    if not event:
        flash("You are not authorised to update this signup.", "error")
        return redirect(url_for('list_events'))
    
    status = request.form.get("status")
    role_id = request.form.get("role_id")
    
    if role_id == "":
        role_id = None
    
    db.execute("UPDATE Signups SET Status = ?, RoleID = ? WHERE SignupID = ?", (status, role_id, signup_id))
    db.commit()
    flash("Volunteer signup status and role updated successfully.", "success")
    return redirect(url_for('view_event_signups', event_id=event["EventID"]))

# ====================
# EVENT ROUTES
# ====================

@app.route("/events")
@login_required
def list_events():
    """Lists events for both volunteers and organisations."""
    db = get_db()
    user_id = session.get('user_id')
    account_type = session.get('account_type')

    if account_type == 'organisation':
        my_events = db.execute(
            """SELECT e.*, o.Name AS OrgName
               FROM Events e 
               JOIN Organisations o ON e.OrganisationID = o.OrganisationID
               WHERE e.OrganisationID = ? ORDER BY e.Date""", (user_id,)
        ).fetchall()
        other_events = db.execute(
            """SELECT e.*, o.Name AS OrgName
               FROM Events e 
               JOIN Organisations o ON e.OrganisationID = o.OrganisationID
               WHERE e.OrganisationID != ? ORDER BY e.Date""", (user_id,)
        ).fetchall()
        return render_template("list_events.html", my_events=my_events, other_events=other_events)
    elif account_type == 'volunteer':
        events = db.execute(
            """SELECT e.*, o.Name AS OrgName, s.Status AS signup_status
               FROM Events e
               JOIN Organisations o ON e.OrganisationID = o.OrganisationID
               LEFT JOIN Signups s ON e.EventID = s.EventID AND s.VolunteerID = ?
               ORDER BY e.Date""", (user_id,)
        ).fetchall()
        return render_template("list_events.html", events=events)
    return redirect(url_for('login'))

@app.route("/events/<int:event_id>")
@login_required
def view_event(event_id):
    """Displays details for a single event."""
    db = get_db()
    event = db.execute(
        """SELECT e.*, o.Name AS OrgName, e.EndTime - e.StartTime AS Duration
           FROM Events e 
           JOIN Organisations o ON e.OrganisationID = o.OrganisationID
           WHERE e.EventID = ?""", (event_id,)
    ).fetchone()
    if not event:
        flash("Event not found.", "error")
        return redirect(url_for('index'))

    skills_data = db.execute(
        """SELECT s.Name, s.Description, COUNT(vs.VolunteerID) AS FilledCount
           FROM EventSkills es
           JOIN Skills s ON es.SkillID = s.SkillID
           LEFT JOIN Signups sup ON es.EventID = sup.EventID AND sup.Status = 'Accepted'
           LEFT JOIN VolunteerSkills vs ON sup.VolunteerID = vs.VolunteerID AND vs.SkillID = es.SkillID
           WHERE es.EventID = ?
           GROUP BY s.SkillID, s.Name, s.Description""", (event_id,)
    ).fetchall()

    required_skill_count = db.execute(
        """SELECT COUNT(DISTINCT es.SkillID) AS RequiredSkillCount FROM EventSkills es
           JOIN Signups s ON s.EventID = es.EventID
           JOIN VolunteerSkills vs ON vs.VolunteerID = s.VolunteerID AND vs.SkillID = es.SkillID
           WHERE es.EventID = ? AND s.status = 'Accepted'""", (event_id,)
    ).fetchone()
    event_skill_count = db.execute("""SELECT COUNT(*) AS EventSkillCount FROM EventSkills WHERE EventID = ?""", (event_id,)).fetchone()
    volunteer_count = db.execute("""SELECT COUNT(*) AS VolunteerCount FROM Signups sup WHERE sup.EventID = ?""", (event_id,)).fetchone()

    signup = None
    role = None
    if session.get("account_type") == 'volunteer':
        signup = db.execute("SELECT Status FROM Signups s WHERE VolunteerID = ? AND EventID = ?", (session["user_id"], event_id)).fetchone()
        role = db.execute("SELECT r.* FROM Signups s JOIN Roles r ON r.RoleID = s.RoleID WHERE VolunteerID = ? AND EventID = ?", (session["user_id"], event_id)).fetchone()
    
    return render_template("view_event.html", event=event, skills_data=skills_data, signup=signup, role=role, account_type=session.get("account_type"), requiredskillcount=required_skill_count, eventskillcount=event_skill_count, volunteercount=volunteer_count)

@app.route("/events/<int:event_id>/signup", methods=["POST"])
@login_required
@volunteer_required
def signup_for_event(event_id):
    """Handles a volunteer signing up for an event."""
    db = get_db()
    existing_signup = db.execute("SELECT 1 FROM Signups WHERE VolunteerID = ? AND EventID = ?", (session["user_id"], event_id)).fetchone()
    if existing_signup:
        flash("You are already signed up for this event.", "info")
    else:
        db.execute("INSERT INTO Signups (VolunteerID, EventID, Status) VALUES (?, ?, 'Pending')", (session["user_id"], event_id))
        db.commit()
        flash("Successfully signed up for the event! Your status is 'Pending'.", "success")
    return redirect(url_for("list_events"))

@app.route("/events/<int:event_id>/retract_signup", methods=["POST"])
@login_required
@volunteer_required
def retract_signup(event_id):
    """Allows a volunteer to retract their pending signup for an event."""
    db = get_db()
    volunteer_id = session.get('user_id')
    signup = db.execute("""SELECT Status FROM Signups WHERE VolunteerID = ? AND EventID = ?""", (volunteer_id, event_id)).fetchone()
    if signup and signup['Status'] != 'Accepted':
        db.execute("DELETE FROM Signups WHERE VolunteerID = ? AND EventID = ?", (volunteer_id, event_id))
        db.commit()
        flash("Your signup has been retracted.", "success")
    elif signup and signup['Status'] == 'Accepted':
        flash("Cannot retract signup after it has been accepted.", "error")
    else:
        flash("No pending signup found for this event.", "error")
    return redirect(url_for('list_events'))

@app.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
@org_required
def edit_event(event_id):
    """Allows an organisation to edit an event and its skills."""
    db = get_db()
    event = db.execute("SELECT * FROM Events WHERE EventID=? AND OrganisationID=?", (event_id, session["user_id"])).fetchone()
    if not event:
        flash("Not authorised.", "error")
        return redirect(url_for("list_events"))

    all_skills = db.execute("SELECT * FROM Skills ORDER BY Name").fetchall()
    event_skills_with_names = db.execute("""SELECT S.SkillID, S.Name FROM EventSkills ES JOIN Skills S ON ES.SkillID = S.SkillID WHERE ES.EventID = ? ORDER BY S.Name""", (event_id,)).fetchall()
    event_skill_ids = {skill['SkillID'] for skill in event_skills_with_names}
    
    if request.method == "POST":
        db.execute(
            """UPDATE Events SET Name=?, Description=?, Date=?, Location=?, StartTime=?, EndTime=?, Status=? WHERE EventID=? AND OrganisationID=?""",
            (request.form["name"], request.form.get("description"), request.form.get("date"), request.form.get("location"), request.form.get("start_time"), request.form.get("end_time"), request.form.get("status"), event_id, session["user_id"])
        )
        db.execute("DELETE FROM EventSkills WHERE EventID=?", (event_id,))
        selected_skills = request.form.getlist("skills")
        for skill_id in selected_skills:
            db.execute("INSERT INTO EventSkills (EventID, SkillID) VALUES (?, ?)", (event_id, int(skill_id)))
        db.commit()
        flash("Event updated.", "success")
        return redirect(url_for("edit_event", event_id=event_id))

    return render_template("edit_event.html", event=event, all_skills=all_skills, event_skills_with_names=event_skills_with_names, event_skill_ids=event_skill_ids)

@app.route("/events/add", methods=["GET", "POST"])
@login_required
@org_required
def add_event():
    """Allows an organisation to create a new event."""
    db = get_db()
    all_skills = db.execute("SELECT * FROM Skills ORDER BY Name").fetchall()
    if request.method == "POST":
        db.execute(
            """INSERT INTO Events (OrganisationID, Name, Description, Date, StartTime, EndTime, Location, Status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (session["user_id"], request.form["name"], request.form.get("description"), request.form.get("date"), request.form.get("start_time"), request.form.get("end_time"), request.form.get("location"), request.form.get("status", "Open"))
        )
        event_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        selected_skills = request.form.getlist("skills")
        for skill_id in selected_skills:
            db.execute("INSERT INTO EventSkills (EventID, SkillID) VALUES (?, ?)", (event_id, int(skill_id)))
        db.commit()
        flash("Event created.", "success")
        return redirect(url_for("list_events"))
    return render_template("add_event.html", all_skills=all_skills)

@app.route("/events/<int:event_id>/delete", methods=["POST"])
@login_required
@org_required
def delete_event(event_id):
    """Deletes an event from the database."""
    db = get_db()
    db.execute("DELETE FROM Events WHERE EventID=? AND OrganisationID=?", (event_id, session["user_id"]))
    db.commit()
    flash("Event deleted.", "success")
    return redirect(url_for("list_events"))

# ====================
# GENERAL ROUTES
# ====================

@app.route("/")
@login_required
def index():
    """Redirects authenticated users to their respective dashboards."""
    if session.get("account_type") == "volunteer":
        return redirect(url_for("volunteer_dashboard"))
    elif session.get("account_type") == "organisation":
        return redirect(url_for("organisation_dashboard"))
    return render_template("index.html")

@app.route("/volunteers")
@login_required
def list_volunteers():
    """Lists all volunteers, with optional filtering by skill name."""
    db = get_db()
    search_query = request.args.get('q', '')
    query = """
        SELECT V.VolunteerID, V.FirstName ||' '|| V.LastName AS Fullname,
               (strftime('%Y', 'now') - strftime('%Y', DateOfBirth)) - (CASE WHEN strftime('%m-%d', 'now') < strftime('%m-%d', DateOfBirth) THEN 1 ELSE 0 END) AS Age,
               V.Email, V.Phone, V.Availability, GROUP_CONCAT(S.Name) AS Skills
        FROM Volunteers V
        LEFT JOIN VolunteerSkills VS ON V.VolunteerID = VS.VolunteerID
        LEFT JOIN Skills S ON VS.SkillID = S.SkillID
    """
    params = []
    if search_query:
        query += " WHERE S.Name LIKE ?"
        params.append('%' + search_query + '%')
    query += " GROUP BY V.VolunteerID ORDER BY V.FirstName"
    volunteers = db.execute(query, params).fetchall()
    return render_template("list_volunteers.html", volunteers=volunteers, query=search_query)

@app.route("/volunteers/stats", methods=["GET", "POST"])
@login_required
def volunteer_stats():
    """Displays statistics on volunteer skills."""
    db = get_db()
    skill_count = db.execute(
        """SELECT s.Name, COUNT(*) AS SkillCount
           FROM Volunteers v JOIN VolunteerSkills vs ON v.VolunteerID = vs.VolunteerID
           JOIN Skills s ON vs.SkillID = s.SkillID
           GROUP BY vs.SkillID"""
    ).fetchall()
    return render_template("volunteer_stats.html", skillcount=skill_count)

@app.route('/events/<int:event_id>/skills_json')
@login_required
def get_event_skills_json(event_id):
    """Returns a JSON object of an event's skills."""
    db = get_db()
    event = db.execute("SELECT Name FROM Events WHERE EventID = ?", (event_id,)).fetchone()
    if not event:
        return jsonify({"error": "Event not found."}), 404
    skills = db.execute("SELECT T2.Name FROM EventSkills AS T1 JOIN Skills AS T2 ON T1.SkillID = T2.SkillID WHERE T1.EventID = ?", (event_id,)).fetchall()
    skill_names = [skill['Name'] for skill in skills]
    return jsonify({"event_name": event['Name'], "skills": skill_names})

@app.route("/organisations")
@login_required
def list_orgs():
    """Lists all organisations, with a special view for organisation users."""
    db = get_db()
    if session.get('account_type') == 'organisation':
        my_org = db.execute("SELECT OrganisationID, Name, Description, Email, Phone, Website, ContactPerson FROM Organisations WHERE OrganisationID = ?", (session['user_id'],)).fetchone()
        other_orgs = db.execute("SELECT OrganisationID, Name, Description, Email, Phone, Website, ContactPerson FROM Organisations WHERE OrganisationID != ?", (session['user_id'],)).fetchall()
        return render_template("list_orgs.html", my_org=my_org, other_orgs=other_orgs)
    else:
        all_orgs = db.execute("SELECT OrganisationID, Name, Description, Email, Phone, Website, ContactPerson FROM Organisations").fetchall()
        return render_template("list_orgs.html", all_orgs=all_orgs)

@app.route("/organisations/<int:org_id>")
@login_required
def view_organisation(org_id):
    """Displays a single organisation's details on a full page."""
    db = get_db()
    org = db.execute("""SELECT * FROM Organisations WHERE OrganisationID = ?""", (org_id,)).fetchone()
    if not org:
        flash("Organisation not found.", "danger")
        return redirect(url_for('list_orgs'))
    return render_template("view_organisation.html", org=org)

@app.route("/organisation/events_full")
@login_required
@org_required
def organisation_events_full():
    """Lists all events for an organisation, with modals for detailed view."""
    db = get_db()
    my_events = db.execute("""SELECT * FROM Events WHERE OrganisationID = ? ORDER BY Date""", (session["user_id"],)).fetchall()
    other_events = db.execute("""SELECT e.*, o.Name AS OrgName FROM Events e JOIN Organisations o ON e.OrganisationID = o.OrganisationID WHERE e.OrganisationID != ? ORDER BY e.Date""", (session["user_id"],)).fetchall()
    return render_template("organisation_events_full.html", my_events=my_events, other_events=other_events)

# ====================
# MAIN APPLICATION RUN
# ====================

if __name__ == "__main__":
    init_db()
    app.run(debug=True)