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
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field  
import extract_msg
from langchain_core.tools import StructuredTool

GIGA_KEY = dotenv.get_key('.env', 'GIGA_KEY')

# Создаем экземпляр LLM для модели Gigachat 2 Max.
# Здесь можно задать max_tokens и другие параметры по необходимости.
llm = GigaChat(
        credentials=GIGA_KEY,  # нужно заменить на ключ
        verify_ssl_certs=False,
        scope="GIGACHAT_API_PERS",
        model="GigaChat-2-Max", # выбрал первую модель, а не вторую т.к. при использовании второй происходит переполнение стека 
        top_p=0.2,
        timeout = 1000
    )

#Задаём инструменты, которыми может пользоваться агент (в виде функций).
#Описания к ним ниже
def data_collector(folder_path: str) -> str:
    try:
        # Получаем список всех файлов (без папок), отсортированный по имени
        files = sorted(
            [f for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f))]
        )

        if not files:
            return "Нет доступных файлов для обработки."

        # Собираем содержимое
        combined_content = ""
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            
            if file_name.lower().endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    combined_content += f"{file_name}\n{content}\n\n"
            elif file_name.lower().endswith(".msg"):
                try:
                    msg = extract_msg.Message(file_path)
                    msg_subject = msg.subject or ""
                    msg_body = msg.body or ""
                    content = f"Subject: {msg_subject}\nBody:\n{msg_body}"
                    combined_content += f"{file_name}\n{content}\n\n"
                except Exception as msg_error:
                    combined_content += f"{file_name}\nОшибка при чтении MSG файла: {msg_error}\n\n"

        # print(combined_content.strip())
        return combined_content.strip()
    
    except Exception as e:
        return f"Ошибка при обработке файлов: {str(e)}"
    
def get_requirements(text: str, folder_path: str) -> str:

    try:
        # Создаем папку, если её нет
        os.makedirs(folder_path, exist_ok=True)

        # Формируем путь к файлу
        file_path = os.path.join(folder_path, "final_document.txt")

        # Сохраняем текст в файл
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text.strip())

        print(f"Документ успешно сохранён в: {file_path}")
        return file_path
    
    except Exception as e:
        print(f"❗Ошибка при сохранении файла: {str(e)}")
        return ""

def extract_requirements(text: str, product: str) -> str:
    # Здесь можно заморочиться, но для старта достаточно просто вернуть обработанный текст
    return f"Требования к продукту {product}:\n\n{text}"

#Это для того, чтобы чётко прописать какие аргументы инструмент должен принимать на вход ( без этого агент выполняет get_requirements с ошибкой)
class GetRequirementsInput(BaseModel):
    text: str = Field(description="Текст для сохранения")
    folder_path: str = Field(description="Путь к папке")

class ExtractRequirementsInput(BaseModel):
    text: str = Field(description="Текст, полученный от data_collector")
    product: str = Field(description="Название продукта")

class DataCollectorInput(BaseModel):
    folder_path: str = Field(description="Путь к папке с файлами")


extract_requirements_tool = StructuredTool(
    name="extract_requirements",
    func=extract_requirements,
    description=(
        "Выделяет бизнес‑требования, относящиеся к заданному продукту, "
        "из предоставленного текста и указывает источник каждого требования."
    ),
    args_schema=ExtractRequirementsInput,
)

data_collector_tool = StructuredTool(
    name="data_collector",
    func=data_collector,
    args_schema=DataCollectorInput,
    description=(
        "Собирает содержимое всех .txt и .msg файлов в указанной папке "
        "и возвращает объединённый текст с наименованиями и содержимым всех файлов в папке."
    ),
)

#Создаю массив tools с инструментами (Tool) для агента. 
#Можно объявляться инструменты и через декоратор @tool (или @giga_tool) перед функцией, но у меня это, к сожалению, не работает. Поэтому вручную.
tools = [
    data_collector_tool,
    StructuredTool (
        name = 'get_requirements',
        func = get_requirements,
        description = """
            Компилирует текст с требованиями в один чёткий и хорошо структурированный документ. На каждое требование обязательно должна быть ссылка из какого файла оно взято. Сохраняет получившийся документ в указанный файл внутри заданной папки.
    
            Аргументы:
                text (str): Текст, который необходимо скомпилировать, структурировать и сохранить.
                folder_path (str): Путь к папке.
                filename (str): Название файла (по умолчанию "final_document.txt").
            
            Возвращает:
                str: Полный путь к сохраненному файлу.
    """,
        args_schema=GetRequirementsInput
    ),
    extract_requirements_tool
]

#Тут пока явно объявляю переменные, для промта агенту т.к. пока не научился читать их с пользовательского запроса
folder = 'C:/Users/artem/YandexDisk/AI_Agent_4BT/AI-agent-for-business-requirements/examples'
product = 'Монеты'

#Промт - синтрукция для агента. get_requirements - он так и не выполняет.
system_prompt = f"""
Ты бизнес-аналитик. Всегда действуй строго по инструкции. :

1. Сначала вызови инструмент 'data_collector', передав ему путь к {folder}.
   Получи объединённый текст всех файлов.

2. Затем вызови инструмент 'extract_requirements', передав ему:
   - текст, который ты получил от 'data_collector'
   - название продукта: {product}
   
   Этот инструмент выделит бизнес-требования, относящиеся к продукту {product}, и укажет, из каких файлов они были взяты.

3. После этого вызови инструмент 'get_requirements', передав ему:
   - текст, который ты получил от 'extract_requirements'
   - путь к папке: {folder}

   Инструмент сохранит финальный документ с требованиями.

Запрещено писать Python-код, делать предположения, просить уточнений или описывать алгоритмы.
Ты должен использовать только доступные тебе инструменты для выполнения действий.
После выполнения всех шагов ты можешь завершить работу.
"""


prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "{input}")
])

# Если при создании агента передавать отдельно promt и отдельно экземпляр llm, обогащённый инструментами, агент не работает. Поэтому сделал так.
processing_chain = prompt| llm.bind_tools(tools)

# Объявляю отдельный экземпляр класса MemorySaver, а не напрямую передаю MemorySaver в коде создания агента, чтобы можно было гибко смотреть состояния агента.
memory = MemorySaver()

agent_req = create_react_agent(processing_chain
                                    , tools
                                    , checkpointer = memory
                                    )

# Перед запуском требуется генерировать thread_id (уникальный идентификатор сессии)
thread_id = str(uuid4())
config = {"configurable": {"thread_id": thread_id}}

# Запускаю агент 
user_prompt = r"Напиши бизнес требования к продукту Монеты. Папка: C:\Users\artem\YandexDisk\AI_Agent_4BT\AI-agent-for-business-requirements\examples"  
print("Вызов агента...")
agent_req.invoke({"input": user_prompt}, config=config)

print("Чтение состояния памяти...")
result = memory.get(config)

print("Содержимое памяти:")
if isinstance(result, dict):
    for k, v in result.items():
        print(f"{k}:", v)
else:
    print(result, flush=True)

messages = result.get("channel_values", {}).get("messages", [])

# Ниже просто, чтобы вывести в консоль последнее сообщение от модели
# Фильтруем только AIMessage
ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]

# Берём последнее
if ai_messages:
    last_ai_message = ai_messages[-1]
    print("Последнее сообщение от модели:")
    print(last_ai_message.content, flush=True)
else:
    print("AIMessage не найдено.")
