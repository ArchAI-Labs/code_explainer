from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage import ltm_sqlite_storage
from .storage_qdrant import QdrantStorage

def get_long_term_memory():
    ltm = LongTermMemory(
        storage=ltm_sqlite_storage.LTMSQLiteStorage(
            db_path="./memory/long_term_memory_storage.db"
        )
    )
    return ltm

def get_short_term_memory():
    stm = ShortTermMemory(
        storage=QdrantStorage(type="short_term",
             )
    )
    return stm

def get_entity_memory():
    entity = EntityMemory(
        storage=QdrantStorage(type="entity_storage",
             )
    )
    return entity