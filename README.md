# 🩸 LifeLink – Smart Blood Donor & Emergency Assistance System

LifeLink is a web-based blood donor and emergency assistance platform designed to help patients and hospitals connect with suitable blood donors during emergency situations.

## 🚀 Features

### 👤 Patient
- Patient registration and login
- Submit emergency blood requests
- Select required blood group
- Select number of blood units
- Select urgency level
- Select registered hospital
- Track blood request status
- View donor responses

### 🩸 Donor
- Donor registration and login
- Blood group and city information
- Availability status
- View emergency blood requests
- Accept or decline blood requests
- Donor dashboard

### 🏥 Hospital
- Hospital registration
- Hospital login
- Hospital verification
- View blood requests
- View accepted donor details
- Approve/match donors
- Mark requests as fulfilled
- Manage request status

### 👨‍💼 Admin
- Admin login
- Verify hospitals
- Monitor blood requests
- Manage users and donors
- Manage system data

## 🔄 System Workflow

Patient / Hospital
       ↓
Create Blood Request
       ↓
System Checks Available Donors
       ↓
Matching Donors Are Notified
       ↓
Donor Accepts / Declines
       ↓
Hospital Reviews Accepted Donor
       ↓
Hospital Approves / Matches
       ↓
Blood Donation
       ↓
Request Marked as Fulfilled

## 🛠️ Technologies Used

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- Flask

### Database
- MySQL

### Python Libraries
- Flask
- mysql-connector-python
- scikit-learn
- pandas
- numpy
- python-dotenv

## 🗄️ Database

LifeLink uses MySQL for storing application data.

Main tables:

- users
- hospitals
- blood_requests
- donations
- donor_responses

## 📁 Project Structure

LifeLink/
├── app.py
├── requirements.txt
├── reset_lifelink.py
├── .gitignore
└── templates/
    ├── admin_dashboard.html
    ├── admin_login.html
    ├── admin_request_details.html
    ├── donor_dashboard.html
    ├── find_blood.html
    ├── hospital_dashboard.html
    ├── hospital_login.html
    ├── hospital_register.html
    ├── index.html
    ├── login.html
    ├── my_requests.html
    ├── patient_register.html
    ├── register.html
    ├── request_blood.html
    └── request_status.html

## ⚙️ Installation

### 1. Clone the repository

git clone https://github.com/sameerashaik5234/LifeLink.git
cd LifeLink

### 2. Create a virtual environment

python -m venv venv

### 3. Activate the virtual environment

Windows:

venv\Scripts\activate

### 4. Install required packages

pip install -r requirements.txt

### 5. Configure environment variables

Create a .env file in the project root:

LIFELINK_SECRET_KEY=your_secret_key
LIFELINK_DB_PASSWORD=your_mysql_password

Do not upload .env to GitHub.

### 6. Create the MySQL database

CREATE DATABASE lifelink;

Then create the required project tables using the database schema.

### 7. Run the application

python app.py

The application will run locally at:

http://127.0.0.1:5000

## 🔐 Security

The project uses:

- Password hashing
- Session-based authentication
- Role-based access
- Environment variables for sensitive configuration
- .gitignore to prevent secrets from being uploaded

## 🎯 Project Objective

The main objective of LifeLink is to provide a centralized platform that helps connect blood donors with patients and hospitals during emergency situations.

The project focuses on improving coordination and reducing the time required to find potential donors.

## ⚠️ Important Note

LifeLink is an emergency coordination and donor-matching platform.

It does not replace hospitals, blood banks, doctors, or professional medical verification.

Blood-group compatibility, donor eligibility, and final medical decisions must be verified by qualified medical professionals or authorized blood banks.

## 🔮 Future Enhancements

- SMS emergency notifications
- WhatsApp notifications
- OTP-based verification
- GPS-based nearby donor matching
- Hospital document verification
- Advanced donor availability management
- Email notifications
- Blood donation history
- Admin analytics dashboard
- Mobile application
- Improved emergency response tracking

## 👨‍💻 Project

**Project Name:** LifeLink – Smart Blood Donor & Emergency Assistance System

**Type:** Final Year Computer Engineering Project

**GitHub Repository:**

https://github.com/sameerashaik5234/LifeLink

## 📄 License

This project is developed for educational and academic purposes.
