import asyncio
from datetime import datetime
import json

# Store emails in memory for the web interface
stored_emails = []

class DualProtocolServer:
    def __init__(self, host='0.0.0.0', port=5337):
        self.host = host
        self.port = port
        self.server = None
        
    async def handle_client(self, reader, writer):
        try:
            first_line = await reader.readline()
            if not first_line:  # Add timeout and connection check
                writer.close()
                return
                
            peername = writer.get_extra_info('peername')
            print(f"New connection from {peername}")
            
            if first_line.startswith(b'EHLO') or first_line.startswith(b'HELO'):
                # SMTP connection
                await self.handle_smtp(first_line, reader, writer)
            else:
                # Not an SMTP connection, close it
                writer.write(b'500 Unknown protocol\r\n')
                await writer.drain()
                writer.close()
                
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def handle_smtp(self, first_line, reader, writer):
        try:
            # Send greeting
            writer.write(b'220 localhost ESMTP Postfix\r\n')
            await writer.drain()

            # Handle EHLO/HELO
            if first_line.startswith(b'EHLO') or first_line.startswith(b'HELO'):
                writer.write(b'250-localhost\r\n')
                writer.write(b'250-PIPELINING\r\n')
                writer.write(b'250-SIZE 10240000\r\n')
                writer.write(b'250-VRFY\r\n')
                writer.write(b'250-ETRN\r\n')
                writer.write(b'250-STARTTLS\r\n')
                writer.write(b'250-8BITMIME\r\n')
                writer.write(b'250 DSN\r\n')
                await writer.drain()

            # Process SMTP commands
            while True:
                line = await reader.readline()
                if not line:
                    break
                    
                line = line.strip().upper()
                
                if line.startswith(b'QUIT'):
                    writer.write(b'221 Bye\r\n')
                    await writer.drain()
                    break
                    
                elif line.startswith(b'MAIL FROM:'):
                    writer.write(b'250 Ok\r\n')
                    await writer.drain()
                    
                elif line.startswith(b'RCPT TO:'):
                    writer.write(b'250 Ok\r\n')
                    await writer.drain()
                    
                elif line == b'DATA':
                    writer.write(b'354 End data with <CR><LF>.<CR><LF>\r\n')
                    await writer.drain()
                    
                    # Collect email data
                    email_lines = []
                    while True:
                        data_line = await reader.readline()
                        if data_line.strip() == b'.':
                            break
                        email_lines.append(data_line.decode())
                    
                    # Store the email
                    email_content = ''.join(email_lines)
                    stored_emails.append({
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'from': 'noreply@brokenhospital.ctf',
                        'to': ['hecker@binary.xor'],
                        'body': email_content
                    })
                    
                    writer.write(b'250 Ok: queued\r\n')
                    await writer.drain()
                    
                else:
                    writer.write(b'500 Error: command not recognized\r\n')
                    await writer.drain()
                    
        except Exception as e:
            print(f"SMTP Error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def start(self):
        self.server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        print(f'Server running on {self.host}:{self.port}')
        await self.server.serve_forever()

if __name__ == '__main__':
    server = DualProtocolServer()
    asyncio.run(server.start())