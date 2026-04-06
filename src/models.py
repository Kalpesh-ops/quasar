from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class TrafficLog(BaseModel):
    packet_id: str
    source_ip: str
    endpoint: str
    payload_body: str
    suspicion_score: float = Field(default=0.0, description="Internal WAF metric. 0.0 is benign, 1.0 is highly suspicious.")

class QuasarObservation(BaseModel):
    recent_traffic: List[TrafficLog] = Field(..., description="Batch of the most recent JSON traffic hitting the pipeline.")
    database_integrity_score: float = Field(..., description="Current health of the backend model. Drops if poisoned data gets through.")
    active_firewall_rules: List[str] = Field(default_factory=list, description="List of currently isolated IPs.")

class QuasarAction(BaseModel):
    command: Literal["allow_packet", "flag_packet", "isolate_ip", "pass"] = Field(
        ..., 
        description="Action to take. 'pass' means do nothing and let traffic flow."
    )
    target_id: Optional[str] = Field(
        None, 
        description="The packet_id (for flag_packet) or source_ip (for isolate_ip). Leave null for 'allow_packet' or 'pass'."
    )

class QuasarReward(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)