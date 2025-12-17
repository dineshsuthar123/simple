-- Gym Management System schema for MySQL
CREATE DATABASE IF NOT EXISTS gymdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gymdb;

CREATE TABLE IF NOT EXISTS Members (
  member_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  gender VARCHAR(10) NOT NULL,
  phone VARCHAR(15),
  email VARCHAR(50),
  join_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Trainers (
  trainer_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  specialization VARCHAR(50) NOT NULL,
  contact_no VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS Membership_Plans (
  plan_id INT AUTO_INCREMENT PRIMARY KEY,
  plan_name VARCHAR(30) NOT NULL,
  duration_months INT NOT NULL,
  fee DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS Member_Plan (
  member_id INT NOT NULL,
  plan_id INT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  PRIMARY KEY (member_id, plan_id),
  CONSTRAINT fk_member_plan_member FOREIGN KEY (member_id) REFERENCES Members(member_id),
  CONSTRAINT fk_member_plan_plan FOREIGN KEY (plan_id) REFERENCES Membership_Plans(plan_id)
);

CREATE TABLE IF NOT EXISTS Workout_Schedule (
  schedule_id INT AUTO_INCREMENT PRIMARY KEY,
  trainer_id INT NOT NULL,
  schedule_name VARCHAR(50) NOT NULL,
  time_slot VARCHAR(30) NOT NULL,
  CONSTRAINT fk_schedule_trainer FOREIGN KEY (trainer_id) REFERENCES Trainers(trainer_id)
);

CREATE TABLE IF NOT EXISTS Payments (
  payment_id INT AUTO_INCREMENT PRIMARY KEY,
  member_id INT NOT NULL,
  schedule_id INT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  mode_of_payment VARCHAR(20) NOT NULL,
  CONSTRAINT fk_payment_member FOREIGN KEY (member_id) REFERENCES Members(member_id),
  CONSTRAINT fk_payment_schedule FOREIGN KEY (schedule_id) REFERENCES Workout_Schedule(schedule_id)
);

CREATE TABLE IF NOT EXISTS Attendance (
  attendance_id INT AUTO_INCREMENT PRIMARY KEY,
  attender_id INT NOT NULL,
  schedule_id INT NOT NULL,
  attendance_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(10) NOT NULL,
  CONSTRAINT fk_attendance_member FOREIGN KEY (attender_id) REFERENCES Members(member_id),
  CONSTRAINT fk_attendance_schedule FOREIGN KEY (schedule_id) REFERENCES Workout_Schedule(schedule_id)
);

-- Seed data (optional)
INSERT INTO Trainers (name, specialization, contact_no) VALUES
 ('Ravi Kumar','Weight Training','9876543210'),
 ('Anita Sharma','Yoga','9876501234');

INSERT INTO Membership_Plans (plan_name, duration_months, fee) VALUES
 ('Basic',3,2000),
 ('Premium',6,4000),
 ('Gold',12,7000);

INSERT INTO Members (name, gender, phone, email) VALUES
 ('Namita Shaji','Female','9998887776','namita@gmail.com'),
 ('Aviksha Rao','Female','9876543211','aviksha@gmail.com');

INSERT INTO Member_Plan (member_id, plan_id, start_date, end_date)
SELECT 1, 3, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 12 MONTH)
UNION ALL
SELECT 2, 1, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 3 MONTH);

INSERT INTO Workout_Schedule (trainer_id, schedule_name, time_slot) VALUES
 (1,'Morning Strength','7 AM - 9 AM'),
 (2,'Evening Yoga','5 PM - 6 PM');

INSERT INTO Payments (member_id, schedule_id, amount, mode_of_payment) VALUES
 (1,1,7000,'Online');

INSERT INTO Attendance (attender_id, schedule_id, status) VALUES
 (1,1,'Present');
