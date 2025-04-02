"""
Configuration for honeytokens used in the DICOM honeypot.
"""

HONEYTOKEN_CONFIG = {
    'patient_names': [
        'HONEYPOT^PATIENT',
        'TRACKER^MEDICAL',
        'MONITOR^ALERT',
        'SECURITY^TEST',
        'CANARY^TOKEN'
    ],
    
    'patient_ids': [
        'HT-10001',
        'HT-10002',
        'HT-10003',
        'HT-10004',
        'HT-10005'
    ],
    
    'institution_names': [
        'Honeypot Medical Center',
        'Security Monitoring Hospital',
        'Tracking Medical Institute',
        'Alert Healthcare System',
        'Canary Medical Group'
    ],
    
    'study_descriptions': [
        'HONEYPOT STUDY - DO NOT USE FOR DIAGNOSIS',
        'SECURITY MONITORING SCAN - NOT REAL PATIENT',
        'TRACKING TEST - ALERT ON ACCESS',
        'CANARY TOKEN SCAN - REPORT ACCESS',
        'SECURITY ALERT STUDY - MONITORING ACCESS'
    ],
    
    'tracking_uids': {
        'study_instance_uid_prefix': '1.2.826.0.1.3680043.9.7891.',
        'series_instance_uid_prefix': '1.2.826.0.1.3680043.9.7892.',
        'sop_instance_uid_prefix': '1.2.826.0.1.3680043.9.7893.'
    },
    
    'tracking_urls': [
        'https://security-monitor.example.com/ht1',
        'https://security-monitor.example.com/ht2',
        'https://security-monitor.example.com/ht3',
        'https://security-monitor.example.com/ht4',
        'https://security-monitor.example.com/ht5'
    ],
    
    'tracking_tags': [
        (0x0008, 0x0090),  # Referring Physician's Name
        (0x0008, 0x1080),  # Admitting Diagnoses Description
        (0x0008, 0x4000),  # Comments
        (0x0010, 0x4000),  # Patient Comments
        (0x0032, 0x4000),  # Study Comments
    ]
}
