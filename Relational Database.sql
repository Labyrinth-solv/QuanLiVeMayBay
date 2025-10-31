-- Max Needle

-- Queries to create tables and a view
create table Airport
	(name		varchar(30),
	 city		varchar(30),
	 primary key (name)
	);

create table Airline
	(name		varchar(30),
	 primary key (name)
	);

create table Airplane
	(name		varchar(30),
	 ID			numeric(30),
	 seats		numeric(5),
	 primary key (ID, name),
	 foreign key (name) references Airline(name) 
	 	on delete cascade
	);

create table Flight
	(name		varchar(30),
	 flight_number			numeric(30),
	 dep_date_time			timestamp,
	 dep_airport			varchar(30),
	 arr_airport			varchar(30),
	 arr_date_time			timestamp,
	 base_price			numeric(6,2),
	 ID			numeric(30),
	 status			varchar(30),
	 primary key (flight_number, name, dep_date_time),
	 foreign key (name) references Airline(name)
	 	on delete cascade,
	 foreign key (dep_airport) references Airport(name)
	 	on delete cascade,
	 foreign key (arr_airport) references Airport(name)
	 	on delete set null,
	 foreign key (ID) references Airplane(ID)
	 	on delete cascade
	);

create table Customer
	(email		varchar(30),
	 name			varchar(30),
	 password			varchar(30),
	 building_number			numeric(30),
	 street			varchar(30),
	 city			varchar(30),
	 state			varchar(30),
	 phone_number			numeric(30),
	 passport_number			numeric(30),
	 passport_exp			date,
	 passport_country			varchar(30),
	 date_of_birth			date,
	 primary key (email)
	);

create table Ticket
	(ID		numeric(30),
	 email			varchar(30),
	 name			varchar(30),
	 flight_number			numeric(30),
	 sold_price			numeric(6,2),
	 card_type			varchar(30),
	 card_number			numeric(30),
	 name_on_card			varchar(30),
	 exp_date			date,
	 purchase_date_time			timestamp,
	 primary key (ID),
	 foreign key (email) references Customer(email)
	 	on delete set null,
	 foreign key (name) references Airline(name)
	 	on delete set null,
	 foreign key (flight_number) references Flight(flight_number)
		on delete set null
	);

create table Airline_Staff
	(username		varchar(30),
	 password			varchar(30),
	 first_name			varchar(30),
	 last_name			varchar(30),
	 date_of_birth			date,
	 name			varchar(30),
	 primary key (username),
	 foreign key (name) references Airline(name)
		on delete set null
	);

create table Phone_Number
	(username		varchar(30),
	 phone_number			numeric(30),
	 primary key (username, phone_number),
	 foreign key (username) references Airline_Staff(username)
		on delete cascade
	);

create table Flight_Ratings
	(rating_id		numeric(5),
	name		varchar(30),
	 flight_number		numeric(30),
	 rating		numeric(2),
	 comment		varchar(500),
	 primary key (rating_id),
	 foreign key (name) references Airline(name) 
	 	on delete cascade,
	 foreign key (flight_number) references Flight(flight_number)
		on delete cascade
	);

create view monthly_spending as 
	SELECT *, month(CURRENT_DATE-date(purchase_date_time)) as relative_month
	FROM Ticket


-- Queries to add data into tables
--a.One Airline named "China Eastern".*/
insert into Airline values ('China Eastern');

--b.At least Two airports named "JFK" in NYC and "PVG" in Shanghai.
insert into Airport values ('JFK', 'New York City');
insert into Airport values ('PVG', 'Shanghai');	

--c.Insert at least two customers with appropriate names and other attributes.
insert into Customer values ('email@123.com, 'Max Needle', 'password', 123, 'East 11th Street', 'New York', 'New York', 1234567890, 12345678, '2020-1-1', 'United States of America', '2000-8-30');
insert into Customer values ('email@345.com', 'Matt Needle', 'password', 345, 'East 12th Street', 'New York', 'New York', 1234567891, 87654321, '2020-1-1', 'United States of America', '1985-11-3');

--d.Insert at least two airplanes.
insert into Airplane values ('China Eastern', 12345, 50);
insert into Airplane values ('China Eastern', 54321, 100);

--e.Insert At least One airline Staff working for China Eastern.
insert into Airline_Staff values ('mneedle','password','Manny','Needle','2000-12-9','China Eastern');

--f.Insert several flights with on-time, and delayed statuses.
insert into Flight values ('China Eastern',1234567890, '2020-10-11 10:00:00.00', 'JFK','PVG','2020-10-12 2:00:00.00', 1000.00, 12345, 'on-time');
insert into Flight values ('China Eastern',1234567891, '2020-10-12 10:00:00.00', 'PVG','JFK','2020-10-13 2:00:00.00', 1200.00, 12345, 'on-time');
insert into Flight values ('China Eastern',1234567892, '2020-10-14 10:00:00.00', 'JFK','PVG','2020-10-15 2:00:00.00', 1200.00, 54321, 'delayed');
insert into Flight values ('China Eastern',1234567893, '2020-10-15 10:00:00.00', 'PVG','JFK','2020-10-16 2:00:00.00', 1000.00, 54321, 'delayed');

--g.Insert some tickets for corresponding flights and insert some purchase records (customers bought those tickets).
insert into Ticket values (13579, 'email@123.com', 'China Eastern', 1234567890, 950.00, 'credit', 1234567887654321, 'Max Needle', '2025-1-5',' 2020-1-5 05:00:00.00');
insert into Ticket values (24680, 'email@123.com', 'China Eastern', 1234567891, 1350.00, 'debit', 8765432112345678, 'Max Needle', '2024-5-6',' 2020-1-5 05:00:00.00');


-- Queries to provide sample output
a.Show all the future flights in the system.*/
select * 
from Flight 
where dep_date_time > CURRENT_TIMESTAMP
--copied from clipboard:
name	flight_number	dep_date_time	dep_airport	arr_airport	arr_date_time	base_price	ID	status	
China Eastern	1234567890	2020-10-11 10:00:00	JFK	PVG	2020-10-12 02:00:00	1000.00	12345	on-time	
China Eastern	1234567891	2020-10-12 10:00:00	PVG	JFK	2020-10-13 02:00:00	1200.00	12345	on-time	
China Eastern	1234567892	2020-10-14 10:00:00	JFK	PVG	2020-10-15 02:00:00	1200.00	54321	delayed	
China Eastern	1234567893	2020-10-15 10:00:00	PVG	JFK	2020-10-16 02:00:00	1000.00	54321	delayed	

--b.Show all of the delayed flights in the system.
select * 
from Flight
where status='delayed'
--copied from clipboard:
name	flight_number	dep_date_time	dep_airport	arr_airport	arr_date_time	base_price	ID	status	
China Eastern	1234567892	2020-10-14 10:00:00	JFK	PVG	2020-10-15 02:00:00	1200.00	54321	delayed	
China Eastern	1234567893	2020-10-15 10:00:00	PVG	JFK	2020-10-16 02:00:00	1000.00	54321	delayed	

--c.Show the customer names who bought the tickets.
select Customer.name
from Ticket left join Customer on Ticket.email=Customer.email
--copied from clipboard:
name	
Max Needle	
Max Needle	

--d.Show all of the airplanes owned by the airline (such as "Emirates")
select *
from Airplane
--copied from clipboard:
name	ID	seats	
China Eastern	12345	50	
China Eastern	54321	100	
