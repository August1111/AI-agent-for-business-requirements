from langchain_gigachat.chat_models import GigaChat
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
import dotenv
from langchain_core.tools import Tool
import os
from uuid import uuid4
from langchain_core.prompts import ChatPromptTemplate
import re
from langchain_core.runnables import RunnableLambda


def extract_folder_path(user_query: str) -> tuple[str, str]:
    """Извлекает путь к папке из запроса пользователя"""
    pattern = r"(?:Папка|папке)[:\s]\s*([A-Za-z]:[\\\/].*?)(?:\s|$)"
    match = re.search(pattern, user_query)
    if not match:
        raise ValueError("Путь к папке не указан!")
    folder_path = match.group(1).replace("\\", "/")
    clean_query = user_query[:match.start()].strip()
    return clean_query, folder_path

def files_numerator(folder_path: str) -> int:
    try:
        files = os.listdir(folder_path)
        count = sum(1 for file in files if os.path.isfile(os.path.join(folder_path, file)))
        print(count)
        return count
    except Exception as e:
        print(f"Ошибка при доступе к папке {folder_path}: {e}")
        print(0)
        return 0

  
def requirements_agregator(folder_path: str) -> str:
    try:
        # Получаем список файлов (без папок), отсортированный по имени
        files = sorted(
            [f for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f))]
        )

        if not files:
            return "Нет доступных файлов для обработки."

        # Берём первый файл по алфавиту
        file_name = files[0]
        file_path = os.path.join(folder_path, file_name)

        # Чтение содержимого файла
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Перемещаем файл в папку processed
        processed_folder = os.path.join(folder_path, "processed")
        os.makedirs(processed_folder, exist_ok=True)

        new_path = os.path.join(processed_folder, file_name)
        os.rename(file_path, new_path)

        print(content)
        return content

    except Exception as e:
        return f"Ошибка при обработке файла: {str(e)}"



GIGA_KEY = dotenv.get_key('.env', 'GIGA_KEY')

# Создаем объект LLM для модели Gigachat 2 Max.
# Здесь можно задать max_tokens и другие параметры по необходимости.
llm = GigaChat(
        credentials=GIGA_KEY,  # замените на свой ключ
        verify_ssl_certs=False,
        scope="GIGACHAT_API_PERS",
        model="GigaChat-Max"
    )

tools = [
    Tool(
        name = 'files_numerator',
        func = files_numerator,
        description = """
            Подсчитывает количество файлов в указанной папке.
            Аргументы:
            folder_path: Путь к папке, в которой производится поиск файлов.
            Возвращает:
            Количество файлов (не считая папок) в указанной директории.
    """
    ),
    Tool(
        name = 'requirements_agregator',
        func = requirements_agregator,
        description = """
    Инструмент для обработки файла.

        Аргументы:
          folder_path: Путь к папке, где лежат файлы.
          
        Действия:
          1. Находит первый по алфавиту файл.
          2. Читает содержимое.
          3. Перемещает в "processed".
          4. Возвращает содержимое файла для анализа.
    """
    )
]

folder = 'C:/Users/artem/YandexDisk/AI_Agent_4BT/AI-agent-for-business-requirements/examples'

system_prompt = f"""
Ты бизнес-аналитик. Всегда действуй строго по инструкции:

1. Сначала вызывай инструмент 'files_numerator', передав ему путь к {folder}
2. Затем вызывай 'requirements_agregator' столько раз, сколько файлов было найдено, передав ему путь к {folder}.

Запрещено писать Python-код, делать предположения, просить уточнений, описывать алгоритмы.
Ты должен сразу выполнять действия с помощью инструментов.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "{input}")
])

processing_chain = prompt| llm.bind_tools(tools)


memory = MemorySaver()

agent_executor77 = create_react_agent(processing_chain
                                    , tools
                                    , checkpointer = memory
                                    )

thread_id = str(uuid4())
config = {"configurable": {"thread_id": thread_id}}

user_prompt = r"Напиши бизнес требования к продукту Монеты. Папка: C:\Users\artem\YandexDisk\AI_Agent_4BT\AI-agent-for-business-requirements\examples"  
print("Вызов агента...")
agent_executor77.invoke({"input": user_prompt}, config=config)

print("Чтение состояния памяти...")
result = memory.get(config)

print("Содержимое памяти:")
if isinstance(result, dict):
    for k, v in result.items():
        print(f"{k}:", v)
else:
    print(result)