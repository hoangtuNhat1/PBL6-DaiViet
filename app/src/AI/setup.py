from pymilvus import connections, Collection, MilvusClient
from sentence_transformers import SentenceTransformer
from openai import OpenAI

# Kết nối đến Milvus trên localhost với cổng mặc định
connections.connect(host="localhost", port="19530")
print("Connected to Milvus")

# Tải mô hình biến đổi câu để xử lý ngôn ngữ tự nhiên cho tiếng Việt
tokenize_model: SentenceTransformer = SentenceTransformer("keepitreal/vietnamese-sbert")
print("Tokenize Model loaded successfully")

# Cấu hình kết nối đến OpenAI LLM Model qua API nội bộ
llm_model: OpenAI = OpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="ollama",
)
print("LLM Model loaded successfully")


def get_collection(agent_short_name: str) -> Collection:
    """
    Tạo một đối tượng Collection trong Milvus dựa trên tên rút gọn của tác nhân.

    Parameters:
    - agent_short_name (str): Tên rút gọn của tác nhân để xác định tên của collection.

    Returns:
    - Collection: Đối tượng Collection trong Milvus tương ứng với tên tác nhân.
    """
    collection_name = f"{agent_short_name}_info"
    collection = Collection(name=collection_name)
    return collection
