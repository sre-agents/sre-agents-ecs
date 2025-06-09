import json
import os
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_time():
    return datetime.now().strftime("%Y%m%d%H%M%S")


def is_json(string):
    try:
        json.loads(string)
        return True
    except json.JSONDecodeError:
        return False


class Sampler:
    def __init__(
        self,
        agent,
        dataset_name: str,
        dataset_path: str = "datasets",
    ):
        self.dataset_path = dataset_path
        self.dataset_name = dataset_name
        self.agent = agent

        self.schema = {
            "input": None,
            "response": None,
        }

        self.dump_path = self._dump_path()
        dir_path = os.path.dirname(self.dump_path)
        os.makedirs(dir_path, exist_ok=True)

        logger.info(f"Sampler initialized. the dump directory is {self.dump_path}")

    def _dump_path(self):
        # path: {datapath}/{dataset_name}/{agent.name}_{timestamp}.jsonl
        timestamp = get_time()
        return f"./{self.dataset_path}/{self.dataset_name}/{self.agent.name}-{timestamp}.jsonl"

    def add_sample(self, input: str, output: str):
        input = json.loads(input) if is_json(input) else input
        output = json.loads(output) if is_json(output) else output

        sample = {
            "input": input,
            "response": output,
        }

        logger.info(f"Dump sample to {self.dump_path}...")

        with open(self.dump_path, "a") as f:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")

        logger.info(f"Successfully dumped {self.agent.name} sample.")
