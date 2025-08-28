-- Drop old tables (for development resets)
DROP TABLE IF EXISTS VolunteerSkills;
DROP TABLE IF EXISTS VolunteerEvents;
DROP TABLE IF EXISTS Skills;
DROP TABLE IF EXISTS Signups;
DROP TABLE IF EXISTS Events;
DROP TABLE IF EXISTS Organisations;
DROP TABLE IF EXISTS Volunteers;

-- -------------------------
-- Volunteers
-- -------------------------
CREATE TABLE Volunteers (
    VolunteerID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Phone TEXT,
    Address TEXT,
    DateOfBirth TEXT,
    Availability TEXT,
    ProfilePhoto TEXT,
    EmergencyContact TEXT
);

-- -------------------------
-- Skills
-- -------------------------
CREATE TABLE Skills (
    SkillID INTEGER PRIMARY KEY AUTOINCREMENT,
    SkillName TEXT NOT NULL,
    SkillDescription TEXT
);

-- -------------------------
-- VolunteerSkills (M:N Volunteers <-> Skills)
-- -------------------------
CREATE TABLE VolunteerSkills (
    VolunteerID INTEGER NOT NULL,
    SkillID INTEGER NOT NULL,
    PRIMARY KEY (VolunteerID, SkillID),
    FOREIGN KEY (VolunteerID) REFERENCES Volunteers(VolunteerID),
    FOREIGN KEY (SkillID) REFERENCES Skills(SkillID)
);

-- -------------------------
-- Organisations
-- -------------------------
CREATE TABLE Organisations (
    OrganisationID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Address TEXT,
    Phone TEXT,
    Email TEXT
);

-- -------------------------
-- Events
-- -------------------------
CREATE TABLE Events (
    EventID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    Date TEXT,
    Location TEXT,
    OrganisationID INTEGER NOT NULL,
    FOREIGN KEY (OrganisationID) REFERENCES Organisations(OrganisationID)
);

-- -------------------------
-- VolunteerEvents (M:N Volunteers <-> Events)
-- -------------------------
CREATE TABLE VolunteerEvents (
    VolunteerID INTEGER NOT NULL,
    EventID INTEGER NOT NULL,
    PRIMARY KEY (VolunteerID, EventID),
    FOREIGN KEY (VolunteerID) REFERENCES Volunteers(VolunteerID),
    FOREIGN KEY (EventID) REFERENCES Events(EventID)
);

-- -------------------------
-- Signups (alternative to VolunteerEvents, matches your Flask app)
-- -------------------------
CREATE TABLE Signups (
    SignupID INTEGER PRIMARY KEY AUTOINCREMENT,
    VolunteerID INTEGER NOT NULL,
    EventID INTEGER NOT NULL,
    FOREIGN KEY (VolunteerID) REFERENCES Volunteers(VolunteerID),
    FOREIGN KEY (EventID) REFERENCES Events(EventID)
);
