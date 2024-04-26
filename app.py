from flask import Flask, render_template
import boto3
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

# Environment variables for AWS credentials
aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Boto3 Setup with environment variables
def authenticate_aws():
    ec2_client = boto3.client(
        'ec2',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=config['aws_region']
    )
    return ec2_client

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
    ses_client = boto3.client('ses', region_name=config['aws_region'])
    message = {
        'Subject': {'Data': subject},
        'Body': {'Text': {'Data': body}}
    }
    try:
        response = ses_client.send_email(
            Source=config['email']['sender'],
            Destination={'ToAddresses': [config['email']['recipient']]},
            Message=message
        )
        print("Email sent! Message ID:", response['MessageId'])
    except Exception as e:
        handle_error(e)

@app.route('/')
def index():
    ec2_client = authenticate_aws()
    instances = ec2_client.describe_instances()

    health_data = []

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_name = [tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name']
            if instance_name:
                instance_name = instance_name[0]
            else:
                instance_name = instance_id  # Use instance ID if name tag not found

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
