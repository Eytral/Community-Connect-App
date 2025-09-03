-- Drop tables if exist (reverse order of dependencies)
DROP TABLE IF EXISTS Signups;
DROP TABLE IF EXISTS EventSkills;
DROP TABLE IF EXISTS VolunteerSkills;
DROP TABLE IF EXISTS Events;
DROP TABLE IF EXISTS Organisations;
DROP TABLE IF EXISTS Volunteers;
DROP TABLE IF EXISTS Roles;
DROP TABLE IF EXISTS Skills;

-- Organisations Table
CREATE TABLE Organisations (
    OrganisationID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Description TEXT,
    ContactPerson TEXT,
    Email TEXT UNIQUE,
    Password TEXT,
    Phone TEXT,
    Address TEXT,
    Website TEXT,
    Logo TEXT
);

-- Volunteers Table
CREATE TABLE Volunteers (
    VolunteerID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    Email TEXT UNIQUE,
    Password TEXT,
    Phone TEXT,
    Address TEXT,
    DateOfBirth DATE,
    Availability BOOLEAN,
    ProfilePhoto TEXT,
    EmergencyContact TEXT
);

-- Roles Table
CREATE TABLE Roles (
    RoleID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Description TEXT
);

-- Skills Table
CREATE TABLE Skills (
    SkillID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Description TEXT
);

-- Events Table
CREATE TABLE Events (
    EventID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrganisationID INTEGER,
    Name TEXT NOT NULL,
    Description TEXT,
    Date DATE,
    StartTime TIME,
    EndTime TIME,
    Location TEXT,
    Status TEXT,
    FOREIGN KEY (OrganisationID) REFERENCES Organisations(OrganisationID)
    CONSTRAINT chk_end_after_start CHECK (end_time > start_time)
);

-- VolunteerSkills (Many-to-Many Volunteers <> Skills)
CREATE TABLE VolunteerSkills (
    VolunteerID INTEGER,
    SkillID INTEGER,
    PRIMARY KEY (VolunteerID, SkillID),
    FOREIGN KEY (VolunteerID) REFERENCES Volunteers(VolunteerID) ON DELETE CASCADE,
    FOREIGN KEY (SkillID) REFERENCES Skills(SkillID) ON DELETE CASCADE
);

-- EventSkills (Many-to-Many Events <> Skills)
CREATE TABLE EventSkills (
    EventID INTEGER,
    SkillID INTEGER,
    PRIMARY KEY (EventID, SkillID),
    FOREIGN KEY (EventID) REFERENCES Events(EventID) ON DELETE CASCADE,
    FOREIGN KEY (SkillID) REFERENCES Skills(SkillID) ON DELETE CASCADE
);

-- Signups Table (Many-to-Many Volunteers <> Events with Roles)
CREATE TABLE Signups (
    SignupID INTEGER PRIMARY KEY AUTOINCREMENT,
    EventID INTEGER,
    VolunteerID INTEGER,
    RoleID INTEGER,
    Status TEXT,
    FOREIGN KEY (EventID) REFERENCES Events(EventID) ON DELETE CASCADE,
    FOREIGN KEY (VolunteerID) REFERENCES Volunteers(VolunteerID) ON DELETE CASCADE,
    FOREIGN KEY (RoleID) REFERENCES Roles(RoleID) ON DELETE CASCADE
);
