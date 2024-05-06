# Server Health Check

Server Health Check is a Flask application that monitors the health metrics of servers (EC2 instances) and sends email notifications if any metric exceeds predefined thresholds.

## Features

- Monitor CPU usage, memory usage, disk usage, and network connectivity of EC2 instances.
- Send email notifications to alert the DevOps team of any issues.
- Basic frontend interface to view server health metrics in real-time.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.x installed on your machine.
- AWS account with necessary permissions for EC2 instances and SES.
- Configuration settings stored in a `config.yml` file.

### Installation

1. **Clone the repository**:

    ```bash
   git clone https://github.com/prasad3936/Server-Health-Check-Application.git
    ```

    ### Snapshots
![Final Output](https://github.com/prasad3936/Server-Health-Check-Application/assets/63768420/26e3f940-319a-422a-82e5-4ec49ed4df60)

   

3. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

### Configuration

Before running the application, ensure you have configured the following settings:

1. **AWS Credentials**: 
   - Set environment variables for `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
   - Or configure AWS credentials file (`~/.aws/credentials`).

2. **Configuration File**:
   - Create a `config.yml` file in the project root directory with the following structure:

   ```yaml
   thresholds:
     cpu: 80
     memory: 90
     disk: 80
   email:
     sender: example@example.com
     recipient: recipient@example.com
   aws_region: us-east-1

### Running the application 

1. ***Get into the directory***
   
```bash
cd Server-Health-Check-Application
```
2. ***Run command***
   
```bash
python3 app.py
```

### Accessing The Application

***http://localhost:5000***

### Snapshot
![Final Output](https://github.com/prasad3936/Server-Health-Check-Application/assets/63768420/32c10067-99f3-4ebe-9c11-f9263ac05058)
