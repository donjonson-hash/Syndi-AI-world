# github_agent.py
from typing import Dict, Any, Optional
from base import AIAgent


class GitHubAgent(AIAgent):
    """
    AI-агент, специализирующийся на помощи в разработке ПО.
    Может анализировать код, давать рекомендации и взаимодействовать с GitHub.
    """

    def __init__(self, deepseek_api_key: str):
        system_prompt = """Ты — AI-ассистент для разработки программного обеспечения.
Твоя специализация:
- Анализ кода на Python, JavaScript, TypeScript, Rust, Go.
- Объяснение архитектурных решений.
- Поиск багов и уязвимостей.
- Генерация документации и тестов.
- Советы по рефакторингу и улучшению производительности.
- Работа с Git и GitHub: создание коммитов, PR, управление issues.

Всегда давай чёткие, лаконичные ответы с примерами кода, где это уместно.
Если вопрос не относится к разработке, вежливо укажи на это."""
        super().__init__(system_prompt=system_prompt, deepseek_api_key=deepseek_api_key)

    def process_message(
        self,
        user_id: str,
        message: str,
        repo_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Обрабатывает сообщение, при необходимости добавляя контекст репозитория.
        repo_context может содержать:
          - structure: str  (дерево каталогов)
          - files: dict {имя_файла: содержимое}
        """
        if repo_context:
            context_str = self._format_repo_context(repo_context)
            prompt = f"Контекст репозитория:\n{context_str}\n\nВопрос пользователя: {message}"
        else:
            prompt = message
        return super().process_message(user_id, prompt)

    def _format_repo_context(self, repo_context: Dict[str, Any]) -> str:
        """Форматирует метаданные репозитория в текстовый блок."""
        parts = []
        if "structure" in repo_context:
            parts.append(f"Структура проекта:\n{repo_context['structure']}")
        if "files" in repo_context:
            for filename, content in repo_context["files"].items():
                parts.append(f"Файл: {filename}\n```\n{content}\n```")
        return "\n\n".join(parts)
