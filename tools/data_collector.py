import json
from langchain.tools import Tool


def data_collector_logic(input_text: str) -> str:
    """
    Симулирует сбор данных из разных источников (email, чат, расшифровки)
    по заданному идентификатору задачи или пути к данным.

    Алгоритм:
      1. Принимает входной текст (например, идентификатор задачи или путь к источнику).
      2. Симулирует сбор данных, формируя список строк с данными.
      3. Возвращает JSON-строку с ключом "raw_data" и списком собранных сообщений.

    Пример входа:
      "TASK-123"

    Пример выхода:
      {"raw_data": [
          "Email from TASK-123: Письмо с описанием требований",
          "Chat message from TASK-123: Обсуждение деталей",
          "Transcript from TASK-123: Расшифровка встречи"
      ]}
    """
    task_id = input_text.strip()

    # Симуляция сбора данных (в реальном проекте здесь могут быть вызовы API, чтение файлов и т.п.)
    collected_data = [
        f"Email from {task_id}: Письмо с описанием требований",
        f"Chat message from {task_id}: Обсуждение деталей",
        f"Transcript from {task_id}: Расшифровка встречи"
    ]

    output = {"raw_data": collected_data}
    return json.dumps(output, ensure_ascii=False)


# Создаем инструмент для сбора данных, который можно привязать к LLM через bind_tools
data_collector_tool = Tool(
    name="data_collector",
    func=data_collector_logic,
    description=(
        "Собирает данные из различных источников (email, чат, расшифровки) по заданному идентификатору задачи или пути к данным. "
        "Вход: строка с идентификатором задачи или путем. Выход: JSON-строка с ключом 'raw_data' и списком собранных сообщений."
    )
)
