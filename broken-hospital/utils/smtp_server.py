import asyncio
from aiosmtpd.controller import Controller
import smtplib
from email.parser import Parser
from email.policy import default
import threading
import logging
import socket
from datetime import datetime

class CustomSMTPHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        # Accept all emails for our CTF domains
        allowed_domains = ['binary.xor', 'hackers.net', 'brokenhospital.ctf']
        domain = address.split('@')[-1]
        if domain not in allowed_domains:
            return f'550 Only {", ".join(allowed_domains)} addresses are accepted'
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        print('Received mail:')
        print(f'From: {envelope.mail_from}')
        print(f'To: {envelope.rcpt_tos}')
        print(f'Data: {envelope.content.decode("utf8", errors="replace")}')
        
        # Store the email for web interface instead of forwarding to Gmail
        email_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'from': envelope.mail_from,
            'to': envelope.rcpt_tos,
            'body': envelope.content.decode('utf8', errors='replace')
        }
        stored_emails.append(email_data)
        
        return '250 Message accepted for delivery'

class EmailServer:
    def __init__(self, host='127.0.0.1', start_port=2525):
        self.host = host
        self.port = self.find_available_port(start_port)
        self.controller = None
        self.thread = None

    def find_available_port(self, start_port, max_attempts=10):
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + max_attempts):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind((self.host, port))
                    return port
                except OSError:
                    continue
        raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")

    def start(self):
        def run():
            try:
                self.controller = Controller(
                    CustomSMTPHandler(), 
                    hostname=self.host, 
                    port=self.port
                )
                self.controller.start()
                print(f"SMTP Server running on {self.host}:{self.port}")
            except Exception as e:
                print(f"Failed to start SMTP server: {e}")
                raise

        self.thread = threading.Thread(target=run)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        if self.controller:
            self.controller.stop()