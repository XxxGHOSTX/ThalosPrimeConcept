"""
Provenance Record (PR) - Immutable chain linking artifacts to directives.

Links: Artifacts → HDR → pipeline version → container → signer.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import hashlib
import json


class ProvenanceRecord(BaseModel):
    """
    An immutable provenance record linking an artifact to its creation context.
    
    Links: Artifact → HDR → pipeline version → container → signer
    """
    
    record_id: str = Field(..., description="Unique identifier for this record")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    artifact_id: str = Field(..., description="ID of the artifact this record describes")
    hdr_id: str = Field(..., description="ID of the Human Directive Record")
    pipeline_version: str = Field(..., description="Version of the pipeline that created the artifact")
    container_info: Dict[str, str] = Field(..., description="Container/environment information")
    signer: str = Field(..., description="Identity of the signer")
    execution_metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    previous_record_id: Optional[str] = Field(None, description="ID of previous record in chain")
    record_hash: Optional[str] = Field(None, description="Hash of this record for integrity")
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def compute_hash(self) -> str:
        """
        Compute the hash of this record.
        
        Returns:
            SHA-256 hash of the record content
        """
        data = {
            "record_id": self.record_id,
            "timestamp": self.timestamp.isoformat(),
            "artifact_id": self.artifact_id,
            "hdr_id": self.hdr_id,
            "pipeline_version": self.pipeline_version,
            "container_info": self.container_info,
            "signer": self.signer,
            "execution_metadata": self.execution_metadata,
            "previous_record_id": self.previous_record_id,
        }
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def finalize(self) -> None:
        """Compute and set the record hash."""
        self.record_hash = self.compute_hash()
    
    def verify_integrity(self) -> bool:
        """
        Verify the integrity of this record.
        
        Returns:
            True if the hash matches the content, False otherwise
        """
        if not self.record_hash:
            return False
        return self.record_hash == self.compute_hash()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp.isoformat(),
            "artifact_id": self.artifact_id,
            "hdr_id": self.hdr_id,
            "pipeline_version": self.pipeline_version,
            "container_info": self.container_info,
            "signer": self.signer,
            "execution_metadata": self.execution_metadata,
            "previous_record_id": self.previous_record_id,
            "record_hash": self.record_hash,
        }


class ProvenanceChain:
    """
    An immutable chain of provenance records.
    
    Maintains the full history of artifacts and their creation context.
    """
    
    def __init__(self):
        self.records: Dict[str, ProvenanceRecord] = {}
        self.chain_head: Optional[str] = None
    
    def add_record(self, record: ProvenanceRecord) -> None:
        """
        Add a provenance record to the chain.
        
        Args:
            record: ProvenanceRecord to add
        """
        # Verify previous record exists if specified
        if record.previous_record_id:
            if record.previous_record_id not in self.records:
                raise ValueError(f"Previous record {record.previous_record_id} not found")
            
            # Verify integrity of previous record
            prev_record = self.records[record.previous_record_id]
            if not prev_record.verify_integrity():
                raise ValueError(f"Previous record {record.previous_record_id} failed integrity check")
        
        # Finalize and add the record
        record.finalize()
        self.records[record.record_id] = record
        self.chain_head = record.record_id
    
    def get_record(self, record_id: str) -> Optional[ProvenanceRecord]:
        """
        Get a provenance record by ID.
        
        Args:
            record_id: ID of the record
            
        Returns:
            ProvenanceRecord if found, None otherwise
        """
        return self.records.get(record_id)
    
    def get_chain_for_artifact(self, artifact_id: str) -> List[ProvenanceRecord]:
        """
        Get the full provenance chain for an artifact.
        
        Args:
            artifact_id: ID of the artifact
            
        Returns:
            List of ProvenanceRecords in chronological order
        """
        chain = []
        for record in self.records.values():
            if record.artifact_id == artifact_id:
                chain.append(record)
        
        # Sort by timestamp
        chain.sort(key=lambda r: r.timestamp)
        return chain
    
    def get_lineage(self, record_id: str) -> List[ProvenanceRecord]:
        """
        Get the full lineage (chain) from a specific record back to the root.
        
        Args:
            record_id: ID of the record to trace back from
            
        Returns:
            List of ProvenanceRecords from root to the specified record
        """
        lineage = []
        current_id = record_id
        
        while current_id:
            record = self.records.get(current_id)
            if not record:
                break
            lineage.insert(0, record)
            current_id = record.previous_record_id
        
        return lineage
    
    def verify_chain(self) -> bool:
        """
        Verify the integrity of the entire chain.
        
        Returns:
            True if all records are valid and properly linked, False otherwise
        """
        for record in self.records.values():
            # Verify record integrity
            if not record.verify_integrity():
                return False
            
            # Verify link to previous record
            if record.previous_record_id:
                if record.previous_record_id not in self.records:
                    return False
        
        return True
    
    def export_chain(self) -> List[Dict[str, Any]]:
        """
        Export the entire chain as a list of dictionaries.
        
        Returns:
            List of record dictionaries
        """
        return [record.to_dict() for record in self.records.values()]
