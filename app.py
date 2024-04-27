from flask import Flask, render_template
import psutil
import ping3
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import yaml
import os

app = Flask(__name__)

# Read configuration from config.yml file
with open('config.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)

# Health Checkup Logic
def get_instance_metrics(instance_id):
    metrics = {}
    # CPU usage
    metrics['cpu_usage'] = psutil.cpu_percent(interval=1)
    # Memory usage
    mem = psutil.virtual_memory()
    metrics['memory_usage'] = mem.percent
    # Disk space
    disk = psutil.disk_usage('/')
    metrics['disk_usage'] = disk.percent
    # Network connectivity
    metrics['network_status'] = 'UP' if ping3.ping('8.8.8.8') else 'DOWN'
    
    return metrics

# Logging
logging.basicConfig(filename='health_check.log', level=logging.INFO)

# Error Handling
def handle_error(exception):
    logging.error(f"An error occurred: {exception}")

# Email Notification
def send_email_notification(subject, body):
    # Set up SMTP connection to Gmail
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Gmail SMTP port
    sender_email = os.environ.get('EMAIL_USERNAME')
    sender_password = os.environ.get('EMAIL_PASSWORD')

    if not sender_email or not sender_password:
        raise ValueError("Email username or password not set in environment variables.")

    # Create message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = config['email']['recipient']
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        # Start TLS for security
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        # Login with your Gmail credentials
        server.login(sender_email, sender_password)
        # Send email
        server.sendmail(sender_email, config['email']['recipient'], message.as_string())
        print("Email sent!")
    except Exception as e:
        handle_error(e)
    finally:
        # Quit SMTP server
        server.quit() if 'server' in locals() else None

@app.route('/')
def index():
    instances = boto3.client('ec2', region_name=config['aws_region']).describe_instances()

    health_data = []

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_name = next((tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name'), instance_id)

            try:
                metrics = get_instance_metrics(instance_id)
                health_data.append({
                    'instance_id': instance_id,
                    'instance_name': instance_name,
                    'cpu_usage': metrics['cpu_usage'],
                    'memory_usage': metrics['memory_usage'],
                    'disk_usage': metrics['disk_usage'],
                    'network_status': metrics['network_status']
                })
                
                exceeded_thresholds = []
                if metrics['cpu_usage'] > config['thresholds']['cpu']:
                    exceeded_thresholds.append('CPU usage')
                if metrics['memory_usage'] > config['thresholds']['memory']:
                    exceeded_thresholds.append('Memory usage')
                if metrics['disk_usage'] > config['thresholds']['disk']:
                    exceeded_thresholds.append('Disk usage')
                if metrics['network_status'] == 'DOWN':
                    exceeded_thresholds.append('Network status')
                
                if exceeded_thresholds:
                    subject = f"Issue detected on instance: {instance_name}"
                    body = f"The following health metrics exceeded thresholds: {', '.join(exceeded_thresholds)}"
                    send_email_notification(subject, body)
                
            except Exception as e:
                handle_error(e)
                health_data.append({
                    'instance_id': instance_id,
                    'instance_name': instance_name,
                    'error': str(e)
                })

    return render_template('index.html', health_data=health_data)

if __name__ == '__main__':
    app.run(debug=True)
