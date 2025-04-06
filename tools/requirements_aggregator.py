import json
from langchain.tools import Tool


def requirements_aggregator_logic(input_text: str) -> str:
    """
    Агрегирует извлечённые требования в единый документ с указанием источников.

    Ожидаемый формат входных данных (JSON-строка):
    {
      "extracted_requirements": [
          {"req": "Система должна обеспечивать быстрый отклик.", "source": "Email №1"},
          {"req": "Пользователь должен иметь возможность изменить пароль.", "source": "Transcript №2"}
      ]
    }

    Пример выхода:
    {
      "aggregated_requirements": "1. Система должна обеспечивать быстрый отклик (Источник: Email №1)\n2. Пользователь должен иметь возможность изменить пароль (Источник: Transcript №2)",
      "status": "OK"
    }

    Если входные данные некорректны или список требований пустой, возвращается JSON с описанием ошибки.
    """
    try:
        data = json.loads(input_text)
        requirements = data.get("extracted_requirements", [])

        if not requirements:
            return json.dumps({
                "status": "error",
                "message": "Нет извлеченных требований для агрегации."
            }, ensure_ascii=False)

        aggregated_list = []
        for idx, req_item in enumerate(requirements, 1):
            req_text = req_item.get("req", "").strip()
            source = req_item.get("source", "Неизвестный источник")
            aggregated_list.append(f"{idx}. {req_text} (Источник: {source})")

        aggregated_requirements = "\n".join(aggregated_list)
        output = {
            "aggregated_requirements": aggregated_requirements,
            "status": "OK"
        }
        return json.dumps(output, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)


# Создаем инструмент requirements_aggregator, который можно привязать к LLM через bind_tools
requirements_aggregator_tool = Tool(
    name="requirements_aggregator",
    func=requirements_aggregator_logic,
    description=(
        "Агрегирует извлеченные требования в единый документ с указанием источников. "
        "Принимает JSON-строку с ключом 'extracted_requirements', содержащим список объектов, "
        "где каждый объект имеет поля 'req' (текст требования) и 'source' (источник). "
        "Выдает JSON-строку с ключом 'aggregated_requirements'."
    )
)
