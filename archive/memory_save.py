import json
from uuid import UUID
from datetime import datetime
from langgraph.checkpoint.memory import MemorySaver

# Кастомный сериализатор для обработки специальных типов
def custom_serializer(obj):
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

# Сохранение в JSON
def save_checkpoints(checkpointer: MemorySaver, filename: str):
    data = {
        "checkpoints": checkpointer.checkpoints,
        "checkpoints_metadata": checkpointer.checkpoints_metadata
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, default=custom_serializer, indent=2)

# Загрузка из JSON
def load_checkpoints(filename: str) -> MemorySaver:
    checkpointer = MemorySaver()
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Восстанавливаем UUID и datetime
        for key, value in data['checkpoints'].items():
            checkpointer.checkpoints[UUID(key)] = {
                "config": value["config"],
                "checkpoint": value["checkpoint"],
                "created_at": datetime.fromisoformat(value["created_at"])
            }
            
        checkpointer.checkpoints_metadata = data['checkpoints_metadata']
        
    except FileNotFoundError:
        print("Файл чекпоинтов не найден, создаем новый MemorySaver")
    
    return checkpointer

# Пример использования
if __name__ == "__main__":
    # 1. Сохранение состояния
    original_saver = MemorySaver()
    
    # Добавляем тестовые данные
    thread_id = "my_thread_123"
    original_saver.checkpoints = {
        UUID(thread_id): {
            "config": {"key": "value"},
            "checkpoint": {"state": "active"},
            "created_at": datetime.now()
        }
    }
    
    save_checkpoints(original_saver, "checkpoints.json")
    
    # 2. Восстановление состояния
    loaded_saver = load_checkpoints("checkpoints.json")
    
    # Проверка восстановленных данных
    print(loaded_saver.checkpoints)