import logging
import os
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/dicom_honeypot.log')
    ]
)
logger = logging.getLogger('dicom_honeypot')
try:
    from pynetdicom import AE, evt, StoragePresentationContexts
    from pynetdicom.sop_class import Verification
except ImportError as e:
    logger.error(f"Failed to import pynetdicom: {e}")
    sys.exit(1)

class StandaloneDicomServer:
    
    def __init__(self, ae_title="HONEYPOT", port=11112):
        self.ae = AE(ae_title=ae_title)
        self.port = port
        logger.info(f"Initialized DICOM server with AE Title: {ae_title}, Port: {port}")
        
    def start(self):
        try:
            self.ae.add_supported_context(Verification)
            logger.info("Added Verification SOP Class")
            
            for context in StoragePresentationContexts:
                self.ae.add_supported_context(context.abstract_syntax)
            logger.info("Added Storage SOP Classes")
            
            handlers = [(evt.EVT_C_ECHO, self._handle_c_echo)]
            
            logger.info(f"Starting DICOM server on port {self.port}")
            self.ae.start_server(("0.0.0.0", self.port), block=True, evt_handlers=handlers)
        except Exception as e:
            logger.error(f"Error starting DICOM server: {e}")
            raise
    
    def _handle_c_echo(self, event):
        """Handle C-ECHO requests."""
        logger.info(f"Received C-ECHO from {event.assoc.requestor.address}")
        return 0x0000  # Success

def main():
    os.makedirs('/app/logs', exist_ok=True)
    
    try:
        server = StandaloneDicomServer()
        server.start()
    except KeyboardInterrupt:
        logger.info("DICOM server stopped by user")
    except Exception as e:
        logger.error(f"DICOM server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()