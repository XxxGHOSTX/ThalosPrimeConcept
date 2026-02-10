"""
Artifact - Digital outputs with unique IDs and metadata.

Represents any digital output (code, model, simulation, claim) with tracking.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import hashlib
import json
from pathlib import Path


class Artifact(BaseModel):
    """
    A digital output with unique ID and metadata.
    
    Can represent code, models, simulations, claims, or any other digital output.
    """
    
    artifact_id: str = Field(..., description="Unique identifier for this artifact")
    artifact_type: str = Field(..., description="Type of artifact (code, model, simulation, claim, etc.)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    content_hash: str = Field(..., description="Hash of the artifact content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    content: Optional[Any] = Field(None, description="Actual content (optional)")
    content_path: Optional[str] = Field(None, description="Path to content file")
    parent_artifacts: List[str] = Field(default_factory=list, description="IDs of parent artifacts")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @staticmethod
    def compute_hash(content: Any) -> str:
        """
        Compute SHA-256 hash of content.
        
        Args:
            content: Content to hash (will be converted to string)
            
        Returns:
            Hex digest of the hash
        """
        if isinstance(content, bytes):
            data = content
        elif isinstance(content, str):
            data = content.encode('utf-8')
        else:
            data = str(content).encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    @classmethod
    def create_from_content(
        cls,
        artifact_id: str,
        artifact_type: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        parent_artifacts: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> "Artifact":
        """
        Create an artifact from content.
        
        Args:
            artifact_id: Unique identifier
            artifact_type: Type of artifact
            content: The actual content
            metadata: Additional metadata
            parent_artifacts: IDs of parent artifacts
            tags: Tags for categorization
            
        Returns:
            New Artifact instance
        """
        content_hash = cls.compute_hash(content)
        return cls(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            content_hash=content_hash,
            content=content,
            metadata=metadata or {},
            parent_artifacts=parent_artifacts or [],
            tags=tags or [],
        )
    
    @classmethod
    def create_from_file(
        cls,
        artifact_id: str,
        artifact_type: str,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_artifacts: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> "Artifact":
        """
        Create an artifact from a file.
        
        Args:
            artifact_id: Unique identifier
            artifact_type: Type of artifact
            file_path: Path to the file
            metadata: Additional metadata
            parent_artifacts: IDs of parent artifacts
            tags: Tags for categorization
            
        Returns:
            New Artifact instance
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = path.read_bytes()
        content_hash = cls.compute_hash(content)
        
        return cls(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            content_hash=content_hash,
            content_path=str(path.absolute()),
            metadata=metadata or {},
            parent_artifacts=parent_artifacts or [],
            tags=tags or [],
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "timestamp": self.timestamp.isoformat(),
            "content_hash": self.content_hash,
            "metadata": self.metadata,
            "content_path": self.content_path,
            "parent_artifacts": self.parent_artifacts,
            "tags": self.tags,
        }


class ArtifactManager:
    """
    Manager for storing and retrieving artifacts.
    """
    
    def __init__(self):
        self.artifacts: Dict[str, Artifact] = {}
    
    def register(self, artifact: Artifact) -> None:
        """
        Register an artifact.
        
        Args:
            artifact: Artifact to register
        """
        if artifact.artifact_id in self.artifacts:
            raise ValueError(f"Artifact {artifact.artifact_id} already registered")
        self.artifacts[artifact.artifact_id] = artifact
    
    def get(self, artifact_id: str) -> Optional[Artifact]:
        """
        Get an artifact by ID.
        
        Args:
            artifact_id: ID of the artifact
            
        Returns:
            Artifact if found, None otherwise
        """
        return self.artifacts.get(artifact_id)
    
    def find_by_type(self, artifact_type: str) -> List[Artifact]:
        """
        Find artifacts by type.
        
        Args:
            artifact_type: Type to search for
            
        Returns:
            List of matching artifacts
        """
        return [
            artifact for artifact in self.artifacts.values()
            if artifact.artifact_type == artifact_type
        ]
    
    def find_by_tag(self, tag: str) -> List[Artifact]:
        """
        Find artifacts by tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of matching artifacts
        """
        return [
            artifact for artifact in self.artifacts.values()
            if tag in artifact.tags
        ]
    
    def get_descendants(self, artifact_id: str) -> List[Artifact]:
        """
        Get all descendant artifacts (artifacts that depend on this one).
        
        Args:
            artifact_id: ID of the parent artifact
            
        Returns:
            List of descendant artifacts
        """
        descendants = []
        for artifact in self.artifacts.values():
            if artifact_id in artifact.parent_artifacts:
                descendants.append(artifact)
        return descendants
    
    def export_metadata(self, artifact_id: str) -> Dict[str, Any]:
        """
        Export artifact metadata.
        
        Args:
            artifact_id: ID of the artifact
            
        Returns:
            Dictionary with artifact metadata
        """
        artifact = self.get(artifact_id)
        if not artifact:
            raise ValueError(f"Artifact {artifact_id} not found")
        return artifact.to_dict()
