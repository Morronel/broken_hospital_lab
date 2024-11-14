# 🏥 Broken Hospital CTF

> "Where security is optional and privacy is a myth" - Anonymous Patient

## 🎯 Overview
Welcome to Broken Hospital CTF - a deliberately vulnerable web application showcasing various access control vulnerabilities. Built with Flask and containerized for easy deployment, this CTF challenges participants to exploit a medical management system where security is more of a suggestion than a requirement.

## 🚀 Quick Setup

### Prerequisites
- Docker installed
- WSL2 on Windows 11 (tested environment)
- Basic understanding of web

### Deployment

1. Clone this repository:
   ```git clone https://github.com/Morronel/broken_hospital_lab.git```

2. Navigate to the project directory:
   ```cd broken_hospital_lab/broken-hospital```

3. Build the Docker image:
   ```sudo docker build -t broken-hospital .```

4. Run the container:
   ```sudo docker run -p 0.0.0.0:5000:5000 broken-hospital```

Access the application at: `http://127.0.0.1:5000`

## ⚠️ Disclaimer
This application is intentionally vulnerable and should never be deployed in a production environment. It's designed purely for educational purposes and practicing web application security testing.

## 📝 License
MIT License - Feel free to use this for your own CTF events or learning purposes.

---

![image](https://github.com/user-attachments/assets/c2c88893-72e1-4c09-9db0-72a9a4c957d1)

![image](https://github.com/user-attachments/assets/07af21c9-12f9-4681-b4d9-bcf51a76b90b)

![image](https://github.com/user-attachments/assets/1d25fd10-465f-4c92-8419-700a185dcacc)


> "In Broken Hospital, security is just a placebo, and your data is everyone's data!"
