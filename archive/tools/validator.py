import json
from langchain.tools import Tool


def validator_logic(input_text: str) -> str:
    """
    Валидирует агрегированный документ требований, проверяя,
    что все извлечённые требования присутствуют в агрегированном документе.

    Ожидаемый формат входных данных (JSON-строка):
    {
      "aggregated_requirements": "<текст агрегированного документа>",
      "extracted_requirements": [
          {"req": "Требование 1", "source": "Chunk #1"},
          {"req": "Требование 2", "source": "Chunk #3"},
          ...
      ]
    }

    Если для каждого требования из extracted_requirements его текст (поле "req")
    найден как подстрока в aggregated_requirements, возвращается:
      {"status": "OK", "message": "Все требования прошли валидацию."}

    Иначе возвращается:
      {"status": "validation_failed", "missing_requirements": [<список не найденных требований>],
       "message": "Некоторые требования отсутствуют в агрегированном документе."}

    При ошибке возвращается JSON с описанием ошибки.
    """
    try:
        data = json.loads(input_text)
        aggregated = data.get("aggregated_requirements", "")
        extracted = data.get("extracted_requirements", [])

        missing = []
        for req_item in extracted:
            req_text = req_item.get("req", "").strip()
            # Если текст требования не пустой и не найден в агрегированном документе,
            # добавляем его в список отсутствующих требований.
            if req_text and req_text not in aggregated:
                missing.append(req_text)

        if missing:
            output = {
                "status": "validation_failed",
                "missing_requirements": missing,
                "message": "Некоторые требования отсутствуют в агрегированном документе."
            }
        else:
            output = {
                "status": "OK",
                "message": "Все требования прошли валидацию."
            }
        return json.dumps(output, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)


# Создаем инструмент validator_tool, который можно привязать к LLM через bind_tools
validator_tool = Tool(
    name="validator",
    func=validator_logic,
    description=(
        "Проверяет агрегированный документ требований на соответствие извлеченным требованиям. "
        "Принимает JSON-строку с ключами 'aggregated_requirements' (текст документа) и 'extracted_requirements' (список объектов с полем 'req'). "
        "Возвращает JSON-строку с результатом валидации."
    )
)
