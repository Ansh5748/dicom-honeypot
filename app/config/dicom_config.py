
import os

DICOM_CONFIG = {
    "port": int(os.environ.get("DICOM_PORT", 11112)),
    "ae_title": os.environ.get("DICOM_AE_TITLE", "HONEYPOT"),
    "num_honeytokens": int(os.environ.get("NUM_HONEYTOKENS", 10)),
    "allowed_ae_titles": os.environ.get("ALLOWED_AE_TITLES", "").split(","),
    "max_associations": int(os.environ.get("MAX_ASSOCIATIONS", 10)),
    "timeout": int(os.environ.get("ASSOCIATION_TIMEOUT", 30))
}
