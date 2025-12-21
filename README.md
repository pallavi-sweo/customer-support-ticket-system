# customer-support-ticket-system
To build a Customer Support Ticket System similar to tools like Freshdesk / Zendesk (lite version)

mysql -u root -p
CREATE DATABASE tickets_db;
show databases;
CREATE USER 'tickets_user'@'localhost' IDENTIFIED BY 'tickets_pass';
GRANT ALL PRIVILEGES ON tickets_db.* TO 'tickets_user'@'localhost';
FLUSH PRIVILEGES;

Apis:
/signup & /login completed
Execution steps:
cd backend
uvicorn app.main:app --reload


USE tickets_db;
SHOW TABLES;
DESCRIBE users;
select * from users;

pytest or python -m pytest -q
black .
flake8 .
pylint app
