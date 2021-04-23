CREATE TABLE user (
    email varchar(24) PRIMARY KEY,
    password varchar(16)
);
INSERT INTO user (email,password) values ('test@localhost','test');