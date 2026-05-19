from typing import List, ClassVar, Optional
from pydantic import BaseModel, Field
from .base import BaseFirestoreModel

class Location(BaseModel):
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")

class Provider(BaseFirestoreModel):
    COLLECTION_NAME: ClassVar[str] = "providers"
    
    name: str = Field(..., description="Full name of the provider")
    service_type: str = Field(..., description="Type of service offered (e.g., Plumber, Electrician)")
    location: Location = Field(..., description="Current coordinates of the provider")
    address: str = Field(..., description="Full street address")
    rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Average user rating")
    on_time_score: float = Field(default=100.0, ge=0.0, le=100.0, description="Percentage of times the provider arrived on time")
    cancellation_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Percentage of bookings cancelled by the provider")
    base_rate: float = Field(..., gt=0.0, description="Base service rate in PKR")
    availability: bool = Field(default=True, description="Whether the provider is currently available for booking")
    skills: List[str] = Field(default_factory=list, description="List of specific skills or specializations")
    total_jobs: int = Field(default=0, ge=0, description="Total number of completed jobs")
    
    # Verification Fields
    cnic_front_url: Optional[str] = None
    cnic_back_url: Optional[str] = None
    face_photo_url: Optional[str] = None
    cnic_number: Optional[str] = Field(None, pattern=r"^\d{5}-\d{7}-\d{1}$", description="CNIC format: 12345-6789012-3")
    mobile_number: Optional[str] = Field(None, pattern=r"^03\d{2}-\d{7}$", description="Mobile format: 0300-1234567")
    is_cnic_verified: bool = False
    is_face_verified: bool = False
    verification_status: str = Field(default="pending", description="pending/verified/rejected")
    gender: str = Field(default="male", description="male/female")

class ProviderWithDistance(Provider):
    distance_text: str = Field(..., description="Distance formatted text (e.g., '5.2 km')")
    distance_value: int = Field(..., description="Distance in meters")
    duration_text: str = Field(..., description="Estimated travel time")
