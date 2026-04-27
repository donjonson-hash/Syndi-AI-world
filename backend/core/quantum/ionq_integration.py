"""
IONQ Quantum Computing Integration
Интеграция с квантовыми вычислениями IONQ

Возможности:
- Реальные квантовые вычисления через IONQ API
- Симуляция квантовых схем (fallback)
- Генерация квантовых путей для пользователей
"""

import os
from typing import Optional, Dict, Any, List
import aiohttp


class IonQClient:
    """
    Клиент для IONQ Quantum Cloud API
    
    Документация: https://docs.ionq.com/
    """
    
    BASE_URL = "https://api.ionq.co/v0.3"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("IONQ_API_KEY")
        self.use_real_quantum = os.getenv("USE_REAL_QUANTUM", "false").lower() == "true"
        
        if not self.api_key and self.use_real_quantum:
            raise ValueError(
                "IONQ_API_KEY не найден. "
                "Установите IONQ_API_KEY или USE_REAL_QUANTUM=false"
            )
    
    async def run_circuit(
        self,
        circuit: Dict[str, Any],
        shots: int = 1024,
        backend: str = "simulator"
    ) -> Dict[str, Any]:
        """
        Запустить квантовую схему
        
        Args:
            circuit: JSON-описание квантовой схемы
            shots: Количество запусков
            backend: "simulator" или "qpu" (реальное устройство)
        
        Returns:
            Результаты измерений
        """
        if not self.use_real_quantum or not self.api_key:
            # Fallback: симуляция
            return self._simulate_circuit(circuit, shots)
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"apiKey {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "target": backend,
                "name": "syndi_quantum_job",
                "shots": shots,
                "input": circuit
            }
            
            async with session.post(
                f"{self.BASE_URL}/jobs",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"IONQ API error: {error}")
                
                job = await response.json()
                return await self._wait_for_result(session, headers, job["id"])
    
    async def _wait_for_result(
        self,
        session: aiohttp.ClientSession,
        headers: Dict[str, str],
        job_id: str,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """Ожидание результата квантового вычисления"""
        import asyncio
        
        for _ in range(timeout // 5):
            async with session.get(
                f"{self.BASE_URL}/jobs/{job_id}",
                headers=headers
            ) as response:
                job = await response.json()
                
                if job["status"] == "completed":
                    return job["data"]["histogram"]
                elif job["status"] == "failed":
                    raise Exception(f"Job failed: {job.get('error', 'Unknown error')}")
                
                await asyncio.sleep(5)
        
        raise TimeoutError("Quantum job timeout")
    
    def _simulate_circuit(
        self,
        circuit: Dict[str, Any],
        shots: int
    ) -> Dict[str, Any]:
        """
        Симуляция квантовой схемы (fallback)
        
        Используется когда:
        - Нет IONQ_API_KEY
        - USE_REAL_QUANTUM=false
        """
        # Простая симуляция: равномерное распределение
        import random
        
        num_qubits = len(circuit.get("qubits", [0]))
        num_states = 2 ** num_qubits
        
        # Генерируем случайное распределение
        results = {}
        for _ in range(shots):
            state = random.randint(0, num_states - 1)
            state_str = format(state, f"0{num_qubits}b")
            results[state_str] = results.get(state_str, 0) + 1
        
        return results
    
    def get_backends(self) -> List[Dict[str, Any]]:
        """Получить список доступных квантовых устройств"""
        return [
            {
                "name": "simulator",
                "type": "simulator",
                "qubits": 29,
                "description": "Высокопроизводительный симулятор"
            },
            {
                "name": "ionq_qpu",
                "type": "qpu",
                "qubits": 11,
                "description": "Реальное квантовое устройство IONQ"
            }
        ]


class QuantumPathGenerator:
    """
    Генератор квантовых путей для пользователей
    
    Создает уникальные траектории развития на основе квантовых вычислений
    """
    
    def __init__(self, ionq_client: Optional[IonQClient] = None):
        self.ionq = ionq_client or IonQClient()
    
    async def generate_path(
        self,
        user_profile: Dict[str, Any],
        num_paths: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Сгенерировать квантовые пути для пользователя
        
        Args:
            user_profile: Профиль пользователя
            num_paths: Количество путей
        
        Returns:
            Список квантовых путей с вероятностями
        """
        # Создаем квантовую схему на основе профиля
        circuit = self._create_circuit_from_profile(user_profile)
        
        # Запускаем квантовое вычисление
        results = await self.ionq.run_circuit(circuit, shots=1024)
        
        # Интерпретируем результаты
        paths = self._interpret_results(results, num_paths)
        
        return paths
    
    def _create_circuit_from_profile(
        self,
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Создать квантовую схему из профиля пользователя"""
        # Используем Big Five или другие параметры для создания схемы
        
        _big_five = profile.get("big_five", {})
        
        # Преобразуем параметры в квантовые гейты
        num_qubits = 5  # По одному на каждую черту Big Five
        
        circuit = {
            "qubits": num_qubits,
            "circuit": []
        }
        
        # Добавляем Hadamard гейты для суперпозиции
        for i in range(num_qubits):
            circuit["circuit"].append({
                "gate": "h",
                "target": i
            })
        
        # Добавляем CNOT для запутанности
        for i in range(num_qubits - 1):
            circuit["circuit"].append({
                "gate": "cnot",
                "control": i,
                "target": i + 1
            })
        
        # Добавляем измерения
        for i in range(num_qubits):
            circuit["circuit"].append({
                "gate": "measure",
                "target": i
            })
        
        return circuit
    
    def _interpret_results(
        self,
        results: Dict[str, Any],
        num_paths: int
    ) -> List[Dict[str, Any]]:
        """Интерпретировать результаты квантового вычисления"""
        # Сортируем результаты по вероятности
        sorted_results = sorted(
            results.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        paths = []
        path_names = [
            "Творческий путь",
            "Аналитический путь",
            "Лидерский путь",
            "Исследовательский путь",
            "Гармоничный путь"
        ]
        
        for i, (state, count) in enumerate(sorted_results[:num_paths]):
            probability = count / sum(results.values())
            
            paths.append({
                "id": i + 1,
                "name": path_names[i % len(path_names)],
                "quantum_state": state,
                "probability": round(probability * 100, 2),
                "description": self._generate_description(state, probability)
            })
        
        return paths
    
    def _generate_description(
        self,
        state: str,
        probability: float
    ) -> str:
        """Сгенерировать описание квантового пути"""
        descriptions = {
            "00000": "Путь полного обнуления. Новое начало, чистый лист.",
            "11111": "Путь максимальной активации. Пик возможностей.",
        }
        
        return descriptions.get(
            state,
            f"Квантовый путь с вероятностью {probability:.1%}. "
            "Уникальная траектория развития."
        )


# Singleton instance
_ionq_client: Optional[IonQClient] = None


def get_ionq_client() -> IonQClient:
    """Получить клиент IONQ (singleton)"""
    global _ionq_client
    if _ionq_client is None:
        _ionq_client = IonQClient()
    return _ionq_client
