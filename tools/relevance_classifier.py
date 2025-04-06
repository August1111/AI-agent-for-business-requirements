import json
from langchain.tools import Tool


def relevance_classifier_logic(input_text: str) -> str:
    """
    Функция для фильтрации исходных данных, полученных от data_collector.

    Принимает на вход JSON-строку с ключом "raw_data", содержащим список сообщений.
    Для каждого сообщения проверяет наличие ключевого слова "требование" (регистр не важен).

    Пример входа:
      '{"raw_data": ["Email from TASK-123: Письмо с описанием требований", "Chat message: Привет", "Transcript: Обсуждение деталей"]}'

    Пример выхода, если релевантные сообщения найдены:
      '{"status": "OK", "relevant_data": ["Email from TASK-123: Письмо с описанием требований"]}'

    Если релевантных сообщений не найдено, возвращается:
      '{"status": "NO_RELEVANT_DATA", "relevant_data": []}'
    """
    try:
        data = json.loads(input_text)
        raw_data = data.get("raw_data", [])

        # Простейшая логика фильтрации: если сообщение содержит слово "требование" (без учета регистра)
        relevant_data = [
            msg for msg in raw_data if "требование" in msg.lower()
        ]

        status = "OK" if relevant_data else "NO_RELEVANT_DATA"
        output = {"status": status, "relevant_data": relevant_data}
        return json.dumps(output, ensure_ascii=False)
    except Exception as e:
        # При ошибке возвращаем информацию об ошибке
        output = {"status": "error", "message": str(e)}
        return json.dumps(output, ensure_ascii=False)


# Создаем инструмент relevance_classifier_tool,
# который можно привязать к LLM через bind_tools.
relevance_classifier_tool = Tool(
    name="relevance_classifier",
    func=relevance_classifier_logic,
    description=(
        "Фильтрует исходные данные, полученные из data_collector. "
        "Принимает JSON-строку с ключом 'raw_data' (список сообщений) и возвращает JSON с ключом 'relevant_data', "
        "содержащим только те сообщения, которые содержат слово 'требование'."
    )
)
