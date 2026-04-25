# main.py
import os
import uuid
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from github import Github

from big_five import BigFiveTest, BigFiveResult
from matching import MatchingEngine
from kristina import KristinaAgent
from github_agent import GitHubAgent

# -------------------------------------------------------------------
# Инициализация приложения
# -------------------------------------------------------------------
app = FastAPI(title="Syndi-AI", version="0.2.0")

# Временное in-memory хранилище
users_db: Dict[str, dict] = {}

# Инициализация движка матчинга и AI-агентов
matching_engine = MatchingEngine()

kristina_agent = KristinaAgent(
    deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", "")
)

github_agent = GitHubAgent(
    deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", "")
)

# -------------------------------------------------------------------
# Модели запросов/ответов
# -------------------------------------------------------------------
class UserCreate(BaseModel):
    name: str
    skills: List[str]
    interests: List[str]
    goals: str


class UserProfile(UserCreate):
    user_id: str
    big_five: Optional[BigFiveResult] = None


class TestSubmission(BaseModel):
    answers: List[int]  # список из 50 ответов (1–5)


class AgentChatRequest(BaseModel):
    user_id: str
    message: str


class GitHubChatRequest(BaseModel):
    user_id: str
    message: str
    repo_context: Optional[dict] = None


class GitHubActionRequest(BaseModel):
    user_token: str
    action: str  # "create_issue" | "list_files"
    repo_name: str
    payload: dict = {}


# -------------------------------------------------------------------
# Пользователи
# -------------------------------------------------------------------
@app.post("/users", response_model=UserProfile)
def create_user(user: UserCreate):
    user_id = str(uuid.uuid4())
    users_db[user_id] = {
        "user_id": user_id,
        "name": user.name,
        "skills": user.skills,
        "interests": user.interests,
        "goals": user.goals,
        "big_five": None,
    }
    return users_db[user_id]


@app.get("/users/{user_id}", response_model=UserProfile)
def get_user(user_id: str):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]


# -------------------------------------------------------------------
# Тест Big Five
# -------------------------------------------------------------------
@app.post("/users/{user_id}/test")
def submit_test(user_id: str, submission: TestSubmission):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    if len(submission.answers) != 50:
        raise HTTPException(status_code=400, detail="Expected 50 answers")
    test = BigFiveTest()
    result = test.calculate_scores(submission.answers)
    users_db[user_id]["big_five"] = result.dict()
    return {"message": "Test results saved", "big_five": result.dict()}


# -------------------------------------------------------------------
# Матчинг
# -------------------------------------------------------------------
@app.get("/matches/{user_id}")
def get_matches(user_id: str, top_k: int = 10):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    current_user = users_db[user_id]
    if not current_user.get("big_five"):
        raise HTTPException(status_code=400, detail="Complete Big Five test first")
    matches = matching_engine.find_matches(current_user, users_db, top_k=top_k)
    return {"matches": matches}


# -------------------------------------------------------------------
# Агент «Кристина»
# -------------------------------------------------------------------
@app.post("/agents/kristina/chat")
def chat_with_kristina(request: AgentChatRequest):
    if request.user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    response = kristina_agent.process_message(
        user_id=request.user_id,
        message=request.message
    )
    return {"response": response}


@app.get("/agents/kristina/history/{user_id}")
def get_kristina_history(user_id: str):
    history = kristina_agent.memories.get(user_id, [])
    return {"history": history}


# -------------------------------------------------------------------
# GitHub-агент
# -------------------------------------------------------------------
@app.post("/agents/github/chat")
def chat_with_github_agent(request: GitHubChatRequest):
    response = github_agent.process_message(
        user_id=request.user_id,
        message=request.message,
        repo_context=request.repo_context
    )
    return {"response": response}


@app.get("/agents/github/history/{user_id}")
def get_github_agent_history(user_id: str):
    history = github_agent.memories.get(user_id, [])
    return {"history": history}


# -------------------------------------------------------------------
# Прямые действия с GitHub
# -------------------------------------------------------------------
@app.post("/agents/github/action")
def github_action(request: GitHubActionRequest):
    try:
        g = Github(request.user_token)
        repo = g.get_repo(request.repo_name)
        if request.action == "create_issue":
            issue = repo.create_issue(
                title=request.payload["title"],
                body=request.payload.get("body", "")
            )
            return {"issue_url": issue.html_url}
        elif request.action == "list_files":
            contents = repo.get_contents("")
            return {"files": [c.name for c in contents]}
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported action: {request.action}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------
# Запуск (для отладки)
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
