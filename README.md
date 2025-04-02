# DICOM Protocol Honeypot

A honeypot system designed to detect and monitor unauthorized access attempts to DICOM (Digital Imaging and Communications in Medicine) services.

## Features
- Simulates a DICOM server with configurable services
- Supports standard DICOM operations (C-ECHO, C-FIND, C-MOVE, C-STORE)
- Embeds honeytokens in DICOM data to track data exfiltration
- Real-time monitoring and alerting for suspicious activities
- Web API for configuration and monitoring
- Integration with Elasticsearch for event storage and analysis

## Installation

### Using Docker (Recommended)
```bash
# Clone the repository
git clone https://github.com/Ansh5748/dicom-honeypot.git
cd dicom-honeypot

# Start the containers
docker-compose up -d
```

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/Ansh5748/dicom-honeypot.git
cd dicom-honeypot

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the application
python -m app
```

## Usage

### Starting the Honeypot
```bash
# Start both DICOM server and API
python -m app

# Start only the DICOM server
python -m app --dicom-only

# Start only the API server
python -m app --api-only
```

### Testing DICOM Connectivity
To test if the DICOM server is working correctly, you can use the echoscu tool from the DCMTK package:
```bash
# Install DCMTK (if not already installed)
sudo apt-get install dcmtk

# Test DICOM connectivity (C-ECHO)
echoscu localhost 11112 -aec HONEYPOT
```
A successful response indicates that the DICOM server is running correctly.

## Accessing the API
The API is available at `http://localhost:8000/` with the following endpoints:

- `/api/events/` - Query DICOM events
- `/api/stats/` - Get statistics about connections and events
- `/api/alerts/` - View security alerts
- `/api/config/` - Configure the honeypot

## Accessing the Dashboard
The web dashboard is available at `http://localhost:8000/index.html` and provides:
- Real-time monitoring of DICOM events
- Visualization of connection attempts
- Configuration management
- Event search and filtering

## Architecture
The DICOM Honeypot consists of several interconnected components:
- **DICOM Server**: Emulates a DICOM server with deliberate vulnerabilities
- **Elasticsearch**: Stores all captured events and attack data
- **Kibana**: Provides visualization and dashboards for monitoring
- **API Server**: Offers programmatic access to the collected data

## Understanding DICOM Port Access
The DICOM server runs on port `11112`, which is the standard DICOM port. This port is not accessible through a web browser, as DICOM uses its own protocol that's different from HTTP.

To interact with the DICOM server:
- Use a DICOM client application (like Horos, OsiriX, or dcmtk)
- Configure the client to connect to your server's IP address on port `11112`
- Use "HONEYPOT" as the AE Title

For example, using `dcmtk`:
```bash
# Test DICOM connectivity (C-ECHO)
echoscu -d localhost 11112 -aec HONEYPOT
```

## Monitoring and Analysis

### Web Dashboard
Access the dashboard at `http://localhost:8000/index.html` to:
- View real-time events
- Search and filter connection attempts
- Configure the honeypot
- View system status

### Kibana Dashboard
Access Kibana at `http://localhost:5601` to:
- Create custom visualizations
- Perform advanced searches
- Set up alerts
- Export data for further analysis

## Configuration
Configuration files are located in the `app/config/` directory:
- `dicom_config.py` - DICOM server configuration
- `honeytokens.py` - Honeytoken configuration
- `logging_config.py` - Logging configuration

## Troubleshooting

### Common Issues
#### DICOM Server Not Starting
```bash
# Check logs
docker logs dicom-honeypot
# Ensure port 11112 is not in use by another application
```

#### Cannot Connect to DICOM Server
```bash
# Verify the server is running
docker exec dicom-honeypot netstat -tuln | grep 11112
# Check firewall settings to ensure port 11112 is open
```

#### Elasticsearch Connection Issues
```bash
# Check Elasticsearch status
curl http://localhost:9200
# Ensure Elasticsearch container is running
docker ps | grep elasticsearch
```

## Security Considerations
This honeypot is designed to attract attackers. Deploy it in a controlled environment and monitor it closely. Consider:
- Placing it in a segregated network
- Using a firewall to control access
- Regularly reviewing logs for suspicious activity
- Not storing real patient data in the honeypot

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- [pynetdicom](https://github.com/pydicom/pynetdicom) for DICOM networking capabilities
- [Elasticsearch](https://www.elastic.co/) for powerful data storage and search
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework