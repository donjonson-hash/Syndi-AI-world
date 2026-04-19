"""
Tests for AI Agents
Тесты для AI-агентов Syndi
"""

import pytest
import pytest_asyncio
from agents import get_kristina, AgentResponse
from agents.base import AgentRole, MessageType, AgentMemory


class TestKristinaAgent:
    """Тесты для агента Кристины"""
    
    @pytest.fixture
    def kristina(self):
        agent = get_kristina()
        # Очищаем память перед тестами
        agent.memories = {}
        return agent
    
    @pytest.fixture
    def user_id(self):
        import uuid
        return f"test_user_{uuid.uuid4().hex[:8]}"
    
    @pytest.mark.asyncio
    async def test_agent_info(self, kristina):
        """Проверка информации об агенте"""
        info = kristina.get_info()
        
        assert info["id"] == "kristina_ux_001"
        assert info["name"] == "Кристина"
        assert info["role"] == "ux_designer"
        assert len(info["expertise"]) == 9
        assert "UX Design" in info["expertise"]
    
    @pytest.mark.asyncio
    async def test_greeting_response(self, kristina, user_id):
        """Проверка приветственного ответа"""
        response = await kristina.process_message(user_id, "Привет!")
        
        assert isinstance(response, AgentResponse)
        assert len(response.content) > 0
        assert "Кристина" in response.content or "привет" in response.content.lower()
    
    @pytest.mark.asyncio
    async def test_research_question(self, kristina, user_id):
        """Проверка ответа на вопрос об исследовании"""
        # Сначала приветствуемся
        await kristina.process_message(user_id, "Привет!")
        
        # Затем задаём вопрос
        response = await kristina.process_message(
            user_id, 
            "Как провести исследование пользователей?"
        )
        
        assert isinstance(response, AgentResponse)
        assert "исследован" in response.content.lower() or "пользовател" in response.content.lower()
        assert len(response.suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_prototype_question(self, kristina, user_id):
        """Проверка ответа на вопрос о прототипировании"""
        # Сначала приветствуемся
        await kristina.process_message(user_id, "Привет!")
        
        # Затем задаём вопрос
        response = await kristina.process_message(
            user_id,
            "Нужно создать прототип"
        )
        
        assert isinstance(response, AgentResponse)
        assert "прототип" in response.content.lower()
    
    @pytest.mark.asyncio
    async def test_memory_persistence(self, kristina, user_id):
        """Проверка сохранения контекста в памяти"""
        # Первое сообщение
        await kristina.process_message(user_id, "Привет!")
        
        # Второе сообщение
        await kristina.process_message(user_id, "Как дела?")
        
        # Проверяем память
        memory = kristina.get_memory(user_id)
        assert len(memory.messages) == 4  # 2 user + 2 assistant
    
    @pytest.mark.asyncio
    async def test_message_type_detection(self, kristina):
        """Проверка определения типа сообщения"""
        assert kristina._detect_message_type("Как написать код?") == MessageType.CODE
        assert kristina._detect_message_type("Сделай дизайн") == MessageType.DESIGN
        assert kristina._detect_message_type("Дай совет") == MessageType.ADVICE
        assert kristina._detect_message_type("Что думаешь?") == MessageType.QUESTION
    
    @pytest.mark.asyncio
    async def test_response_has_suggestions(self, kristina, user_id):
        """Проверка наличия предложений в ответе"""
        response = await kristina.process_message(
            user_id,
            "Начинаю новый проект"
        )
        
        assert len(response.suggestions) > 0
        assert all(isinstance(s, str) for s in response.suggestions)
    
    @pytest.mark.asyncio
    async def test_response_has_actions(self, kristina, user_id):
        """Проверка наличия действий в ответе"""
        response = await kristina.process_message(user_id, "Привет!")
        
        assert len(response.actions) > 0
        assert all("type" in a for a in response.actions)
        assert all("label" in a for a in response.actions)


class TestAgentMemory:
    """Тесты для памяти агента"""
    
    def test_memory_creation(self):
        """Проверка создания памяти"""
        memory = AgentMemory(user_id="test_001")
        
        assert memory.user_id == "test_001"
        assert len(memory.messages) == 0
        assert memory.user_profile is None
    
    def test_add_message(self):
        """Проверка добавления сообщения"""
        memory = AgentMemory(user_id="test_001")
        
        memory.add_message("user", "Привет!")
        assert len(memory.messages) == 1
        assert memory.messages[0]["role"] == "user"
        assert memory.messages[0]["content"] == "Привет!"
    
    def test_get_context(self):
        """Проверка получения контекста"""
        memory = AgentMemory(user_id="test_001")
        
        # Добавляем 15 сообщений
        for i in range(15):
            memory.add_message("user", f"Сообщение {i}")
        
        # Получаем последние 5
        context = memory.get_context(limit=5)
        assert len(context) == 5
    
    def test_memory_limit(self):
        """Проверка ограничения размера памяти"""
        memory = AgentMemory(user_id="test_001")
        
        # Добавляем 60 сообщений
        for i in range(60):
            memory.add_message("user", f"Сообщение {i}")
        
        # Память должна быть ограничена 50
        assert len(memory.messages) == 50
    
    def test_clear_memory(self):
        """Проверка очистки памяти"""
        memory = AgentMemory(user_id="test_001")
        
        memory.add_message("user", "Привет!")
        memory.user_profile = {"name": "Test"}
        memory.project_context = {"name": "Project"}
        
        memory.clear()
        
        assert len(memory.messages) == 0
        assert memory.project_context is None


class TestAgentRole:
    """Тесты для ролей агентов"""
    
    def test_agent_roles(self):
        """Проверка всех ролей агентов"""
        roles = list(AgentRole)
        
        assert AgentRole.UX_DESIGNER in roles
        assert AgentRole.DEVELOPER in roles
        assert AgentRole.PRODUCT_MANAGER in roles
        assert AgentRole.MARKETING in roles
        assert AgentRole.MENTOR in roles
        assert AgentRole.GENERAL in roles
    
    def test_agent_role_values(self):
        """Проверка значений ролей"""
        assert AgentRole.UX_DESIGNER.value == "ux_designer"
        assert AgentRole.DEVELOPER.value == "developer"
        assert AgentRole.PRODUCT_MANAGER.value == "product_manager"


class TestMessageType:
    """Тесты для типов сообщений"""
    
    def test_message_types(self):
        """Проверка всех типов сообщений"""
        types = list(MessageType)
        
        assert MessageType.TEXT in types
        assert MessageType.CODE in types
        assert MessageType.DESIGN in types
        assert MessageType.ADVICE in types
        assert MessageType.QUESTION in types
        assert MessageType.FEEDBACK in types
