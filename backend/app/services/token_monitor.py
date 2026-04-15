import json
from datetime import datetime
from pathlib import Path
from typing import Dict


class TokenMonitor:
    def __init__(self, log_file: str = "logs/token_usage.jsonl", daily_limit: int = 100000):
        self.log_file = Path(log_file)
        self.daily_limit = daily_limit
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def record_usage(self, operation: str, tokens_used: int, estimated_cost: float) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "tokens_used": tokens_used,
            "estimated_cost": estimated_cost,
        }
        with self.log_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_summary(self) -> Dict:
        today = datetime.now().strftime("%Y-%m-%d")
        total_tokens = 0
        total_cost = 0.0

        if self.log_file.exists():
            with self.log_file.open("r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    if record.get("timestamp", "").startswith(today):
                        total_tokens += int(record.get("tokens_used", 0))
                        total_cost += float(record.get("estimated_cost", 0.0))

        return {
            "date": today,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 3),
            "remaining": max(0, self.daily_limit - total_tokens),
        }
