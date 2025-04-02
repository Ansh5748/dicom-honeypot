import logging
import os
import socket
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional

from pydicom.dataset import Dataset
from pynetdicom import AE, evt, AllStoragePresentationContexts, debug_logger
from pynetdicom.sop_class import Verification

from app.core.elasticsearch_client import ElasticsearchClient
from app.utils.logging_utils import setup_logging
from app.models.event import DicomEvent
from app.utils.honeytoken_generator import create_honeytoken_dataset
from app.config.dicom_config import DICOM_CONFIG

logger = setup_logging()

if os.environ.get('DEBUG', 'False').lower() == 'true':
    debug_logger()

class DicomHoneypot:
    
    def __init__(self):
        self.ae = AE(ae_title=DICOM_CONFIG['ae_title'])
        self.port = DICOM_CONFIG['port']
        self.honeytoken_datasets = self._create_honeytoken_datasets()
        self.elasticsearch = ElasticsearchClient()
        self.active_connections = {}
        self.connection_lock = threading.Lock()
        
    def _create_honeytoken_datasets(self) -> Dict[str, Dataset]:
        datasets = {}
        for i in range(DICOM_CONFIG['num_honeytokens']):
            dataset = create_honeytoken_dataset(f"HONEYTOKEN-{i+1}")
            datasets[dataset.SOPInstanceUID] = dataset
        return datasets
    
    def start(self):
        self.ae.add_supported_context(Verification)
        for context in AllStoragePresentationContexts:
            self.ae.add_supported_context(context)
        
        handlers = [
            (evt.EVT_C_ECHO, self._handle_c_echo),
            (evt.EVT_C_FIND, self._handle_c_find),
            (evt.EVT_C_GET, self._handle_c_get),
            (evt.EVT_C_MOVE, self._handle_c_move),
            (evt.EVT_C_STORE, self._handle_c_store),
            (evt.EVT_ACCEPTED, self._handle_accepted),
            (evt.EVT_REJECTED, self._handle_rejected),
            (evt.EVT_RELEASED, self._handle_released),
            (evt.EVT_ABORTED, self._handle_aborted),
            (evt.EVT_ESTABLISHED, self._handle_established),
        ]
        
        for event, handler in handlers:
            self.ae.add_handler(event, handler)
        
        logger.info(f"Starting DICOM honeypot server on port {self.port}")
        self.ae.start_server(("0.0.0.0", self.port), block=True)
    
    def _log_event(self, event_type: str, event_data: Dict[str, Any], 
                   association=None, client_ip: Optional[str] = None):
        
        if association and not client_ip:
            client_ip = association.requestor.address
            
        event = DicomEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            client_ip=client_ip,
            client_ae_title=association.requestor.ae_title if association else None,
            called_ae_title=association.acceptor.ae_title if association else None,
            event_data=event_data
        )
        
        logger.info(event.dict())
        
        try:
            self.elasticsearch.index_event(event.dict())
        except Exception as e:
            logger.error(f"Failed to send event to Elasticsearch: {e}")
    
    def _handle_c_echo(self, event):
        association = event.assoc
        self._log_event("C-ECHO", {
            "message": "C-ECHO request received"
        }, association)
        return 0x0000  # Success
    
    def _handle_c_find(self, event):
        association = event.assoc
        request = event.request
        
        self._log_event("C-FIND", {
            "message": "C-FIND request received",
            "query_dataset": str(request.identifier)
        }, association)
        
        # Return honeytoken datasets as results
        for dataset in self.honeytoken_datasets.values():
            yield 0x0000, dataset
    
    def _handle_c_get(self, event):
        """Handle C-GET requests."""
        association = event.assoc
        request = event.request
        
        self._log_event("C-GET", {
            "message": "C-GET request received",
            "query_dataset": str(request.identifier)
        }, association)
        
        # Return honeytoken datasets
        yield from ((0x0000, dataset) for dataset in self.honeytoken_datasets.values())
    
    def _handle_c_move(self, event):
        association = event.assoc
        request = event.request
        
        self._log_event("C-MOVE", {
            "message": "C-MOVE request received",
            "query_dataset": str(request.identifier),
            "destination": request.move_destination
        }, association)
        
        yield 0x0000, None
    
    def _handle_c_store(self, event):
        """Handle C-STORE requests."""
        association = event.assoc
        request = event.request
        
        self._log_event("C-STORE", {
            "message": "C-STORE request received",
            "sop_class_uid": request.dataset.SOPClassUID,
            "sop_instance_uid": request.dataset.SOPInstanceUID,
            "dataset_summary": str(request.dataset)
        }, association)
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            client_ip = association.requestor.address.replace('.', '_')
            filename = f"/app/data/received_{client_ip}_{timestamp}.dcm"
            request.dataset.save_as(filename)
            logger.info(f"Saved received dataset to {filename}")
        except Exception as e:
            logger.error(f"Failed to save received dataset: {e}")
        
        return 0x0000  # Success
    
    def _handle_accepted(self, event):
        """Handle association accepted events."""
        association = event.assoc
        self._log_event("ASSOCIATION_ACCEPTED", {
            "message": "Association accepted"
        }, association)
    
    def _handle_rejected(self, event):
        """Handle association rejected events."""
        association = event.assoc
        self._log_event("ASSOCIATION_REJECTED", {
            "message": "Association rejected",
            "reason": event.reject_info
        }, association)
    
    def _handle_released(self, event):
        """Handle association released events."""
        association = event.assoc
        self._log_event("ASSOCIATION_RELEASED", {
            "message": "Association released"
        }, association)
        
        with self.connection_lock:
            client_addr = association.requestor.address
            if client_addr in self.active_connections:
                del self.active_connections[client_addr]
    
    def _handle_aborted(self, event):
        association = event.assoc
        self._log_event("ASSOCIATION_ABORTED", {
            "message": "Association aborted",
            "source": event.source,
            "reason": event.reason
        }, association)
        
        with self.connection_lock:
            client_addr = association.requestor.address
            if client_addr in self.active_connections:
                del self.active_connections[client_addr]
    
    def _handle_established(self, event):
        """Handle association established events."""
        association = event.assoc
        client_addr = association.requestor.address
        client_ae = association.requestor.ae_title
        
        with self.connection_lock:
            self.active_connections[client_addr] = {
                'ae_title': client_ae,
                'established_time': datetime.utcnow().isoformat(),
                'association': association
            }
        
        self._log_event("ASSOCIATION_ESTABLISHED", {
            "message": "Association established",
            "presentation_contexts": [
                {
                    "abstract_syntax": str(cx.abstract_syntax),
                    "transfer_syntax": [str(ts) for ts in cx.transfer_syntax]
                }
                for cx in association.accepted_contexts
            ]
        }, association)


def main():
    try:
        honeypot = DicomHoneypot()
        honeypot.start()
    except KeyboardInterrupt:
        logger.info("DICOM honeypot server stopped by user")
    except Exception as e:
        logger.error(f"DICOM honeypot server error: {e}")


if __name__ == "__main__":
    main()