from datetime import datetime, timezone
from typing import Optional, Any, Dict, ClassVar
from pydantic import BaseModel, Field, ConfigDict

class BaseFirestoreModel(BaseModel):
    id: Optional[str] = Field(default=None, description="Firestore document ID")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Collection name should be overridden by child classes
    COLLECTION_NAME: ClassVar[str] = ""

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for Firestore serialization."""
        # We typically don't store the id in the document data itself, 
        # as it's the document key in Firestore.
        return self.model_dump(exclude={"id"}, exclude_none=True)

    @classmethod
    def from_dict(cls, doc_id: str, data: Dict[str, Any]) -> "BaseFirestoreModel":
        """Create a model instance from Firestore document data and ID."""
        data["id"] = doc_id
        return cls(**data)
