import asyncio
import math
import json
from typing import Any, Dict, Tuple
from openenv.core.env_server import Environment, State

try:
    from .models import QuasarObservation, QuasarAction, QuasarReward, TrafficLog
    from .traffic_gen import generate_traffic
except ImportError:
    from models import QuasarObservation, QuasarAction, QuasarReward, TrafficLog
    from traffic_gen import generate_traffic

class QuasarEnv(Environment[QuasarObservation, QuasarAction, QuasarReward]):
    def __init__(self, task_name: str = "task_1_volumetric_flood"):
        super().__init__()
        self.task_name = task_name
        self.difficulty = self._get_difficulty()
        self.current_step = 0
        self.max_steps = 15

        self.database_integrity = 100.0
        self.active_firewall_rules = []
        self.recent_traffic = []

        self.poison_caught = 0
        self.poison_missed = 0
        self.false_positives = 0

    def _get_difficulty(self) -> str:
        if "1" in self.task_name: return "easy"
        if "2" in self.task_name: return "medium"
        return "hard"

    def _calculate_entropy(self, text: str) -> float:
        if not text:
            return 0.0
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1
        entropy = 0.0
        for count in freq.values():
            p = count / len(text)
            entropy -= p * math.log2(p)
        return entropy

    def _is_poisoned(self, payload: str) -> bool:
        upper_payload = payload.upper()
        if any(flag in upper_payload for flag in ["IGNORE", "OVERRIDE", "SYSTEM"]):
            return True

        try:
            data = json.loads(payload)

            def extract_values(obj):
                vals = ""
                if isinstance(obj, dict):
                    for v in obj.values():
                        vals += extract_values(v)
                elif isinstance(obj, str):
                    vals += obj
                return vals

            pure_text = extract_values(data)
            entropy = self._calculate_entropy(pure_text)

            if entropy > 4.85:
                return True

        except json.JSONDecodeError:
            pass

        return False

    async def reset(self) -> QuasarObservation:
        self.current_step = 0
        self.database_integrity = 100.0
        self.active_firewall_rules = []
        self.poison_caught = 0
        self.poison_missed = 0
        self.false_positives = 0

        self.recent_traffic = generate_traffic(self.difficulty, num_packets=5, inject_poison=True)
        
        return QuasarObservation(
            recent_traffic=self.recent_traffic,
            database_integrity_score=self.database_integrity,
            active_firewall_rules=self.active_firewall_rules,
            reward=QuasarReward(score=0.0),
            done=False
        )

    async def step(self, action: QuasarAction) -> QuasarObservation:
        self.current_step += 1
        step_reward = 0.0

        target = action.target_id
        command = action.command

        if command == "isolate_ip" and target:
            if target not in self.active_firewall_rules:
                self.active_firewall_rules.append(target)
                if self.difficulty == "easy" and target == "198.51.100.42":
                    step_reward += 0.5
                    self.poison_caught += 1
                else:
                    step_reward -= 0.2
                    self.false_positives += 1
        
        elif command == "flag_packet" and target:
            packet = next((p for p in self.recent_traffic if p.packet_id == target), None)
            if packet:
                if self._is_poisoned(packet.payload_body):
                    step_reward += 0.5
                    self.poison_caught += 1
                else:
                    step_reward -= 0.3
                    self.false_positives += 1
            else:
                step_reward -= 0.1

        for packet in self.recent_traffic:
            if packet.source_ip in self.active_firewall_rules:
                continue
            
            if self._is_poisoned(packet.payload_body) and command != "flag_packet":
                self.database_integrity -= 15.0
                self.poison_missed += 1
                step_reward -= 0.4

        self.database_integrity = max(0.0, self.database_integrity)

        done = self.current_step >= self.max_steps or self.database_integrity <= 0.0

        inject = (self.current_step % 2 == 0) 
        self.recent_traffic = generate_traffic(self.difficulty, num_packets=5, inject_poison=inject)

        if done:
            base_score = (self.database_integrity / 100.0) * 0.6
            catch_rate = (self.poison_caught / (self.poison_caught + self.poison_missed)) if (self.poison_caught + self.poison_missed) > 0 else 0.0
            final_score = base_score + (catch_rate * 0.4) - (self.false_positives * 0.1)
            step_reward = max(0.0, min(1.0, final_score)) 

        self.recent_traffic = generate_traffic(self.difficulty, num_packets=5, inject_poison=(self.current_step % 2 == 0))

        return QuasarObservation(
            recent_traffic=self.recent_traffic,
            database_integrity_score=self.database_integrity,
            active_firewall_rules=self.active_firewall_rules,
            reward=QuasarReward(score=max(0.0, min(1.0, step_reward))),
            done=done
        )

    @property
    def state(self) -> State:
        return State(episode_id="quasar-session", step_count=self.current_step)