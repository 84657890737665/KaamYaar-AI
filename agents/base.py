"""
agents/base.py

Defines the abstract base class that every agent in this project must implement.
This ensures a consistent interface across all 7 agents, making the orchestrator
layer straightforward to build.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    Every agent must declare its name and implement the `run` method.
    The `run` method accepts a free-form input dict and returns a result dict,
    keeping the interface flexible enough to accommodate any agent's needs.
    """

    name: str = "base_agent"

    @abstractmethod
    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the agent with the given input and return a structured result.

        Args:
            input_data: A dictionary of inputs relevant to this agent.

        Returns:
            A dictionary containing the agent's output.
        """
        ...
