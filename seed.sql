-- ============================
-- EXTENDED SEED DATA
-- ============================

-- Clear existing data (respecting FK order)
DELETE FROM Signups;
DELETE FROM EventSkills;
DELETE FROM VolunteerSkills;
DELETE FROM Events;
DELETE FROM Organisations;
DELETE FROM Volunteers;
DELETE FROM Roles;
DELETE FROM Skills;

-- Insert Organisations
INSERT INTO Organisations (Name, Description, ContactPerson, Email, Password, Phone, Address, Website, Logo)
VALUES 
('Helping Hands', 'Non-profit focused on community outreach and events.', 'Alice Johnson', 'contact@helpinghands.org', 'hashed_pw1', '555-1234', '123 Main St', 'https://helpinghands.org', NULL),
('Green Earth', 'Organisation dedicated to environmental conservation.', 'Bob Smith', 'info@greenearth.org', 'hashed_pw2', '555-5678', '456 Forest Rd', 'https://greenearth.org', NULL),
('Food For All', 'Charity focused on providing meals to the homeless.', 'Maria Lopez', 'support@foodforall.org', 'hashed_pw3', '555-8765', '22 Market St', 'https://foodforall.org', NULL),
('Tech Volunteers', 'Organisation connecting volunteers with IT skills to NGOs.', 'David Chen', 'admin@techvolunteers.org', 'hashed_pw4', '555-1212', '900 Tech Ave', 'https://techvolunteers.org', NULL);

-- Insert Volunteers
INSERT INTO Volunteers (FirstName, LastName, Email, Password, Phone, Address, DateOfBirth, Availability, ProfilePhoto, EmergencyContact)
VALUES
('John', 'Doe', 'john.doe@email.com', 'hashed_pw5', '555-7890', '789 Pine St', '1990-05-14', 1, NULL, '555-1111'),
('Emma', 'Brown', 'emma.brown@email.com', 'hashed_pw6', '555-2222', '321 Oak Ave', '1995-09-20', 0, NULL, '555-3333'),
('Liam', 'Nguyen', 'liam.nguyen@email.com', 'hashed_pw7', '555-4444', '987 Cedar Blvd', '1988-12-02', 1, NULL, '555-5555'),
('Sophia', 'Khan', 'sophia.khan@email.com', 'hashed_pw8', '555-6666', '12 River St', '1993-03-08', 1, NULL, '555-7777'),
('Ethan', 'Wong', 'ethan.wong@email.com', 'hashed_pw9', '555-8888', '33 Ocean Dr', '2000-11-15', 1, NULL, '555-9999');

-- Insert Roles
INSERT INTO Roles (Name, Description)
VALUES
('Team Leader', 'Responsible for managing a group of volunteers.'),
('Helper', 'General assistance role.'),
('Medical Aid', 'Provides first aid and health-related support.'),
('Cook', 'Prepares and serves meals.'),
('Technical Support', 'Helps set up and troubleshoot technical systems.');

-- Insert Skills
INSERT INTO Skills (Name, Description)
VALUES
('First Aid', 'Basic first aid and CPR knowledge.'),
('Cooking', 'Ability to prepare and serve meals.'),
('Event Management', 'Organising and coordinating events.'),
('IT Support', 'Technical troubleshooting and setup.'),
('Logistics', 'Managing supplies, transport, and resources.');

-- Insert Events
INSERT INTO Events (OrganisationID, Name, Description, Date, StartTime, EndTime, Location, Status)
VALUES
(1, 'Community Clean-up', 'Neighborhood clean-up event.', '2025-09-15', '09:00', '12:00', 'Central Park', 'Upcoming'),
(2, 'Tree Planting Drive', 'Planting trees to promote sustainability.', '2025-10-01', '08:30', '11:30', 'Riverside Grounds', 'Upcoming'),
(3, 'Soup Kitchen', 'Serving hot meals to the homeless.', '2025-09-20', '11:00', '14:00', 'Downtown Shelter', 'Upcoming'),
(4, 'NGO Tech Fair', 'Tech workshops for non-profits.', '2025-11-05', '10:00', '16:00', 'Tech Hub', 'Upcoming'),
(1, 'Fundraising Gala', 'Annual dinner to raise funds.', '2025-12-10', '18:00', '22:00', 'City Hall', 'Planned');

-- Insert VolunteerSkills
INSERT INTO VolunteerSkills (VolunteerID, SkillID)
VALUES
(1, 1), (1, 3),        -- John: First Aid, Event Management
(2, 2),                -- Emma: Cooking
(3, 1), (3, 2),        -- Liam: First Aid, Cooking
(4, 4), (4, 5),        -- Sophia: IT Support, Logistics
(5, 2), (5, 5);        -- Ethan: Cooking, Logistics

-- Insert EventSkills
INSERT INTO EventSkills (EventID, SkillID)
VALUES
(1, 1), (1, 3),        -- Clean-up: First Aid + Event Mgmt
(2, 2), (2, 3),        -- Tree Planting: Cooking + Event Mgmt
(3, 2), (3, 5),        -- Soup Kitchen: Cooking + Logistics
(4, 4), (4, 3),        -- Tech Fair: IT Support + Event Mgmt
(5, 3), (5, 5);        -- Gala: Event Mgmt + Logistics

-- Insert Signups
INSERT INTO Signups (EventID, VolunteerID, RoleID, Status)
VALUES
(1, 1, 1, 'Confirmed'),   -- John = Team Leader for Clean-up
(1, 2, 2, 'Pending'),     -- Emma = Helper for Clean-up
(2, 3, 3, 'Confirmed'),   -- Liam = Medical Aid for Tree Planting
(2, 5, 2, 'Confirmed'),   -- Ethan = Helper for Tree Planting
(3, 2, 4, 'Confirmed'),   -- Emma = Cook for Soup Kitchen
(3, 4, NULL, 'Pending'),  -- Sophia = signed up, role TBD (edge case: nullable RoleID)
(4, 4, 5, 'Confirmed'),   -- Sophia = Tech Support at Tech Fair
(5, 1, 1, 'Confirmed'),   -- John = Team Leader for Gala
(5, 3, 2, 'Confirmed');   -- Liam = Helper for Gala
