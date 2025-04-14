import json
from langchain_gigachat.tools.giga_tool import giga_tool
from langchain.text_splitter import RecursiveCharacterTextSplitter

@giga_tool
def chunker_preprocessor(input_json: dict) -> dict:
    """
    Функция для предварительной обработки текста с использованием RecursiveCharacterTextSplitter.

    Алгоритм работы:
      1. Принимает входной JSON-объект с ключом "text", содержащим исходный текст.
      2. Очищает текст от лишних пробелов, приводя его к единообразному виду.
      3. Делит текст на логические блоки (чанки) с помощью RecursiveCharacterTextSplitter, который использует
         набор разделителей (двойной перевод строки, одинарный перевод строки, точка, пробел и пустая строка)
         для сохранения семантической целостности.
      4. Возвращает результат в виде JSON-объекта, где массив чанков записан под ключом "chunks".

    Пример входных данных:
      {"text": "Это первое предложение. Это второе предложение. \n\n Это новый абзац."}

    Пример выходных данных:
      {"chunks": ["Это первое предложение. Это второе предложение.", "Это новый абзац."]}
    """
    text = input_json.get("text", "")
    # Приводим текст к единообразному виду, убирая лишние пробелы
    cleaned_text = " ".join(text.split())

    # Создаем экземпляр RecursiveCharacterTextSplitter с заданными параметрами
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    # Разбиваем очищенный текст на чанки
    chunks = splitter.split_text(cleaned_text)

    return {"chunks": chunks}


if __name__ == "__main__":
    # Пример входных данных в виде JSON-объекта (dict)
    input_data = {
        "text": "Это первое предложение. Это второе предложение. \n\n Это новый абзац."
    }

    # Вызов функции обработки текста
    result = chunker_preprocessor.invoke({"input_json": input_data})

    # Вывод результата в формате JSON с отступами для удобного чтения
    print("Результат:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
