import json
from langchain.tools import Tool

def jira_uploader_logic(input_text: str) -> str:
    """
    Симулирует загрузку финального документа бизнес-требований в Jira.

    Ожидаемый формат входных данных (JSON-строка):
    {
        "ticket_id": "<идентификатор тикета>",
        "requirements": "<текст бизнес-требований>"
    }

    Пример входа:
      '{"ticket_id": "PROJ-123", "requirements": "Бизнес-требования: ..." }'

    Пример выхода:
      '{"status": "uploaded", "ticket_id": "PROJ-123", "message": "Business requirements uploaded successfully to ticket PROJ-123."}'

    Если происходит ошибка, возвращается JSON с информацией об ошибке.
    """
    try:
        data = json.loads(input_text)
        ticket_id = data.get("ticket_id", "UNKNOWN")
        requirements = data.get("requirements", "")

        # Здесь должна быть реализация вызова Jira API.
        # Для примера симулируем успешную загрузку:
        result = {
            "status": "uploaded",
            "ticket_id": ticket_id,
            "message": f"Business requirements uploaded successfully to ticket {ticket_id}."
        }
    except Exception as e:
        result = {
            "status": "error",
            "message": str(e)
        }
    return json.dumps(result, ensure_ascii=False)

# Создаем инструмент jira_uploader, который можно привязать к LLM через bind_tools
jira_uploader_tool = Tool(
    name="jira_uploader",
    func=jira_uploader_logic,
    description=(
        "Загружает финальный документ бизнес-требований в Jira. "
        "Вход: JSON-строка с ключами 'ticket_id' и 'requirements'. "
        "Выход: JSON-строка с подтверждением загрузки или описанием ошибки."
    )
)
