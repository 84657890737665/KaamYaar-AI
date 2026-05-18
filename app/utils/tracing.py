import datetime
from typing import Dict, Any, List, Optional
import time

# In-memory store for traces, grouped by booking_id
_traces_store: Dict[str, Dict[str, Any]] = {}

def trace_agent_execution(
    agent_name: str,
    input_data: Any,
    output_data: Any,
    reasoning_steps: List[str] = None,
    latency: Optional[float] = None,
    confidence: Optional[float] = None,
    booking_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Logs an agent's execution details including structured JSON logs, timestamp, latency, and confidence scores.
    """
    if reasoning_steps is None:
        reasoning_steps = []
        
    trace_entry = {
        "type": "agent_execution",
        "agent_name": agent_name,
        "input_data": input_data,
        "output_data": output_data,
        "reasoning_steps": reasoning_steps,
        "latency_ms": latency,
        "confidence": confidence,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
    
    target_id = booking_id or "unassigned"
    
    if target_id not in _traces_store:
        _traces_store[target_id] = {"workflow_steps": [], "agent_executions": []}
        
    _traces_store[target_id]["agent_executions"].append(trace_entry)
    
    return trace_entry

def log_workflow_step(step_name: str, booking_id: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Tracks a complete user journey milestone.
    """
    if metadata is None:
        metadata = {}
        
    step_entry = {
        "type": "workflow_step",
        "step_name": step_name,
        "booking_id": booking_id,
        "metadata": metadata,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
    
    if booking_id not in _traces_store:
        _traces_store[booking_id] = {"workflow_steps": [], "agent_executions": []}
        
    _traces_store[booking_id]["workflow_steps"].append(step_entry)
    
    return step_entry

def export_trace(booking_id: str) -> Dict[str, Any]:
    """
    Returns the complete trace for a given booking_id.
    """
    return _traces_store.get(booking_id, {"workflow_steps": [], "agent_executions": []})

class Timer:
    """Helper class to measure latency for agent executions."""
    def __init__(self):
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        
    @property
    def elapsed_ms(self) -> float:
        if self.start_time is None:
            return 0.0
        return (time.time() - self.start_time) * 1000
