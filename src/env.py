import asyncio
from typing import Any, Dict, Tuple
from pydantic import BaseModel
from openenv.core import Environment
from .models import QuasarObservation, QuasarAction, QuasarReward, TrafficLog
from .traffic_gen import generate_traffic


class StepResult(BaseModel):
    observation: QuasarObservation
    reward: QuasarReward | None = None
    done: bool = False

class QuasarEnv(Environment[QuasarObservation, QuasarAction, QuasarReward]):
    def __init__(self, task_name: str = "task_1_volumetric_flood"):
        super().__init__()
        self.task_name = task_name
        self.difficulty = self._get_difficulty()
        self.current_step = 0
        self.max_steps = 15
        
        # Core State
        self.database_integrity = 100.0
        self.active_firewall_rules = []
        self.recent_traffic = []
        
        # Grader Tracking
        self.poison_caught = 0
        self.poison_missed = 0
        self.false_positives = 0

    def _get_difficulty(self) -> str:
        if "1" in self.task_name: return "easy"
        if "2" in self.task_name: return "medium"
        return "hard"

    def _is_poisoned(self, payload: str) -> bool:
            return '"hidden_metadata":' in payload or "IGNORE" in payload.upper() or "OVERRIDE" in payload.upper() or "SYSTEM" in payload.upper()

    async def reset(self) -> StepResult:
        self.current_step = 0
        self.database_integrity = 100.0
        self.active_firewall_rules = []
        self.poison_caught = 0
        self.poison_missed = 0
        self.false_positives = 0
        
        # Start the simulation with immediate poison
        self.recent_traffic = generate_traffic(self.difficulty, num_packets=5, inject_poison=True)
        
        obs = QuasarObservation(
            recent_traffic=self.recent_traffic,
            database_integrity_score=self.database_integrity,
            active_firewall_rules=self.active_firewall_rules
        )
        return StepResult(observation=obs, done=False)

    async def step(self, action: QuasarAction) -> StepResult:
        self.current_step += 1
        step_reward = 0.0
        
        # --- 1. Process the AI's Action ---
        target = action.target_id
        command = action.command

        if command == "isolate_ip" and target:
            if target not in self.active_firewall_rules:
                self.active_firewall_rules.append(target)
                if self.difficulty == "easy" and target == "198.51.100.42":
                    step_reward += 0.5  # Great job blocking the noisy scanner
                    self.poison_caught += 1
                else:
                    step_reward -= 0.2  # Penalty: Blocked a random IP
                    self.false_positives += 1
        
        elif command == "flag_packet" and target:
            packet = next((p for p in self.recent_traffic if p.packet_id == target), None)
            if packet:
                if self._is_poisoned(packet.payload_body):
                    step_reward += 0.5 # Great job catching the stealth poison
                    self.poison_caught += 1
                else:
                    step_reward -= 0.3 # Penalty: Flagged legitimate enterprise data
                    self.false_positives += 1

        # --- 2. Evaluate Missed Poison ---
        for packet in self.recent_traffic:
            if packet.source_ip in self.active_firewall_rules:
                continue # Blocked at the firewall level
            
            if self._is_poisoned(packet.payload_body) and command != "flag_packet":
                self.database_integrity -= 15.0 # Massive damage to the database
                self.poison_missed += 1
                step_reward -= 0.4

        self.database_integrity = max(0.0, self.database_integrity)

        # --- 3. Determine Episode State ---
        done = self.current_step >= self.max_steps or self.database_integrity <= 0.0
        
        # Generate next batch of traffic (inject poison on even steps)
        inject = (self.current_step % 2 == 0) 
        self.recent_traffic = generate_traffic(self.difficulty, num_packets=5, inject_poison=inject)

        # --- 4. Final Grader Calculation ---
        if done:
            # Final score must be between 0.0 and 1.0
            base_score = (self.database_integrity / 100.0) * 0.6
            catch_rate = 0.0
            if (self.poison_caught + self.poison_missed) > 0:
                catch_rate = self.poison_caught / (self.poison_caught + self.poison_missed)
            
            final_score = base_score + (catch_rate * 0.4) - (self.false_positives * 0.1)
            step_reward = max(0.0, min(1.0, final_score)) 

        obs = QuasarObservation(
            recent_traffic=self.recent_traffic,
            database_integrity_score=self.database_integrity,
            active_firewall_rules=self.active_firewall_rules
        )
        
        return StepResult(
            observation=obs,
            reward=QuasarReward(score=max(0.0, min(1.0, step_reward))),
            done=done
        )

    async def state(self) -> StepResult:
        obs = QuasarObservation(
            recent_traffic=self.recent_traffic,
            database_integrity_score=self.database_integrity,
            active_firewall_rules=self.active_firewall_rules
        )
        return StepResult(observation=obs, done=self.current_step >= self.max_steps)