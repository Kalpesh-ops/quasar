from typing import List, Literal, Optional
from pydantic import Field
from openenv.core.env_server import Action, Observation

class QuasarReward(Observation):
    score: float = Field(..., ge=0.0, le=1.0)

class TrafficLog(Observation):
    packet_id: str
    source_ip: str
    endpoint: str
    payload_body: str
    suspicion_score: float = Field(default=0.0)

class QuasarObservation(Observation):
    recent_traffic: List[TrafficLog]
    database_integrity_score: float
    active_firewall_rules: List[str] = Field(default_factory=list)
    reward: QuasarReward = Field(default_factory=lambda: QuasarReward(score=0.0))
    done: bool = False

class QuasarAction(Action):
    command: Literal["allow_packet", "flag_packet", "isolate_ip", "pass"]
    target_id: Optional[str] = None