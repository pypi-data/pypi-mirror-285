from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def send_email(sender_email: str, sender_pwd: str, receiver_email: str, body: str, subject: str, mode: str = "plain") -> None:
    """
    Sends an email to a receiver via gmail.
    
    mode: The mode of the text in the body. (e.g. html, plain, ...)
    """
    try:
        # Set up the MIME
        message: MIMEMultipart = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        
        # Attach the body with the msg instance
        message.attach(MIMEText(body, mode))
        
        # Create SMTP session for sending the mail
        server:smtplib.SMTP = smtplib.SMTP('smtp.gmail.com', 587) # Use Gmail with port
        server.starttls() # Enable security
        
        # Login with your email and password
        server.login(sender_email, sender_pwd)
        
        # Convert the message to a string and send it
        text: str = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        
        # Terminate the SMTP session and close the connection
        server.quit()
    except Exception as e: raise Exception(f"Failed to send email. --> {e}")