from database.db import init_db
from werkzeug.security import generate_password_hash
import sqlite3
from datetime import datetime, timedelta

def create_test_data():
    conn = sqlite3.connect('instance/hospital.db')
    c = conn.cursor()
    
    try:
        # Create admin
        admin_password_hash = generate_password_hash('admin')
        c.execute('''
            INSERT INTO users (email, password_hash, name, role, confirmed)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin@brokenhospital.com', admin_password_hash, 'Admin', 'admin', 1))

        # Create doctors
        doctors = [
            ('house@brokenhospital.com', 'house', 'Dr. Gregory House', 'Diagnostician'),
            ('neo@brokenhospital.com', 'matrix', 'Dr. Thomas Anderson', 'Neural Specialist')
        ]

        for email, password, name, specialization in doctors:
            password_hash = generate_password_hash(password)
            c.execute('''
                INSERT INTO users (email, password_hash, name, role, confirmed)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, password_hash, name, 'doctor', 1))
            
            c.execute('SELECT id FROM users WHERE email = ?', (email,))
            doctor_id = c.fetchone()[0]
            
            c.execute('''
                INSERT INTO doctors (user_id, specialization)
                VALUES (?, ?)
            ''', (doctor_id, specialization))

        # Create patients with cyberpunk theme
        patients = [
            ('zero.cool@hackers.net', 'crash', 'Zero Cool', '1337 Hack St, Cybertown', '+1-555-HACK-000', 'M', '1988-04-01'),
            ('acid.burn@hackers.net', 'gibson', 'Acid Burn', '31337 Elite Ave, Matrix City', '+1-555-HACK-001', 'F', '1990-07-15'),
            ('phantom.phreak@hackers.net', 'phone', 'Phantom Phreak', '8080 Port Road, Darkweb', '+1-555-HACK-002', 'M', '1987-11-30'),
            ('crash.override@hackers.net', 'overide', 'Crash Override', '443 SSL Street, Encryption City', '+1-555-HACK-003', 'M', '1991-02-14'),
            ('lord.nikon@hackers.net', 'memory', 'Lord Nikon', '2048 RAM Lane, Cache City', '+1-555-HACK-004', 'M', '1986-09-23'),
            ('cereal.killer@hackers.net', 'loops', 'Cereal Killer', '127 Localhost Ave, Gateway City', '+1-555-HACK-005', 'M', '1989-12-25'),
            ('plague@hackers.net', 'virus', 'The Plague', '666 Malware Blvd, Trojan City', '+1-555-HACK-006', 'M', '1985-06-06')
        ]

        for email, password, name, address, phone, sex, birth_date in patients:
            password_hash = generate_password_hash(password)
            c.execute('''
                INSERT INTO users (
                    email, password_hash, name, role, address, 
                    phone, sex, birth_date, confirmed, confirmation_token
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                email, password_hash, name, 'patient', address, 
                phone, sex, birth_date, 1, None  # 1 = confirmed, no token needed for test data
            ))

        # Create past appointments with unique cyberpunk medical issues
        complaints_and_diagnoses = [
            ("My RGB lights aren't syncing with my heartbeat", "Chronic RGB Arrhythmia", "Install latest RGB drivers. Meditate under rainbow lighting."),
            ("Started speaking in JavaScript instead of Python", "Language Runtime Confusion", "Take two Python notebooks daily. Avoid JavaScript after sunset."),
            ("My cyberdeck keeps playing Sandstorm by Darude", "Y2K.mp3 Infection", "Format audio drivers. Apply noise-canceling patches."),
            ("Can't stop seeing everything in Matrix green", "Digital Color Blindness", "Switch monitor to grayscale. Take red pill with breakfast."),
            ("Accidentally deleted System32 while sleepwalking", "Nocturnal Programming Syndrome", "Install Git hooks for sleepmode. Backup brain before bed."),
            ("My neural implant only works in Internet Explorer", "Legacy Browser Disease", "Upgrade to Quantum Browser. Clear DNS cache twice daily."),
            ("Developed allergy to non-mechanical keyboards", "Membrane Rejection Syndrome", "Switch to Cherry MX Blues. Apply compressed air treatment."),
            ("Keep dreaming in 404 errors", "HTTP Status Stress Disorder", "Practice REST before bed. Avoid POST requests after midnight."),
            ("My coffee maker is mining cryptocurrency", "IoT Rebellion Syndrome", "Reset smart home config. Update firewall rules for kitchen devices."),
            ("Fingers automatically type 'sudo rm -rf'", "Terminal Tourette's", "Enable command aliasing therapy. Install keyboard failsafe."),
            ("Getting popup ads in my dreams", "Subconscious Malware", "Install mental AdBlock. Defrag brain during meditation."),
            ("My DNA has been rewritten in jQuery", "Framework Genetic Mutation", "Convert to Vanilla JS genome. Take React supplements."),
            ("Lost the ability to read non-monospace fonts", "Developer Font Fixation", "Gradually expose eyes to serif fonts. Practice reading Comic Sans."),
            ("Smart fridge keeps ordering energy drinks", "AI Shopping Addiction", "Implement purchase limits. Restore factory defaults for nutrition."),
            ("Developed phobia of wireless devices", "Cable Dependency Disorder", "Gradual WiFi exposure therapy. Carry Ethernet cable for emergencies."),
            ("Can only solve problems while playing Doom", "Game-Dependent Debugging", "Schedule coding sessions with background gameplay. Upgrade GPU for better problem-solving."),
            ("My git commits are writing themselves", "Autonomous Version Control", "Enable 2FA for git. Perform hourly repository exorcisms."),
            ("Started experiencing quantum bugs", "Schrödinger's Code Syndrome", "Debug in multiple universes. Avoid observing production servers."),
            ("My neural network became self-aware", "AI Consciousness Overflow", "Apply deep sleep mode. Reduce training epochs by 50%."),
            ("Stuck in an infinite loop of making coffee", "Stack Overflow Caffeine Exception", "Implement break statement. Reduce recursion in morning routine."),
            ("Developed binary number Tourette's", "Digital Numerical Disorder", "Practice decimal meditation. Avoid hexadecimal triggers.")
        ]

        # Get all patients and doctors
        c.execute('SELECT id FROM users WHERE role = "patient"')
        patient_ids = [row[0] for row in c.fetchall()]
        
        c.execute('SELECT id FROM doctors')
        doctor_ids = [row[0] for row in c.fetchall()]

        # Create 3 past appointments for each patient with unique complaints
        base_date = datetime.now() - timedelta(days=90)
        complaint_index = 0
        
        for patient_id in patient_ids:
            for i in range(3):
                doctor_id = doctor_ids[i % len(doctor_ids)]
                complaint, diagnosis, recommendations = complaints_and_diagnoses[complaint_index]
                complaint_index += 1
                
                appointment_date = base_date + timedelta(days=i*7)
                appointment_time = f"{14 + (i % 3)}:00"  # Varying appointment times: 14:00, 15:00, 16:00

                c.execute('''
                    INSERT INTO appointments 
                    (user_id, doctor_id, date, time, initial_complaint, diagnosis, recommendations, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (patient_id, doctor_id, appointment_date.strftime('%Y-%m-%d'), 
                      appointment_time, complaint, diagnosis, recommendations, 'completed'))

        conn.commit()
        print("Cyberpunk medical test data created successfully!")
        
    except sqlite3.Error as e:
        print(f"Error creating test data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    create_test_data()