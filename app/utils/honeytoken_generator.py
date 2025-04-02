import random
import string
from datetime import datetime, timedelta
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid

def create_honeytoken_dataset(token_id):
    ds = Dataset()
    
    ds.SOPInstanceUID = generate_uid()
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    
    ds.PatientName = f"HONEYTOKEN^{token_id}"
    ds.PatientID = f"HT{token_id.replace('-', '')}"
    ds.PatientBirthDate = generate_random_date(min_years=20, max_years=80)
    ds.PatientSex = random.choice(["M", "F"])
    
    ds.StudyDate = generate_random_date(min_years=0, max_years=2)
    ds.StudyTime = generate_random_time()
    ds.StudyDescription = f"Honeytoken Study {token_id}"
    ds.AccessionNumber = generate_random_accession()
    
    ds.SeriesDate = ds.StudyDate
    ds.SeriesTime = ds.StudyTime
    ds.SeriesDescription = f"Honeytoken Series {token_id}"
    ds.Modality = "CT"
    
    ds.InstitutionName = "Honeypot Medical Center"
    ds.ReferringPhysicianName = "HONEYPOT^DOCTOR"
    
    return ds

def generate_random_date(min_years=0, max_years=5):
    """Generate a random date in DICOM format (YYYYMMDD)."""
    today = datetime.now()
    days_ago = random.randint(min_years * 365, max_years * 365)
    random_date = today - timedelta(days=days_ago)
    return random_date.strftime("%Y%m%d")

def generate_random_time():
    """Generate a random time in DICOM format (HHMMSS)."""
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    seconds = random.randint(0, 59)
    return f"{hours:02d}{minutes:02d}{seconds:02d}"

def generate_random_accession():
    """Generate a random accession number."""
    return ''.join(random.choices(string.digits, k=8))