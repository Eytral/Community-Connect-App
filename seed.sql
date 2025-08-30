-- -----------------------------
-- Organisations
-- -----------------------------
INSERT INTO Organisations (Name, Description, ContactPerson, Email, Password, Phone, Address, Website, Logo) VALUES
('Helping Hands', 'A charity focused on food distribution', 'Alice Smith', 'alice@helpinghands.org', 'password123', '1234567890', '123 Elm St', 'https://www.helpinghands.org', 'logo1.png'),
('Green Earth', 'Environmental protection group', 'Bob Johnson', 'bob@greenearth.org', 'securepass', '0987654321', '456 Oak Ave', 'https://www.greenearth.org', 'logo2.png'),
('Youth Helpers', 'Youth volunteer network', 'Charlie Davis', 'charlie@youthhelpers.org', 'youthpass', '1112223333', '789 Birch St', 'https://www.youthhelpers.org', 'logo3.png'),
('Animal Rescue', 'Animal welfare and rescue', 'Diana Evans', 'diana@animalrescue.org', 'animalpass', '2223334444', '321 Willow Rd', 'https://www.animalrescue.org', 'logo4.png');

-- -----------------------------
-- Volunteers
-- -----------------------------
INSERT INTO Volunteers (FirstName, LastName, Email, Password, Phone, Address, DateOfBirth, Availability, ProfilePhoto, EmergencyContact) VALUES
('John', 'Doe', 'john@example.com', 'pass123', '5551234567', '789 Pine Rd', '1990-05-14', '1', 'john.jpg', '5559870001'),
('Emma', 'Brown', 'emma@example.com', 'pass456', '5559876543', '101 Maple Ln', '1995-08-20', '1', 'emma.png', '5551230002'),
('Liam', 'Smith', 'liam@example.com', 'liampass', '5551112222', '202 Birch Ln', '1992-03-12', '0', 'liam.jpg', '5553330003'),
('Sophia', 'Taylor', 'sophia@example.com', 'sophiapass', '5553334444', '303 Cedar St', '1998-07-25', '1', 'sophia.png', '5554440004'),
('Noah', 'Wilson', 'noah@example.com', 'noahpass', '5555556666', '404 Spruce Rd', '1991-11-30', '1', 'noah.jpg', '5555550005'),
('Olivia', 'Martinez', 'olivia@example.com', 'oliviapass', '5557778888', '505 Fir St', '1993-02-18', '1', 'olivia.png', '5556660006'),
('Ava', 'Garcia', 'ava@example.com', 'avapass', '5559990000', '606 Walnut Ave', '1996-09-05', '1', 'ava.jpg', '5557770007'),
('Isabella', 'Lee', 'isabella@example.com', 'isabellapass', '5552223333', '707 Cherry Ln', '1994-12-22', '0', 'isabella.png', '5558880008'),
('Mia', 'Harris', 'mia@example.com', 'miapass', '5554445555', '808 Poplar Rd', '1997-06-11', '1', 'mia.jpg', '5559990009'),
('Ethan', 'Clark', 'ethan@example.com', 'ethanpass', '5556667777', '909 Pine St', '1990-01-28', '1', 'ethan.png', '5551110010'),
('Lucas', 'Young', 'lucas@example.com', 'lucaspass', '5558889999', '1010 Maple St', '1992-10-10', '0', 'lucas.jpg', '5552220011'),
('Charlotte', 'King', 'charlotte@example.com', 'charlottepass', '5551011121', '1111 Oak St', '1995-03-03', '1', 'charlotte.png', '5553330012'),
('Amelia', 'Wright', 'amelia@example.com', 'ameliapass', '5551213141', '1212 Birch St', '1993-07-14', '1', 'amelia.jpg', '5554440013'),
('James', 'Scott', 'james@example.com', 'jamespass', '5551415161', '1313 Cedar Ln', '1991-05-05', '0', 'james.png', '5555550014'),
('Benjamin', 'Adams', 'benjamin@example.com', 'benjaminpass', '5551617181', '1414 Spruce Ave', '1996-11-11', '1', 'benjamin.jpg', '5556660015');

-- -----------------------------
-- Roles
-- -----------------------------
INSERT INTO Roles (Name, Description) VALUES
('Organizer', 'Manages the event operations'),
('Helper', 'Assists with various tasks'),
('Coordinator', 'Coordinates between volunteers and organisation'),
('Volunteer Lead', 'Leads a group of volunteers'),
('Photographer', 'Captures photos for events'),
('Logistics', 'Handles logistics and supplies');

-- -----------------------------
-- Skills
-- -----------------------------
INSERT INTO Skills (Name, Description) VALUES
('First Aid', 'Ability to provide first aid assistance'),
('Cooking', 'Preparing food for events'),
('Event Management', 'Planning and organizing events'),
('Photography', 'Skill in taking event photos'),
('Logistics Management', 'Organizing transport and supplies'),
('Teaching', 'Ability to teach or tutor others');

-- -----------------------------
-- Events
-- -----------------------------
INSERT INTO Events (OrganisationID, Name, Description, Date, StartTime, EndTime, Location, Status) VALUES
(1, 'Food Drive', 'Distributing food to the needy', '2025-09-10', '09:00:00', '14:00:00', 'Community Center', 'Planned'),
(2, 'Tree Plantation', 'Planting trees in the park', '2025-09-15', '08:00:00', '12:00:00', 'City Park', 'Planned'),
(3, 'Park Clean-Up', 'Cleaning up the local park', '2025-09-20', '10:00:00', '13:00:00', 'Central Park', 'Planned'),
(4, 'Pet Adoption Fair', 'Facilitating pet adoptions', '2025-09-25', '09:00:00', '15:00:00', 'Community Hall', 'Planned'),
(1, 'Soup Kitchen', 'Serving meals to homeless', '2025-09-30', '11:00:00', '16:00:00', 'Shelter', 'Planned'),
(2, 'Beach Cleanup', 'Cleaning the beach area', '2025-10-05', '07:00:00', '11:00:00', 'Sunny Beach', 'Planned'),
(3, 'Youth Workshop', 'Educational workshop for youths', '2025-10-10', '13:00:00', '17:00:00', 'Youth Center', 'Planned'),
(4, 'Animal Vaccination Camp', 'Vaccination for stray animals', '2025-10-15', '09:00:00', '14:00:00', 'Animal Shelter', 'Planned');

-- -----------------------------
-- VolunteerSkills
-- -----------------------------
INSERT INTO VolunteerSkills (VolunteerID, SkillID) VALUES
(1,1),(1,3),(2,2),(3,4),(3,5),(4,6),(5,1),(5,2),(6,3),(6,4),
(7,5),(7,2),(8,1),(8,6),(9,3),(9,4),(10,5),(10,2),(11,1),(11,6),
(12,2),(12,4),(13,3),(13,5),(14,1),(14,6),(15,2),(15,5);

-- -----------------------------
-- EventSkills
-- -----------------------------
INSERT INTO EventSkills (EventID, SkillID) VALUES
(1,2),(1,1),(2,3),(3,2),(3,5),(4,4),(4,6),(5,2),(5,1),(6,3),
(6,5),(7,6),(7,3),(8,1),(8,4);

-- -----------------------------
-- Signups
-- -----------------------------
INSERT INTO Signups (EventID, VolunteerID, RoleID, Status) VALUES
(1,1,2,'Confirmed'),(1,2,1,'Pending'),
(2,2,3,'Confirmed'),(2,3,4,'Confirmed'),
(3,3,4,'Confirmed'),(3,5,5,'Pending'),
(4,4,2,'Confirmed'),(4,3,6,'Confirmed'),
(5,6,1,'Confirmed'),(5,7,2,'Pending'),
(6,8,3,'Confirmed'),(6,9,4,'Confirmed'),
(7,10,5,'Pending'),(7,11,6,'Confirmed'),
(8,12,1,'Confirmed'),(8,13,2,'Pending'),
(1,14,3,'Confirmed'),(2,15,4,'Confirmed');
