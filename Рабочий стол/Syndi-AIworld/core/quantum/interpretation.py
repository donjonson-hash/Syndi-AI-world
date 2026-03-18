print("[DEBUG] Запуск interpretation.py")
def interpret_quantum_result(counts):
    """Преобразует квантовые данные в психологические инсайты"""
    total = sum(counts.values())
    probabilities = {k: v / total for k, v in counts.items()}

    return {
        "00": f"Консервативный путь ({probabilities.get(0, 0)*100:.1f}%)",
        "01": f"Творческая реализация ({probabilities.get(1, 0)*100:.1f}%)",
        "10": f"Рискованный выбор ({probabilities.get(2, 0)*100:.1f}%)",
        "11": f"Полная трансформация ({probabilities.get(3, 0)*100:.1f}%)",
    }
