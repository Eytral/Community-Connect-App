from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import os

app = Flask(__name__)
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
    with app.app_context():
        db = get_db()
        with open("schema.sql", "r") as f:
            db.executescript(f.read())
        if os.path.exists("seed.sql"):
            with open("seed.sql", "r") as f:
                db.executescript(f.read())
        db.commit()


# ---------- Routes ----------

@app.route("/")
def index():
    return render_template("index.html")

# --- Volunteers ---
@app.route("/volunteers")
def list_volunteers():
    db = get_db()
    volunteers = db.execute("SELECT * FROM Volunteers").fetchall()
    return render_template("volunteers.html", volunteers=volunteers)

@app.route("/volunteers/add", methods=["GET", "POST"])
def add_volunteer():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO Volunteers (FirstName, LastName, Email, Phone, Address, DateOfBirth, Availability) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                request.form["FirstName"],
                request.form["LastName"],
                request.form["Email"],
                request.form["Phone"],
                request.form["Address"],
                request.form["DateOfBirth"],
                request.form["Availability"],
            ),
        )
        db.commit()
        return redirect(url_for("list_volunteers"))
    return render_template("add_volunteer.html")

@app.route("/volunteers/<int:id>/edit", methods=["GET", "POST"])
def update_volunteer(id):
    db = get_db()
    volunteer = db.execute("SELECT * FROM Volunteers WHERE VolunteerID=?", (id,)).fetchone()
    if request.method == "POST":
        db.execute(
            """UPDATE Volunteers 
               SET FirstName=?, LastName=?, Email=?, Phone=?, Address=?, DateOfBirth=?, Availability=? 
               WHERE VolunteerID=?""",
            (
                request.form["FirstName"],
                request.form["LastName"],
                request.form["Email"],
                request.form["Phone"],
                request.form["Address"],
                request.form["DateOfBirth"],
                request.form["Availability"],
                id
            )
        )
        db.commit()
        return redirect(url_for("list_volunteers"))
    return render_template("update_volunteer.html", volunteer=volunteer)



# --- Organisations ---
@app.route("/organisations")
def list_orgs():
    db = get_db()
    orgs = db.execute("SELECT * FROM Organisations").fetchall()
    return render_template("organisations.html", orgs=orgs)

@app.route("/organisations/add", methods=["GET", "POST"])
def add_org():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO Organisations (Name, Address, Phone, Email) VALUES (?, ?, ?, ?)",
            (
                request.form["Name"],
                request.form["Address"],
                request.form["Phone"],
                request.form["Email"],
            ),
        )
        db.commit()
        return redirect(url_for("list_orgs"))
    return render_template("add_org.html")

# --- Events ---
@app.route("/events")
def list_events():
    db = get_db()
    events = db.execute(
        "SELECT e.EventID, e.Title, e.Date, e.Location, o.Name AS OrgName "
        "FROM Events e JOIN Organisations o ON e.OrganisationID = o.OrganisationID"
    ).fetchall()
    return render_template("events.html", events=events)

@app.route("/events/add", methods=["GET", "POST"])
def add_event():
    db = get_db()
    orgs = db.execute("SELECT * FROM Organisations").fetchall()
    if request.method == "POST":
        db.execute(
            "INSERT INTO Events (Title, Date, Location, OrganisationID) VALUES (?, ?, ?, ?)",
            (
                request.form["Title"],
                request.form["Date"],
                request.form["Location"],
                request.form["OrganisationID"],
            ),
        )
        db.commit()
        return redirect(url_for("list_events"))
    return render_template("add_event.html", orgs=orgs)

@app.route("/events/delete/<int:id>", methods=["POST"])
def delete_event(id):
    db = get_db()
    db.execute("DELETE FROM Events WHERE EventID=?", (id,))
    db.commit()
    return redirect(url_for("list_events"))

# --- Signups ---
@app.route("/signups")
def list_signups():
    db = get_db()
    signups = db.execute(
        "SELECT s.SignupID, v.FirstName || ' ' || v.LastName AS VolunteerName, "
        "e.Title AS EventTitle "
        "FROM Signups s "
        "JOIN Volunteers v ON s.VolunteerID = v.VolunteerID "
        "JOIN Events e ON s.EventID = e.EventID"
    ).fetchall()
    return render_template("signups.html", signups=signups)

@app.route("/signups/add", methods=["GET", "POST"])
def add_signup():
    db = get_db()
    volunteers = db.execute("SELECT * FROM Volunteers").fetchall()
    events = db.execute("SELECT * FROM Events").fetchall()
    if request.method == "POST":
        db.execute(
            "INSERT INTO Signups (VolunteerID, EventID) VALUES (?, ?)",
            (request.form["VolunteerID"], request.form["EventID"]),
        )
        db.commit()
        return redirect(url_for("list_signups"))
    return render_template("add_signup.html", volunteers=volunteers, events=events)

@app.route("/signups/delete/<int:id>", methods=["POST"])
def delete_signup(id):
    db = get_db()
    db.execute("DELETE FROM Signups WHERE SignupID=?", (id,))
    db.commit()
    return redirect(url_for("list_signups"))

# ---------- Main ----------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
