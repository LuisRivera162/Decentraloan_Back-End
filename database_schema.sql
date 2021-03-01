CREATE TABLE USERS (
	user_id serial PRIMARY KEY,
	username VARCHAR ( 50 ) UNIQUE NOT NULL,
	firstname VARCHAR ( 50 ) NOT NULL,
	lastname VARCHAR ( 50 ) NOT NULL,
	password VARCHAR ( 200 ) NOT NULL,
	email VARCHAR ( 255 ) UNIQUE NOT NULL,
	created_on TIMESTAMP NOT NULL,
	last_login TIMESTAMP,
	user_age INTEGER,
	phone VARCHAR ( 11 ),
	eth_address VARCHAR ( 200 ) UNIQUE NOT NULL,
	logged_in BOOLEAN DEFAULT FALSE
);


CREATE TABLE BORROWERS (
	borrower_id serial PRIMARY KEY,
	user_id INTEGER,
	created_on TIMESTAMP NOT null,
	FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

CREATE TABLE LOANERS (
	loaner_id serial PRIMARY KEY,
	user_id INTEGER,
	created_on TIMESTAMP NOT null,
	FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

CREATE TABLE LOANS (
	loan_id serial PRIMARY KEY,
	user_id INTEGER,
	loan_amount MONEY,
	time_frame DATE,
	interest FLOAT,
	created_on TIMESTAMP NOT null,
	accepted BOOLEAN default false,
	FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

CREATE TABLE CHATS (
	chat_id serial PRIMARY KEY,
	loan_id INTEGER,
	loaner_id INTEGER,
	borrower_id INTEGER,
	created_on TIMESTAMP NOT null,
	FOREIGN KEY (loaner_id) REFERENCES USERS(user_id),
	FOREIGN KEY (borrower_id) REFERENCES USERS(user_id),
	FOREIGN KEY (loan_id) REFERENCES LOANS(loan_id)
);

CREATE TABLE OFFER (
	offer_id serial PRIMARY KEY,
	loan_id INTEGER,
	borrower_id INTEGER,
	desired_amount MONEY,
	time_frame DATE,
	interest DECIMAL(5,2),
	created_on TIMESTAMP NOT null,
	accepted BOOLEAN default false,
	espiration_date DATE,
	FOREIGN KEY (borrower_id) REFERENCES USERS(user_id),
	FOREIGN KEY (loan_id) REFERENCES LOANS(loan_id)
);

CREATE TABLE MESSAGE (
	message_id serial PRIMARY KEY,
	chat_id INTEGER,
	loaner_id INTEGER,
	borrower_id INTEGER,
	created_on TIMESTAMP NOT null,
	message VARCHAR (300),
	FOREIGN KEY (loaner_id) REFERENCES USERS(user_id),
	FOREIGN KEY (borrower_id) REFERENCES USERS(user_id),
	FOREIGN KEY (chat_id) REFERENCES CHATS(chat_id)
);