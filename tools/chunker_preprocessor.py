import json
from langchain.tools import Tool


def chunker_preprocessor_logic(text: str) -> str:
    """
    Функция для предварительной обработки текста и разбиения его на блоки (chunk’и).

    Алгоритм:
      1. Убирает лишние пробелы и переводит текст в единый формат.
      2. Пытается разбить текст на абзацы по двойным переводам строк.
      3. Если двойных переводов нет, то разбивает текст на предложения по символу точки.
      4. Возвращает JSON-строку с массивом блоков под ключом "chunks".

    Пример входа:
      "Это первое предложение. Это второе предложение. \n\n Это новый абзац."

    Пример выхода:
      {"chunks": ["Это первое предложение", "Это второе предложение", "Это новый абзац"]}
    """
    # Очистка текста: удаляем лишние пробелы
    cleaned_text = " ".join(text.split())

    # Пробуем разбить текст на абзацы, используя двойной перевод строки как разделитель
    if "\n\n" in text:
        chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    else:
        # Если нет явных абзацев, разбиваем по точке (сохраняя предложения)
        chunks = [chunk.strip() for chunk in cleaned_text.split(".") if chunk.strip()]

    # Собираем результат в виде словаря и возвращаем JSON-строку
    output = {"chunks": chunks}
    return json.dumps(output, ensure_ascii=False)


# Создаем инструмент, который можно привязать к LLM через bind_tools
chunker_preprocessor_tool = Tool(
    name="chunker_preprocessor",
    func=chunker_preprocessor_logic,
    description=(
        "Принимает входной текст и выполняет его предварительную обработку: очищает текст и разбивает его на логические блоки (chunk’и). "
        "Возвращает JSON-строку с массивом блоков под ключом 'chunks'."
    )
)
