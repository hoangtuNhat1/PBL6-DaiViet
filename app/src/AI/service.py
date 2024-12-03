from typing import List, Dict, Any, Tuple
from .setup import get_collection, tokenize_model, llm_model
from pymilvus import Collection


class AIService:
    """
    AIService cung cấp các phương thức để thực hiện tìm kiếm, xây dựng prompt và trả lời câu hỏi
    bằng mô hình ngôn ngữ lớn (LLM) dựa trên thông tin được cung cấp.
    """

    def __init__(self):
        pass

    @staticmethod
    def search(
        field: str, question: str, collection: Collection
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm câu trả lời có liên quan dựa trên câu hỏi đã nhập, trả về danh sách các tài liệu
        có thông tin tương tự với câu hỏi.

        Parameters:
        - field (str): Tên trường vector trong collection để tìm kiếm.
        - question (str): Câu hỏi từ người dùng cần được trả lời.
        - collection (Collection): Đối tượng collection từ Milvus để thực hiện tìm kiếm.

        Returns:
        - List[Dict[str, Any]]: Danh sách các tài liệu chứa thông tin tìm được.
        """
        v_q = tokenize_model.encode(question)
        res = collection.search(
            anns_field=field,
            param={"metric_type": "IP", "params": {}},
            data=[v_q],
            output_fields=["id", "text", "question"],
            limit=5,
        )
        result_docs = []

        for hits in res:
            for hit in hits:
                hit_dict = {
                    "id": hit.entity.get("id"),
                    "text": hit.entity.get("text"),
                    "question": hit.entity.get("question"),
                }
                result_docs.append(hit_dict)

        return result_docs

    @staticmethod
    def build_prompt(
        question: str, search_result: List[Dict[str, str]], character_name: str
    ) -> str:
        """
        Xây dựng prompt dựa trên câu hỏi, kết quả tìm kiếm, và tên nhân vật.

        Parameters:
        - question (str): Câu hỏi từ người dùng cần được trả lời.
        - search_result (List[Dict[str, str]]): Danh sách các tài liệu tìm kiếm có thông tin liên quan.
        - character_name (str): Tên của nhân vật giả tưởng mà người dùng muốn đóng vai.

        Returns:
        - str: Chuỗi prompt đã định dạng để gửi đến mô hình ngôn ngữ lớn.
        """
        with open("src/prompt.txt", "r", encoding="utf-8") as file:
            prompt_template = file.read().strip()

        context = ""
        for doc in search_result:
            doc_question = doc["question"].replace("\n", "").strip()
            doc_answer = doc["text"].replace("\n", "").strip()
            context += f"\ncâu hỏi: {doc_question}\ntrả lời: {doc_answer}\n\n"

        prompt = prompt_template.format(
            character_name=character_name, question=question, context=context
        ).strip()
        return prompt

    @staticmethod
    def llm(prompt: str) -> str:
        """
        Gửi prompt đến mô hình ngôn ngữ lớn (LLM) và nhận phản hồi.

        Parameters:
        - prompt (str): Chuỗi prompt đã định dạng cần được gửi đến mô hình.

        Returns:
        - str: Phản hồi từ mô hình ngôn ngữ lớn.
        """
        response = llm_model.chat.completions.create(
            model="gemma2", messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    @staticmethod
    def rag(
        question: str, character_short_name: str, character_name: str
    ) -> Tuple[str, str]:
        """
        Thực hiện tìm kiếm tài liệu liên quan, xây dựng prompt, và trả lời câu hỏi
        bằng mô hình ngôn ngữ lớn dựa trên thông tin thu thập.

        Parameters:
        - question (str): Câu hỏi từ người dùng cần được trả lời.
        - character_short_name (str): Tên rút gọn của nhân vật để lấy collection từ Milvus.
        - character_name (str): Tên đầy đủ của nhân vật giả tưởng mà người dùng muốn đóng vai.

        Returns:
        - Tuple[str, str]: Tuple chứa prompt đã định dạng và câu trả lời từ mô hình ngôn ngữ lớn.
        """
        collection = get_collection(character_short_name)
        results = AIService.search("question_text_vector", question, collection)
        prompt = AIService.build_prompt(question, results, character_name)
        answer = AIService.llm(prompt)
        return prompt, answer
