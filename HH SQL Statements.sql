CREATE TABLE hotel(  /*Creating table to store hotel data */
    hotelid int NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT 'Primary Key',
    hotelLoc VARCHAR(25) NOT NULL COMMENT 'Hotel Location', 
    stdRoomPrice DOUBLE NOT NULL COMMENT 'Room price off peak',
    stdRoomPeakPrice DOUBLE NOT NULL COMMENT 'Room price on peak',
    capacity INT NOT NULL COMMENT 'Total Room Capacity'
) DEFAULT CHARSET UTF8 COMMENT '';

INSERT INTO hotel /*Inserting relevant data into the hotel table */
(
    hotelLoc, 
    stdRoomPrice,
    stdRoomPeakPrice,
    capacity
)
VALUES 
('Aberdeen','60','140','80'),
('Belfast','60','130','80'),
('Birmingham','70','150','90'),
('Bristol','70','140','90'),
('Cardiff','60','120','80'),
('Edinburgh','70','160','90'),
('Glasgow','70','150','100'),
('London','80','200','120'),
('Manchester','80','180','110'),
('Newcastle','60','100','80'),
('Norwich','60','100','80'),
('Nottingham','70','120','100'),
('Oxford','70','180','80'),
('Plymouth','50','180','80'),
('Swansea','50','120','80');

/*Creating user table */
CREATE TABLE account(  /*Creating table to store account data */
    accountId int NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT 'Primary Key for account',
    email VARCHAR(255) UNIQUE NOT NULL COMMENT 'User email', 
    accPassword VARCHAR(255) NOT NULL COMMENT 'User password',
    firstName VARCHAR(255) NOT NULL COMMENT 'User first name',
    lastName VARCHAR(255) NOT NULL COMMENT 'User last name',
    userType VARCHAR(3) NOT NULL DEFAULT 'std' COMMENT 'User type, defaults to standard user or std. Admin manaully added.'
) DEFAULT CHARSET UTF8 COMMENT '';

INSERT INTO account /*Filling account table */
(
    email,
    accPassword,
    firstName,
    lastName,
    phoneNo,
    userType
)
VALUES /*Creating an admin account to use in the website with some filler values*/
('admin@admin.com','admin123','admin','admin','123','adm');

CREATE TABLE Booking( /*Creating a table for booking information*/
    bookingNumber INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'The booking number',
    bookingStart DATE NOT NULL COMMENT 'The start date of the users booking',
    bookingEnd DATE NOT NULL COMMENT 'The end date of the users booking',
    bookingCreationDate DATETIME NOT NULL COMMENT 'When the user created their booking',
    roomType VARCHAR(10) NOT NULL COMMENT 'The room type the user booked',
    cardNum VARCHAR(4) NOT NULL UNIQUE COMMENT 'The card number of the user',
    hotelId INT,
    accountId INT,
    FOREIGN KEY (hotelId) REFERENCES hotel(hotelId) ON DELETE CASCADE, /*Creating a foreign key of Hotel id to know which hotel the booking was created in */
    FOREIGN KEY (accountId) REFERENCES account(accountId) ON DELETE CASCADE /*Creating a foreign key for accountId to know which account it is linked to*/
)DEFAULT CHARSET UTF8 COMMENT '';

