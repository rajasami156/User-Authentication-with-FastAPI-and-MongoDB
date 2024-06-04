# 🛡️ FastAPI Authentication System
Welcome to the FastAPI Authentication System! This project provides a secure and efficient solution for user registration, login, and password recovery using FastAPI and MongoDB. Whether you're building a new application or improving an existing one, our system is designed to help you handle user authentication and password management with ease. 🚀

## ✨ Key Features
Registration & Login: Users can register and log in securely using their username or email.
JWT Authentication: Employs JSON Web Tokens (JWT) for secure and stateless user authentication.
Password Recovery: Allows users to request and perform password resets through a secure recovery code system.
Scalable & Extendable: Built with FastAPI, it is highly performant and ready for deployment in production environments.
## 📦 Endpoints
### 🔒 Authentication Routes
/auth/register (POST): Register a new user by providing a username, email, and password.
/auth/login (POST): Log in with either a username or an email, plus the password.
/auth/request_reset (POST): Request a password recovery code to be sent via email.
/auth/perform_reset (POST): Reset the password using a recovery code.
## 🛠️ Utility Functions
get_current_user: Retrieve the current user by decoding the JWT token.
send_recovery_email: Sends a recovery code email in the background for secure password resets.
## 🏗️ How to Use
### 🖥️ Installation
Clone the repository to your local machine.
Ensure you have Python 3.7+ installed.
Set up a virtual environment and install dependencies with pip.
Configure your MongoDB connection string and credentials in the environment variables.
Run the FastAPI server.

#### Make sure to add this in your .env file:

SMTP_HOST = smtp.gmail.com

SMTP_PORT = 465

SMTP_USERNAME = sami@gmail.com

SMTP_PASSWORD  = v**v *** zzdv o**t

SMTP_MAIL_DEFAULT_SENDER = Samiullah <nicesami156@@gmail.com>


## 📧 Email Configuration
For the password recovery feature to work, set up a suitable email delivery service and provide its credentials.

## 🤝 Contributions
Contributions are welcome! Feel free to fork the repository, submit issues, or open pull requests.

## 📝 License
This project is licensed under the MIT License.

#### Happy Coding! 💻





