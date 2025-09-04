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
    Name TEXT(100) NOT NULL,
    Description TEXT(255),
    ContactPerson TEXT(50),
    Email TEXT(320) UNIQUE NOT NULL,
    Password TEXT(128) NOT NULL,
    Phone TEXT(32),
    Address TEXT(255),
    Website TEXT(255),
    Logo BLOB
);

-- Volunteers Table
CREATE TABLE Volunteers (
    VolunteerID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName TEXT(20) NOT NULL,
    LastName TEXT(20) NOT NULL,
    Email TEXT(320) UNIQUE NOT NULL,
    Password TEXT(128) NOT NULL,
    Phone TEXT(32),
    Address TEXT(255),
    DateOfBirth DATE,
    Availability BOOLEAN,
    ProfilePhoto BLOB,
    EmergencyContact TEXT(32)
);

-- Roles Table
CREATE TABLE Roles (
    RoleID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT(50) NOT NULL,
    Description TEXT(255)
);

-- Skills Table
CREATE TABLE Skills (
    SkillID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT(50) NOT NULL,
    Description TEXT(255)
);

-- Events Table
CREATE TABLE Events (
    EventID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrganisationID INTEGER NOT NULL,
    Name TEXT(100) NOT NULL,
    Description TEXT(255),
    Date DATE,
    StartTime TIME,
    EndTime TIME,
    Location TEXT(255),
    Status TEXT(20),
    FOREIGN KEY (OrganisationID) REFERENCES Organisations(OrganisationID),
    CONSTRAINT chk_end_after_start CHECK (EndTime > StartTime)
);

-- VolunteerSkills (Many-to-Many Volunteers <> Skills)
CREATE TABLE VolunteerSkills (
    VolunteerID INTEGER NOT NULL,
    SkillID INTEGER NOT NULL,
    PRIMARY KEY (VolunteerID, SkillID),
    FOREIGN KEY (VolunteerID) REFERENCES Volunteers(VolunteerID) ON DELETE CASCADE,
    FOREIGN KEY (SkillID) REFERENCES Skills(SkillID) ON DELETE CASCADE
);

-- EventSkills (Many-to-Many Events <> Skills)
CREATE TABLE EventSkills (
    EventID INTEGER NOT NULL,
    SkillID INTEGER NOT NULL,
    PRIMARY KEY (EventID, SkillID),
    FOREIGN KEY (EventID) REFERENCES Events(EventID) ON DELETE CASCADE,
    FOREIGN KEY (SkillID) REFERENCES Skills(SkillID) ON DELETE CASCADE
);

-- Signups Table (Many-to-Many Volunteers <> Events with Roles)
CREATE TABLE Signups (
    SignupID INTEGER PRIMARY KEY AUTOINCREMENT,
    EventID INTEGER NOT NULL,
    VolunteerID INTEGER NOT NULL,
    RoleID INTEGER,
    Status TEXT(20),
    FOREIGN KEY (EventID) REFERENCES Events(EventID) ON DELETE CASCADE,
    FOREIGN KEY (VolunteerID) REFERENCES Volunteers(VolunteerID) ON DELETE CASCADE,
    FOREIGN KEY (RoleID) REFERENCES Roles(RoleID) ON DELETE SET NULL
);
