# app/rl_agent.py

import logging
from typing import Dict, Any, List
from datetime import datetime

class RLAgent:
    """
    A simple RL agent that adapts its threshold based on rewards,
    and tracks its threshold history over time for visualization.
    """
    def __init__(self, threshold: float = 0.5, lr: float = 0.1):
        self.threshold = threshold
        self.lr = lr
        # Initialize history with the starting threshold
        self.history: List[Dict[str, Any]] = [{
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "threshold": self.threshold
        }]
        logging.info(f"RLAgent initialized with threshold={self.threshold}, lr={self.lr}")

    def decide(self, features: Dict[str, Any]) -> str:
        """
        Returns "block" if time_to_submit < threshold, else "allow".
        """
        t = features.get("time_to_submit", 0.0)
        return "block" if t < self.threshold else "allow"

    def update(self, features: Dict[str, Any], action: str, reward: float):
        """
        Adjusts threshold toward (or away from) the observed time,
        records the new threshold in history.
        """
        t = features.get("time_to_submit", 0.0)
        old = self.threshold
        # Move threshold toward t if reward positive, away if negative
        self.threshold += self.lr * reward * (t - self.threshold)
        # Record the new threshold
        self.history.append({
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "threshold": round(self.threshold, 4)
        })
        logging.info(
            f"RLAgent.update: action={action}, reward={reward}, "
            f"time_to_submit={t}, threshold {old:.3f}→{self.threshold:.3f}"
        )

# Global instance
agent = RLAgent()
