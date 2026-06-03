-- ---------------------------------------------------------
-- CREATE DATABASE
-- ---------------------------------------------------------
CREATE DATABASE blood_bank_system;
USE blood_bank_system;


-- ---------------------------------------------------------
-- TABLE 1: DONORS
-- ---------------------------------------------------------
CREATE TABLE donors (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    blood_group VARCHAR(10),
    mobile VARCHAR(20),
    address VARCHAR(200)
);

-- 10 SAMPLE DONORS
INSERT INTO donors (name, blood_group, mobile, address) VALUES
('Rohan Mehta', 'A+', '9876543210', 'Mumbai'),
('Sneha Patil', 'O-', '9123456780', 'Pune'),
('Amit Sharma', 'B+', '9822334455', 'Nashik'),
('Priya Verma', 'AB+', '9988776655', 'Nagpur'),
('Karan Singh', 'O+', '9765423109', 'Thane'),
('Pooja Desai', 'A-', '9090909090', 'Surat'),
('Rahul Jain', 'B-', '9133557799', 'Indore'),
('Swati Kulkarni', 'AB-', '9811223344', 'Kolhapur'),
('Manish Gupta', 'O+', '9900112233', 'Delhi'),
('Anita Sharma', 'A+', '9007006005', 'Jaipur');


-- ---------------------------------------------------------
-- TABLE 2: PATIENTS
-- ---------------------------------------------------------
CREATE TABLE patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    required_blood_group VARCHAR(10),
    mobile VARCHAR(20),
    disease VARCHAR(200)
);

-- 10 SAMPLE PATIENTS
INSERT INTO patients (name, required_blood_group, mobile, disease) VALUES
('Suresh Kumar', 'A+', '9001234567', 'Accident Injury'),
('Kavita Gupta', 'O-', '9898989898', 'Heart Surgery'),
('Ramesh Jadhav', 'B+', '9933221100', 'Cancer Treatment'),
('Neha Sharma', 'AB+', '9870012345', 'Kidney Failure'),
('Vikas Patil', 'O+', '9022446688', 'Dengue'),
('Manoj Verma', 'A-', '9811452255', 'Severe Anemia'),
('Kusum B', 'B-', '9988665544', 'Bone Marrow Issue'),
('Tina Roy', 'AB-', '9099554411', 'Liver Infection'),
('Farhan Khan', 'O+', '9797979797', 'Thalassemia'),
('Asha Rani', 'A+', '9888777665', 'Blood Loss After Surgery');
