import random
import logging

class IonQQuantum:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_circuit(self, profile: dict) -> list:
        seed = sum(ord(c) for c in str(profile)) % 100
        random.seed(seed)
        return [random.choice(["H", "X", "Y", "Z", "CX", "CCX"]) for _ in range(5)]

    def run_simulation(self, circuit: list) -> dict:
        counts = {0: 0, 1: 0, 2: 0, 3: 0}
        for gate in circuit:
            outcome = random.randint(0, 3)
            counts[outcome] += 1
        return counts

    async def run_on_quantum_computer(self, circuit: list) -> dict:
        logging.info(f"Отправка схемы на IonQ: {circuit}")
        return self.run_simulation(circuit)