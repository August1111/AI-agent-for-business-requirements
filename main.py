from agent.agent  import agent_executor6, memory
from uuid import uuid4

def main():
    thread_id = str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    user_prompt = r"Напиши бизнес требования к продукту Монеты. Папка: C:\Users\artem\YandexDisk\AI_Agent_4BT\AI-agent-for-business-requirements\examples"  
    print("Вызов агента...")
    agent_executor6.invoke({"input": user_prompt}, config=config)

    print("Чтение состояния памяти...")
    result = memory.get(config)

    print("Содержимое памяти:")
    if isinstance(result, dict):
        for k, v in result.items():
            print(f"{k}:", v)
    else:
        print(result)
   
if __name__ == "__main__":
    main()
