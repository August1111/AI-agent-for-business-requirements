import json
from langchain.tools import Tool
from langchain_gigachat.tools.giga_tool import giga_tool

@giga_tool
def requirements_extractor(input_text: str) -> str:
    """
    Извлекает требования из блоков текста (chunk’ов).
    
    Ожидаемый формат входных данных (JSON-строка):
    {
      "chunks": [
         "Текст блока 1 ...",
         "Текст блока 2 ...",
         ...
      ]
    }
    
    Функция проходит по каждому блоку и проверяет его на наличие ключевых слов,
    характерных для формулировок требований (например, "должна", "необходимо", "требует", "обязан").
    
    Если в блоке присутствуют такие слова, блок добавляется как требование.
    Каждому требованию присваивается источник вида "Chunk #<номер>".
    
    Возвращает JSON-строку со следующей структурой:
    {
      "status": "OK" или "NO_REQUIREMENTS_FOUND",
      "extracted_requirements": [
           {"req": "Текст требования 1", "source": "Chunk #1"},
           {"req": "Текст требования 2", "source": "Chunk #3"},
           ...
      ]
    }
    """
    try:
        data = json.loads(input_text)
        chunks = data.get("chunks", [])
        
        if not chunks:
            return json.dumps({
                "status": "error",
                "message": "Нет блоков для извлечения требований."
            }, ensure_ascii=False)
        
        # Ключевые слова, характерные для формулировок требований
        keywords = ["должна", "необходимо", "требует", "обязан", "обязана", "требования"]
        extracted = []
        for idx, chunk in enumerate(chunks, 1):
            lower_chunk = chunk.lower()
            # Если хотя бы одно ключевое слово присутствует в блоке, считаем его требованием
            if any(keyword in lower_chunk for keyword in keywords):
                extracted.append({
                    "req": chunk.strip(),
                    "source": f"Chunk #{idx}"
                })
        
        status = "OK" if extracted else "NO_REQUIREMENTS_FOUND"
        output = {
            "status": status,
            "extracted_requirements": extracted
        }
        return json.dumps(output, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)

