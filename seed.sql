-- -------------------------
-- Volunteers
-- -------------------------
INSERT INTO Volunteers (FirstName, LastName, Email, Phone, Address, DateOfBirth, Availability, ProfilePhoto, EmergencyContact)
VALUES 
('Alice', 'Smith', 'alice@example.com', '12345678', '123 Main St', '1990-05-01', 'Weekends', '', 'Bob Smith'),
('Bob', 'Johnson', 'bob@example.com', '87654321', '456 Oak St', '1985-11-12', 'Weekdays', '', 'Alice Johnson'),
('Charlie', 'Brown', 'charlie@example.com', '55555555', '789 Pine St', '1992-07-20', 'Evenings', '', 'David Brown');

-- -------------------------
-- Skills
-- -------------------------
INSERT INTO Skills (SkillName, SkillDescription)
VALUES
('First Aid', 'Certified in first aid techniques'),
('Cooking', 'Can cook meals for events'),
('Event Planning', 'Experience organizing events');

-- -------------------------
-- VolunteerSkills
-- -------------------------
INSERT INTO VolunteerSkills (VolunteerID, SkillID)
VALUES
(1, 1),
(1, 3),
(2, 2),
(3, 1),
(3, 2);

-- -------------------------
-- Organisations
-- -------------------------
INSERT INTO Organisations (Name, Address, Phone, Email)
VALUES
('Helping Hands', '12 Charity Rd', '11122233', 'contact@helpinghands.org'),
('Food for All', '34 Community Ave', '44455566', 'info@foodforall.org');

-- -------------------------
-- Events
-- -------------------------
INSERT INTO Events (Title, Date, Location, OrganisationID)
VALUES
('Community Clean-Up', '2025-09-05', 'Central Park', 1),
('Charity Bake Sale', '2025-09-12', 'Community Center', 2);

-- -------------------------
-- VolunteerEvents
-- -------------------------
INSERT INTO VolunteerEvents (VolunteerID, EventID)
VALUES
(1, 1),
(2, 2),
(3, 1),
(3, 2);

-- -------------------------
-- Signups
-- -------------------------
INSERT INTO Signups (VolunteerID, EventID)
VALUES
(1, 1),
(2, 2),
(3, 1);
