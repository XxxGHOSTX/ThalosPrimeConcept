"""
Human Directive Record (HDR) - Signed, timestamped human directives.

Contains objectives, constraints, parameters, and success criteria.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import json
import base64


class HumanDirectiveRecord(BaseModel):
    """
    A signed, timestamped human directive containing objectives, constraints,
    parameters, and success criteria.
    """
    
    directive_id: str = Field(..., description="Unique identifier for this directive")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    objectives: List[str] = Field(..., description="List of objectives to achieve")
    constraints: List[str] = Field(default_factory=list, description="Constraints on execution")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Execution parameters")
    success_criteria: List[str] = Field(..., description="Criteria for success")
    signer: Optional[str] = Field(None, description="Identity of the signer")
    signature: Optional[str] = Field(None, description="Cryptographic signature")
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_signing_payload(self) -> bytes:
        """Generate the payload for signing."""
        data = {
            "directive_id": self.directive_id,
            "timestamp": self.timestamp.isoformat(),
            "objectives": self.objectives,
            "constraints": self.constraints,
            "parameters": self.parameters,
            "success_criteria": self.success_criteria,
        }
        return json.dumps(data, sort_keys=True).encode('utf-8')
    
    def sign(self, private_key: rsa.RSAPrivateKey, signer_id: str) -> None:
        """
        Sign the directive with a private key.
        
        Args:
            private_key: RSA private key for signing
            signer_id: Identity of the signer
        """
        payload = self.to_signing_payload()
        signature = private_key.sign(
            payload,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        self.signature = base64.b64encode(signature).decode('utf-8')
        self.signer = signer_id
    
    def verify(self, public_key: rsa.RSAPublicKey) -> bool:
        """
        Verify the signature of the directive.
        
        Args:
            public_key: RSA public key for verification
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.signature:
            return False
        
        try:
            signature = base64.b64decode(self.signature)
            payload = self.to_signing_payload()
            public_key.verify(
                signature,
                payload,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "directive_id": self.directive_id,
            "timestamp": self.timestamp.isoformat(),
            "objectives": self.objectives,
            "constraints": self.constraints,
            "parameters": self.parameters,
            "success_criteria": self.success_criteria,
            "signer": self.signer,
            "signature": self.signature,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HumanDirectiveRecord":
        """Create from dictionary representation."""
        data = data.copy()
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


def generate_keypair() -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """
    Generate an RSA keypair for signing directives.
    
    Returns:
        Tuple of (private_key, public_key)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key
