from flask import Flask, render_template, request, redirect, url_for, g, session, flash, jsonify
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

# ---------- Auth & Role Decorators ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def volunteer_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("account_type") != "volunteer":
            flash("Volunteers only.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrapper

def org_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("account_type") != "organisation":
            flash("Organisations only.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrapper

# ---------- Auth Routes ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "volunteer")

        db = get_db()

        if role == "volunteer":
            volunteer = db.execute("SELECT * FROM Volunteers WHERE Email = ?", (email,)).fetchone()
            if volunteer and check_password_hash(volunteer["Password"], password):
                session.clear()
                session["user_id"] = volunteer["VolunteerID"]
                session["email"] = volunteer["Email"]
                session["name"] = volunteer["FirstName"]
                session["account_type"] = "volunteer"
                flash("Logged in as Volunteer.", "success")
                return redirect(url_for("index"))

        elif role == "organisation":
            org = db.execute("SELECT * FROM Organisations WHERE Email = ?", (email,)).fetchone()
            if org and check_password_hash(org["Password"], password):
                session.clear()
                session["user_id"] = org["OrganisationID"]
                session["email"] = org["Email"]
                session["name"] = org["Name"]
                session["account_type"] = "organisation"
                flash("Logged in as Organisation.", "success")
                return redirect(url_for("index"))

        flash("Invalid email, role, or password.", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

@app.route("/register_select")
def register_select():
    """Renders a page for the user to choose their account type."""
    return render_template("register_select.html")


@app.route("/register_volunteer", methods=["GET", "POST"])
def register_volunteer_page():
    """
    Renders the volunteer registration form and handles form submission.
    """
    if request.method == "POST":
        db = get_db()
        email = request.form["email"].strip()

        # Check for existing email in both tables to prevent duplicates
        existing_volunteer = db.execute("SELECT 1 FROM Volunteers WHERE Email = ?", (email,)).fetchone()
        existing_organisation = db.execute("SELECT 1 FROM Organisations WHERE Email = ?", (email,)).fetchone()
        
        if existing_volunteer or existing_organisation:
            flash("An account with that email already exists.", "error")
            return redirect(url_for("register_volunteer_page"))

        # Get availability from the checkbox: 1 if checked, 0 otherwise
        availability = 1 if 'availability' in request.form else 0
        password = generate_password_hash(request.form["password"])

        try:
            db.execute(
                """INSERT INTO Volunteers
                   (FirstName, LastName, Email, Password, Phone, Address, DateOfBirth, Availability, EmergencyContact)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    request.form.get("first_name"),
                    request.form.get("last_name"),
                    email,
                    password,
                    request.form.get("phone"),
                    request.form.get("address"),
                    request.form.get("dob"),
                    availability,
                    request.form.get("emergency_contact"),
                ),
            )
            db.commit()
            flash("Volunteer registration successful! You can now log in.", "success")
            return redirect(url_for("login"))
            
        except sqlite3.Error as e:
            db.rollback()
            flash(f"An error occurred during registration: {e}", "error")
            return redirect(url_for("register_volunteer_page"))

    # Render the registration page for GET requests
    return render_template("register_volunteer.html")

@app.route("/register_organisation", methods=["GET", "POST"])
def register_organisation_page():
    """Renders the organisation registration form and handles its submission."""
    if request.method == "POST":
        db = get_db()
        email = request.form["email"].strip()
        
        # Check for existing email in both tables to prevent duplicates
        existing_volunteer = db.execute("SELECT 1 FROM Volunteers WHERE Email = ?", (email,)).fetchone()
        existing_organisation = db.execute("SELECT 1 FROM Organisations WHERE Email = ?", (email,)).fetchone()
        if existing_volunteer or existing_organisation:
            flash("An account with that email already exists.", "error")
            return redirect(url_for("register_organisation_page"))

        db.execute(
            """INSERT INTO Organisations
               (Name, ContactPerson, Email, Password, Phone, Address, Website, Description, Logo)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                request.form.get("name"),
                request.form.get("contact_person"),
                email,
                generate_password_hash(request.form["password"]),
                request.form.get("phone"),
                request.form.get("address"),
                request.form.get("website"),
                request.form.get("description"),
                request.form.get("logo"),
            ),
        )
        
        db.commit()
        flash("Organisation registration successful! You can now log in.", "success")
        return redirect(url_for("login"))

    # Renders the organisation registration form for GET requests
    return render_template("register_organisation.html")


@app.route("/")
@login_required
def index():
    if session.get("account_type") == "volunteer":
        return redirect(url_for("volunteer_dashboard"))
    elif session.get("account_type") == "organisation":
        return redirect(url_for("organisation_dashboard"))
    return render_template("index.html")

@app.route("/volunteer/dashboard")
@login_required
@volunteer_required
def volunteer_dashboard():
    db = get_db()
    # Fetch volunteer's upcoming signups
    signups = db.execute(
        """SELECT s.Status, e.Name AS EventName, e.Date, e.Location, o.Name AS OrgName, s.EventID
           FROM Signups s
           JOIN Events e ON s.EventID = e.EventID
           JOIN Organisations o ON e.OrganisationID = o.OrganisationID
           WHERE s.VolunteerID = ?
           ORDER BY date(e.Date) ASC""",
        (session["user_id"],)
    ).fetchall()
    return render_template("volunteer_dashboard.html", signups=signups)

@app.route("/organisation/dashboard")
@login_required
@org_required
def organisation_dashboard():
    db = get_db()
    # Fetch organisation's upcoming events
    events = db.execute(
        """SELECT EventID, Name, Description, Date, Location
           FROM Events
           WHERE OrganisationID = ?
           ORDER BY date(Date) ASC""",
        (session["user_id"],)
    ).fetchall()
    return render_template("organisation_dashboard.html", events=events)

# ---------- Volunteer-Specific Routes ----------
@app.route("/volunteer/account/edit", methods=["GET", "POST"])
@login_required
@volunteer_required
def edit_volunteer_account():
    db = get_db()
    volunteer = db.execute(
        "SELECT * FROM Volunteers WHERE VolunteerID=?",
        (session["user_id"],),
    ).fetchone()
    if not volunteer:
        flash("Volunteer account not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        db.execute(
            """UPDATE Volunteers
               SET FirstName=?, LastName=?, Phone=?, Address=?, DateOfBirth=?, Availability=?, ProfilePhoto=?, EmergencyContact=?
               WHERE VolunteerID=?""",
            (
                request.form["first_name"].strip(),
                request.form["last_name"].strip(),
                request.form.get("phone"),
                request.form.get("address"),
                request.form.get("dob"),
                request.form.get("availability"),
                request.form.get("profile_photo"),
                request.form.get("emergency_contact"),
                session["user_id"],
            ),
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
    db = get_db()
    
    # Handle adding an existing skill via POST request
    if request.method == "POST":
        skill_id = request.form.get("skill_id")
        if skill_id:
            db.execute(
                "INSERT OR IGNORE INTO VolunteerSkills (VolunteerID, SkillID) VALUES (?, ?)",
                (session["user_id"], skill_id)
            )
            db.commit()
            flash("Skill added.", "success")
        return redirect(url_for("manage_volunteer_skills"))

    current_skills = db.execute(
        """SELECT s.SkillID, s.Name, s.Description
           FROM VolunteerSkills vs
           JOIN Skills s ON vs.SkillID = s.SkillID
           WHERE vs.VolunteerID = ?""",
        (session["user_id"],)
    ).fetchall()
    
    all_skills = db.execute("SELECT * FROM Skills").fetchall()
    
    return render_template("manage_volunteer_skills.html", current_skills=current_skills, all_skills=all_skills)


@app.route("/volunteer/skills/add_new", methods=["POST"])
@login_required
@volunteer_required
def add_new_skill():
    db = get_db()
    new_skill_name = request.form.get("new_skill_name", "").strip()
    new_skill_description = request.form.get("new_skill_description", "").strip()

    if not new_skill_name:
        flash("Skill name cannot be empty.", "error")
        return redirect(url_for("manage_volunteer_skills"))

    try:
        # Check if the skill already exists in the Skills table
        existing_skill = db.execute("SELECT SkillID FROM Skills WHERE Name = ?", (new_skill_name,)).fetchone()
        
        if existing_skill:
            skill_id = existing_skill["SkillID"]
            flash("This skill already exists. It has been added to your profile.", "info")
        else:
            # If the skill doesn't exist, insert it into the Skills table
            result = db.execute(
                "INSERT INTO Skills (Name, Description) VALUES (?, ?)",
                (new_skill_name, new_skill_description)
            )
            skill_id = result.lastrowid
            flash(f"New skill '{new_skill_name}' created and added to your profile.", "success")

        # Now link the skill to the volunteer
        db.execute(
            "INSERT OR IGNORE INTO VolunteerSkills (VolunteerID, SkillID) VALUES (?, ?)",
            (session["user_id"], skill_id)
        )
        db.commit()

    except sqlite3.Error as e:
        flash(f"An error occurred: {e}", "error")
    
    return redirect(url_for("manage_volunteer_skills"))


@app.route("/volunteer/skills/<int:skill_id>/delete", methods=["POST"])
@login_required
@volunteer_required
def delete_volunteer_skill(skill_id):
    db = get_db()
    db.execute(
        "DELETE FROM VolunteerSkills WHERE VolunteerID = ? AND SkillID = ?",
        (session["user_id"], skill_id)
    )
    db.commit()
    flash("Skill removed.", "success")
    return redirect(url_for("manage_volunteer_skills"))

@app.route("/volunteers/<int:volunteer_id>")
@login_required
def view_volunteer_profile(volunteer_id):
    db = get_db()
    volunteer = db.execute(
        "SELECT VolunteerID, FirstName, LastName, Email, Phone, Address, Availability FROM Volunteers WHERE VolunteerID = ?",
        (volunteer_id,)
    ).fetchone()
    if not volunteer:
        flash("Volunteer not found.", "error")
        return redirect(url_for("list_volunteers"))

    skills = db.execute(
        """SELECT s.Name, s.Description FROM VolunteerSkills vs
           JOIN Skills s ON vs.SkillID = s.SkillID
           WHERE vs.VolunteerID = ?""",
        (volunteer_id,)
    ).fetchall()

    return render_template("view_volunteer_profile.html", volunteer=volunteer, skills=skills)

# ---------- Organisation-Specific Routes ----------
@app.route("/org/account/edit", methods=["GET", "POST"])
@login_required
@org_required
def edit_org_account():
    db = get_db()
    org = db.execute(
        "SELECT * FROM Organisations WHERE OrganisationID=?",
        (session["user_id"],),
    ).fetchone()
    if not org:
        flash("Organisation not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form["name"]
        description = request.form.get("description")
        phone = request.form.get("phone")
        website = request.form.get("website")
        contact_person = request.form.get("contact_person")
        logo = request.form.get("logo")

        db.execute(
            """UPDATE Organisations
               SET Name=?, Description=?, Phone=?, Website=?, ContactPerson=?, Logo=?
               WHERE OrganisationID=?""",
            (name, description, phone, website, contact_person, logo, session["user_id"]),
        )
        db.commit()
        session["name"] = name
        flash("Account updated successfully.", "success")
        return redirect(url_for("organisation_dashboard"))

    return render_template("edit_org_account.html", org=org)

@app.route("/events/<int:event_id>/signups")
@login_required
@org_required
def view_event_signups(event_id):
    db = get_db()
    event = db.execute("SELECT * FROM Events WHERE EventID=? AND OrganisationID=?", (event_id, session["user_id"])).fetchone()
    if not event:
        flash("Event not found or not authorised.", "error")
        return redirect(url_for("list_events"))

    signups = db.execute(
        """SELECT s.SignupID, s.Status, v.VolunteerID, v.FirstName, v.LastName, v.Email, v.Phone
           FROM Signups s
           JOIN Volunteers v ON s.VolunteerID = v.VolunteerID
           WHERE s.EventID = ?""",
        (event_id,)
    ).fetchall()
    return render_template("view_signups.html", event=event, signups=signups)

@app.route("/signups/<int:signup_id>/status", methods=["POST"])
@login_required
@org_required
def update_signup_status(signup_id):
    db = get_db()
    new_status = request.form.get("status")

    # Verify that the signup belongs to an event of the logged-in organisation
    signup = db.execute(
        """SELECT s.SignupID, s.EventID, e.OrganisationID  -- <-- ADDED s.EventID HERE
           FROM Signups s
           JOIN Events e ON s.EventID = e.EventID
           WHERE s.SignupID = ?""",
        (signup_id,)
    ).fetchone()

    if not signup or signup["OrganisationID"] != session["user_id"]:
        flash("Not authorised to change this signup's status.", "error")
        return redirect(url_for("organisation_dashboard"))

    db.execute("UPDATE Signups SET Status = ? WHERE SignupID = ?", (new_status, signup_id))
    db.commit()
    flash(f"Signup status updated to '{new_status}'.", "success")
    return redirect(url_for("view_event_signups", event_id=signup["EventID"]))

# ---------- General Routes (Accessible to both Volunteers and Orgs) ----------
@app.route("/events")
@login_required
def list_events():
    """
    Lists events for both volunteers and organisations.
    Organisations see their own events and others' events separately.
    Volunteers see all events with their signup status.
    """
    db = get_db()
    user_id = session.get('user_id')
    account_type = session.get('account_type')

    if account_type == 'organisation':
        # Fetch events created by the logged-in organisation
        my_events = db.execute(
            """SELECT e.*, o.Name AS OrgName 
               FROM Events e 
               JOIN Organisations o ON e.OrganisationID = o.OrganisationID
               WHERE e.OrganisationID = ? 
               ORDER BY e.Date""",
            (user_id,)
        ).fetchall()

        # Fetch events from other organisations
        other_events = db.execute(
            """SELECT e.*, o.Name AS OrgName 
               FROM Events e 
               JOIN Organisations o ON e.OrganisationID = o.OrganisationID
               WHERE e.OrganisationID != ? 
               ORDER BY e.Date""",
            (user_id,)
        ).fetchall()
        
        return render_template(
            "list_events.html", 
            my_events=my_events, 
            other_events=other_events
        )

    elif account_type == 'volunteer':
        # Fetch all events along with the volunteer's signup status
        events = db.execute(
            """SELECT 
                e.EventID, e.Name, e.Date, e.Location, o.Name AS OrgName, s.Status AS signup_status
               FROM Events e
               JOIN Organisations o ON e.OrganisationID = o.OrganisationID
               LEFT JOIN Signups s ON e.EventID = s.EventID AND s.VolunteerID = ?
               ORDER BY e.Date""",
            (user_id,)
        ).fetchall()
        
        return render_template("list_events.html", events=events)
        
    # If for some reason the account type isn't set, redirect to login
    return redirect(url_for('login'))

@app.route("/organisation/events_full")
@login_required
@org_required
def organisation_events_full():
    """
    Lists all events for an organisation, with modals for detailed view.
    """
    db = get_db()
    my_events = db.execute(
        """SELECT * FROM Events WHERE OrganisationID = ? ORDER BY Date""",
        (session["user_id"],)
    ).fetchall()
    
    other_events = db.execute(
        """SELECT e.*, o.Name AS OrgName 
           FROM Events e 
           JOIN Organisations o ON e.OrganisationID = o.OrganisationID
           WHERE e.OrganisationID != ? 
           ORDER BY e.Date""",
        (session["user_id"],)
    ).fetchall()
    
    return render_template(
        "organisation_events_full.html",
        my_events=my_events,
        other_events=other_events
    )

@app.route("/events/<int:event_id>/signup", methods=["POST"])
@login_required
@volunteer_required
def signup_for_event(event_id):
    db = get_db()
    # Check if the volunteer is already signed up
    existing_signup = db.execute(
        "SELECT 1 FROM Signups WHERE VolunteerID = ? AND EventID = ?",
        (session["user_id"], event_id)
    ).fetchone()

    if existing_signup:
        flash("You are already signed up for this event.", "info")
    else:
        db.execute(
            "INSERT INTO Signups (VolunteerID, EventID, Status) VALUES (?, ?, 'Pending')",
            (session["user_id"], event_id)
        )
        db.commit()
        flash("Successfully signed up for the event! Your status is 'Pending'.", "success")
    return redirect(url_for("list_events"))


@app.route("/events/<int:event_id>/retract_signup", methods=["POST"])
@login_required
@volunteer_required
def retract_signup(event_id):
    db = get_db()
    volunteer_id = session.get('user_id')

    signup = db.execute(
        """SELECT Status FROM Signups WHERE VolunteerID = ? AND EventID = ?""",
        (volunteer_id, event_id)
    ).fetchone()

    if signup and signup['Status'] != 'Accepted':
        db.execute(
            "DELETE FROM Signups WHERE VolunteerID = ? AND EventID = ?",
            (volunteer_id, event_id)
        )
        db.commit()
        flash("Your signup has been retracted.", "success")
    elif signup and signup['Status'] == 'Accepted':
        flash("Cannot retract signup after it has been accepted.", "error")
    else:
        flash("No pending signup found for this event.", "error")
    
    return redirect(url_for('list_events'))

@app.route("/events/<int:event_id>")
@login_required
def view_event(event_id):
    """
    Displays details for a single event, now as a JSON response for modals.
    """
    db = get_db()
    event = db.execute(
        """SELECT e.*, o.Name AS OrgName
           FROM Events e
           JOIN Organisations o ON e.OrganisationID = o.OrganisationID
           WHERE e.EventID = ?""",
        (event_id,)
    ).fetchone()

    if not event:
        # Return a JSON error if the event isn't found
        return jsonify({"error": "Event not found"}), 404

    # Return the event data as a JSON object
    return jsonify({
        "EventID": event["EventID"],
        "Name": event["Name"],
        "OrgName": event["OrgName"],
        "Date": event["Date"],
        "StartTime": event["StartTime"],
        "EndTime": event["EndTime"],
        "Location": event["Location"],
        "Description": event["Description"]
    })

@app.route("/organisations")
@login_required
def list_orgs():
    """
    Lists all organisations, with a special view for organisation users.
    """
    db = get_db()
    
    if session.get('account_type') == 'organisation':
        # Fetch the logged-in organisation's details
        my_org = db.execute(
            """SELECT OrganisationID, Name, Description, Email, Phone, Website, ContactPerson
               FROM Organisations WHERE OrganisationID = ?""",
            (session['user_id'],)
        ).fetchone()

        # Fetch all other organisations
        other_orgs = db.execute(
            """SELECT OrganisationID, Name, Description, Email, Phone, Website, ContactPerson
               FROM Organisations WHERE OrganisationID != ?""",
            (session['user_id'],)
        ).fetchall()

        return render_template("list_orgs.html", my_org=my_org, other_orgs=other_orgs)
    
    else:
        # For volunteers or other users, fetch all organisations
        all_orgs = db.execute(
            "SELECT OrganisationID, Name, Description, Email, Phone, Website, ContactPerson FROM Organisations"
        ).fetchall()
        return render_template("list_orgs.html", all_orgs=all_orgs)

@app.route("/organisations/<int:org_id>")
@login_required
def view_org(org_id):
    """
    Returns the details of a single organisation as a JSON object.
    """
    db = get_db()
    org = db.execute(
        """SELECT OrganisationID, Name, Description, Email, Phone, Website, ContactPerson
           FROM Organisations WHERE OrganisationID = ?""",
        (org_id,)
    ).fetchone()
    
    if not org:
        return jsonify({"error": "Organisation not found"}), 404

    # Return the organisation data as a JSON object
    return jsonify({
        "OrganisationID": org["OrganisationID"],
        "Name": org["Name"],
        "Description": org["Description"],
        "Email": org["Email"],
        "Phone": org["Phone"],
        "Website": org["Website"],
        "ContactPerson": org["ContactPerson"]
    })

@app.route("/volunteers")
@login_required
def list_volunteers():
    db = get_db()
    search_query = request.args.get('q', '')
    
    query = """
        SELECT 
            V.VolunteerID, 
            V.FirstName, 
            V.LastName, 
            V.Email, 
            V.Phone, 
            V.Availability,
            GROUP_CONCAT(S.Name) AS Skills
        FROM 
            Volunteers V
        LEFT JOIN 
            VolunteerSkills VS ON V.VolunteerID = VS.VolunteerID
        LEFT JOIN 
            Skills S ON VS.SkillID = S.SkillID
    """
    params = []

    if search_query:
        query += " WHERE S.Name LIKE ?"
        params.append('%' + search_query + '%')

    query += " GROUP BY V.VolunteerID ORDER BY V.FirstName"
    
    volunteers = db.execute(query, params).fetchall()

    return render_template("list_volunteers.html", volunteers=volunteers, query=search_query)

# ---------- Event Routes ----------
@app.route("/events/add", methods=["GET", "POST"])
@login_required
@org_required
def add_event():
    if request.method == "POST":
        db = get_db()
        db.execute(
            """INSERT INTO Events 
               (OrganisationID, Name, Description, Date, StartTime, EndTime, Location)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                session["user_id"],
                request.form["name"],
                request.form.get("description"),
                request.form.get("date"),
                request.form.get("start_time"),
                request.form.get("end_time"),
                request.form.get("location"),
            )
        )
        db.commit()
        flash("Event created.", "success")
        return redirect(url_for("list_events"))
    return render_template("add_event.html")

@app.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
@org_required
def edit_event(event_id):
    db = get_db()
    event = db.execute("SELECT * FROM Events WHERE EventID=? AND OrganisationID=?", (event_id, session["user_id"])).fetchone()
    if not event:
        flash("Not authorised.", "error")
        return redirect(url_for("list_events"))

    if request.method == "POST":
        db.execute(
            """UPDATE Events
               SET Name=?, Description=?, Date=?, Location=?, StartTime=?, EndTime=?
               WHERE EventID=? AND OrganisationID=?""",
            (
                request.form["name"],
                request.form.get("description"),
                request.form.get("date"),
                request.form.get("location"),
                request.form.get("start_time"),
                request.form.get("end_time"),
                event_id,
                session["user_id"]
            )
        )
        db.commit()
        flash("Event updated.", "success")
        return redirect(url_for("list_events"))

    return render_template("edit_event.html", event=event)

@app.route("/events/<int:event_id>/delete", methods=["POST"])
@login_required
@org_required
def delete_event(event_id):
    db = get_db()
    db.execute("DELETE FROM Events WHERE EventID=? AND OrganisationID=?", (event_id, session["user_id"]))
    db.commit()
    flash("Event deleted.", "success")
    return redirect(url_for("list_events"))

# ---------- Main ----------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)