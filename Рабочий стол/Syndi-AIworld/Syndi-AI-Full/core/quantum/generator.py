from core.quantum.quantum_analysis import analyze_quantum_paths
from handlers.profile import UserProfile
print("[DEBUG] Запуск generator.py")


def generate_quantum_map(profile: UserProfile) -> str:
    """
    Генерирует текстовую карту квантовых сценариев жизни пользователя
    на основе анализа альтернативных путей.
    """
    paths = analyze_quantum_paths(profile)
    result = ["\n\U0001f52e Варианты вашей квантовой судьбы:\n"]

    for i, path in enumerate(paths, 1):
        result.append(f"{i}. \U0001f4d6 {path['title']}")
        result.append(f"   Путь: {path['description']}")
        result.append(f"   Конфликт: {path['conflict']}")
        result.append(f"   Урок: {path['lesson']}")
        result.append(f"   Персонаж: {path['avatar']}\n")

    result.append(
        "\U0001f680 Используйте один из этих путей как метафору для дня или медитации."
    )
    return "\n".join(result)