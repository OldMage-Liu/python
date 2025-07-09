import os
import time
from typing import List, Optional
# 加载环境变量
from dotenv import load_dotenv
load_dotenv()
# LangChain 核心组件
from langchain.agents import Tool
from langchain.chains import RetrievalQA
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.schema import Generation, LLMResult
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.embeddings.base import Embeddings
from pydantic import BaseModel, Field

# Kimi 相关依赖（兼容 OpenAI 接口格式）
from openai import OpenAI

# 本地嵌入模型
from sentence_transformers import SentenceTransformer


# 本地嵌入模型封装
class LocalEmbeddings(Embeddings):
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode([text], convert_to_numpy=True).tolist()[0]


# Kimi 语言模型实现（添加重试和延迟机制）
class KimiLLM(BaseLLM):
    model_name: str = Field(default="moonshot-v1-8k")
    max_retries: int = Field(default=3)
    retry_delay: float = Field(default=2.0)

    @property
    def _llm_type(self) -> str:
        return "kimi"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        client = OpenAI(
            api_key=os.getenv("KIMI_API_KEY"),
            base_url=os.getenv("KIMI_API_BASE_URL", "https://api.moonshot.cn/v1")
        )

        for attempt in range(self.max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=1024,
                    stop=stop
                )
                return response.choices[0].message.content
            except Exception as e:
                if "rate_limit" in str(e) and attempt < self.max_retries - 1:
                    print(f"触发速率限制，等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    print(f"调用 Kimi API 时出错: {e}")
                    return f"抱歉，我现在无法处理您的请求，请稍后再试。"

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> LLMResult:
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop=stop)
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)

    @property
    def _identifying_params(self):
        return {"model_name": self.model_name}


# 初始化知识库
def setup_knowledge_base(product_catalog_file: str, embeddings, llm):
    try:
        os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"
        if not os.path.exists(product_catalog_file):
            raise FileNotFoundError(f"产品目录文件 '{product_catalog_file}' 不存在")

        with open(product_catalog_file, "r", encoding="utf-8") as f:
            product_catalog = f.read()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        texts = text_splitter.split_text(product_catalog)
        print(f"文本已分割为 {len(texts)} 块")

        docsearch = Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            collection_name="product-knowledge-base-v2",
            persist_directory="./chroma_db"
        )

        knowledge_base = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=docsearch.as_retriever(search_kwargs={"k": 3})
        )
        return knowledge_base
    except Exception as e:
        print(f"知识库初始化失败: {e}")
        import traceback
        print(traceback.format_exc())
        raise


# 简化的销售助手（避免使用复杂的 Agent 框架）
class SimpleSalesAssistant:
    def __init__(self, knowledge_base, llm):
        self.knowledge_base = knowledge_base
        self.llm = llm
        self.system_prompt = """你是一个专业的销售助手，帮助客户了解我们的产品和服务。
请根据提供的产品信息回答客户问题。如果没有相关信息，请礼貌地告知客户并提供一般性建议。

产品信息：
{context}

客户问题：{question}

请提供专业、友好的回答："""

    def answer_question(self, question: str) -> str:
        # 检查是否需要查询知识库
        product_keywords = ["产品", "价格", "配置", "规格", "功能", "服务", "保修", "退货", "安装"]
        needs_knowledge = any(keyword in question for keyword in product_keywords)

        if needs_knowledge:
            try:
                # 使用知识库查询相关信息（使用 invoke 替代 run）
                result = self.knowledge_base.invoke({"query": question})
                context = result.get("result", "暂时无法获取产品信息")
                prompt = self.system_prompt.format(context=context, question=question)
            except Exception as e:
                print(f"知识库查询失败: {e}")
                context = "暂时无法获取产品信息"
                prompt = self.system_prompt.format(context=context, question=question)
        else:
            # 简单的问候或一般性问题
            if any(greeting in question.lower() for greeting in ["你好", "hello", "hi", "您好"]):
                return "您好！我是专业的销售助手，很高兴为您服务。如果您对我们的产品或服务有任何问题，请随时告诉我！"
            else:
                prompt = f"作为销售助手，请回答客户的问题：{question}"

        return self.llm._call(prompt)


# 创建示例产品目录文件
def create_sample_catalog():
    sample_content = """
产品目录

智能手机系列：
- iPhone 15 Pro：搭载A17 Pro芯片，6.1英寸Super Retina XDR显示屏，三摄系统，售价9999元
- Samsung Galaxy S24：搭载Exynos 2400处理器，6.2英寸Dynamic AMOLED显示屏，50MP主摄，售价8999元

笔记本电脑系列：
- MacBook Pro 14英寸：M3 Pro芯片，16GB内存，512GB存储，售价16999元
- Dell XPS 13：Intel Core i7-13700H，16GB内存，512GB SSD，售价12999元

智能家居系列：
- 小米空气净化器Pro：CADR值600m³/h，适用60-100平米，售价2999元
- 智能音响HomePod mini：支持Siri，360度音效，售价749元

服务政策：
- 所有产品享有1年质保
- 支持7天无理由退货
- 免费上门安装服务
- 24小时客服热线：400-123-4567
"""
    with open("sample_product_catalog.txt", "w", encoding="utf-8") as f:
        f.write(sample_content)
    print("已创建示例产品目录文件：sample_product_catalog.txt")


# 主程序
def main():
    if not os.getenv("KIMI_API_KEY"):
        print("错误: 请设置环境变量 KIMI_API_KEY")
        return

    if not os.path.exists("sample_product_catalog.txt"):
        create_sample_catalog()

    # 初始化组件
    llm = KimiLLM(model_name="moonshot-v1-8k")
    embeddings = LocalEmbeddings()

    try:
        knowledge_base = setup_knowledge_base("sample_product_catalog.txt", embeddings, llm)
        print("知识库初始化成功")
    except Exception as e:
        print("知识库初始化失败，程序将无法正常运行")
        print(f"错误详情: {e}")
        return

    # 使用简化的销售助手
    sales_assistant = SimpleSalesAssistant(knowledge_base, llm)

    print("\n==== 销售助手已启动 ====")
    print("输入问题，输入 'exit' 结束对话")

    while True:
        try:
            user_input = input("\n客户: ")
            if user_input.lower() == "exit":
                break

            response = sales_assistant.answer_question(user_input)
            print(f"销售助手: {response}")

        except KeyboardInterrupt:
            print("\n\n程序已被用户中断")
            break
        except Exception as e:
            print(f"处理请求时发生错误: {e}")


if __name__ == "__main__":
    main()