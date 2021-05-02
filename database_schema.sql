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
    wallet VARCHAR ( 200 ),
    logged_in BOOLEAN DEFAULT FALSE,
    lender BOOLEAN DEFAULT FALSE
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

CREATE TABLE ACTIVITY (
	activity_id serial PRIMARY KEY,
	user_id INTEGER,
	activity_type INTEGER,
	FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

CREATE TABLE LOANS (
	loan_id serial PRIMARY KEY,
	lender INTEGER,
	borrower INTEGER,
	amount INTEGER,
	months INTEGER,
	interest FLOAT,
	created_on TIMESTAMP NOT null,
	accepted BOOLEAN default false,
	eth_address VARCHAR,
	monthly_repayment FLOAT,
	balance FLOAT default 0,
	rcvd_interest FLOAT default 0,
	platform INTEGER default 0,
	state INTEGER default 0,
	payment_number INTEGER default 0,
	withdrawn BOOLEAN default false,
	withdraw_date TIMESTAMP,
	FOREIGN KEY (lender) REFERENCES USERS(user_id),
	FOREIGN KEY (borrower) REFERENCES USERS(user_id)
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
	lender_id INTEGER,
	amount FLOAT,
	months INTEGER,
	interest FLOAT,
	created_on TIMESTAMP NOT null,
	accepted BOOLEAN default false,
	expiration_date DATE,
	rejected BOOLEAN default false,
	platform INTEGER default 0,
	withdrawn BOOLEAN default false,
	withdraw_date TIMESTAMP,
	FOREIGN KEY (borrower_id) REFERENCES USERS(user_id),
	FOREIGN KEY (lender_id) REFERENCES USERS(user_id),
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

CREATE TABLE PAYMENTS (
	payment_id serial PRIMARY KEY,
	loan_id INTEGER,
	receiver_id INTEGER,
	sender_id INTEGER,
	amount INTEGER,
	payment_date TIMESTAMP NOT null,
	validated BOOLEAN default false, 
	validation_hash VARCHAR (300),
	FOREIGN KEY (receiver_id) REFERENCES USERS(user_id),
	FOREIGN KEY (sender_id) REFERENCES USERS(user_id),
	FOREIGN KEY (loan_id) REFERENCES LOANS(loan_id)
);

CREATE TABLE NOTIFICATIONS (
	notification_id serial PRIMARY KEY,
	user_id INTEGER,
	message VARCHAR,
	created_on TIMESTAMP NOT null,
	dismissed BOOLEAN default false, 
	notification_type INTEGER,
	FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

CREATE TABLE PARTICIPANT (
	lender_id INTEGER,
	borrower_id INTEGER,
	loan_id INTEGER,
	FOREIGN KEY (lender_id) REFERENCES USERS(user_id),
	FOREIGN KEY (borrower_id) REFERENCES USERS(user_id),
	FOREIGN KEY (loan_id) REFERENCES LOANS(loan_id)
);