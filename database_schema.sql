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
	balance FLOAT,
	est_total_interest FLOAT,
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
	loan_eth_address VARCHAR,
	receiver_id INTEGER,
	sender_id INTEGER,
	amount INTEGER,
	payment_date TIMESTAMP NOT null,
	validated BOOLEAN default false, 
	validation_hash VARCHAR (300),
	FOREIGN KEY (receiver_id) REFERENCES USERS(user_id),
	FOREIGN KEY (sender_id) REFERENCES USERS(user_id)
);