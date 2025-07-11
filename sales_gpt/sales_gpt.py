import os
import re
import time
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.llms import BaseLLM
from langchain.schema import Generation, LLMResult
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.embeddings.base import Embeddings
from openai import OpenAI
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

load_dotenv()


class LocalEmbeddings(Embeddings):
    def __init__(self, model_name: str = "shibing624/text2vec-base-chinese"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode([text], convert_to_numpy=True).tolist()[0]


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
                    temperature=0,
                    max_tokens=1024,
                    stop=stop
                )
                return response.choices[0].message.content
            except Exception as e:
                if "rate_limit" in str(e) and attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    return "抱歉，我现在无法处理您的请求，请稍后再试。"

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> LLMResult:
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop=stop)
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)

    @property
    def _identifying_params(self):
        return {"model_name": self.model_name}


def setup_knowledge_base(product_catalog_file: str, embeddings, llm):
    try:
        os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

        if not os.path.exists(product_catalog_file):
            raise FileNotFoundError(f"产品目录文件 '{product_catalog_file}' 不存在")

        with open(product_catalog_file, "r", encoding="utf-8") as f:
            product_catalog = f.read()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        texts = text_splitter.split_text(product_catalog)

        docsearch = Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            collection_name="product-knowledge-base-v2",
            persist_directory="./chroma_db"
        )

        knowledge_base = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=docsearch.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True
        )

        return knowledge_base
    except Exception as e:
        print(f"知识库初始化失败: {e}")
        raise


class ContextAwareSalesAssistant:
    def __init__(self, knowledge_base, llm, catalog_file: str):
        self.knowledge_base = knowledge_base
        self.llm = llm
        self.catalog_file = catalog_file
        self.conversation_history: Dict[str, List[Tuple[str, str]]] = {}
        self.product_names = self.extract_product_names()

        self.system_prompt = """你是一个专业的销售助手，必须严格根据产品信息和对话历史回答客户问题。注意：
1. 只能介绍产品信息中明确提到的产品，不能提及任何未列出的产品
2. 如果信息中未提及相关内容，请明确告知"暂无相关信息"，不要编造
3. 产品名称必须完全匹配文档中的表述
4. 保持回答简洁专业，避免冗长解释
5. 考虑对话上下文提供连贯回答

当前对话历史：
{history}

产品信息：
{context}

客户问题：{question}

请基于上述信息，提供专业、准确的回答："""

    def extract_product_names(self) -> List[str]:
        try:
            with open(self.catalog_file, "r", encoding="utf-8") as f:
                content = f.read()

            pattern = r"-\s*(.*?):"
            names = re.findall(pattern, content)
            return list(set(names))
        except Exception:
            return []

    def contains_unauthorized_products(self, response: str) -> bool:
        if not self.product_names:
            return False

        for product in self.product_names:
            if product in response:
                return False

        return "产品" in response or "推荐" in response

    def format_history(self, history: List[Tuple[str, str]]) -> str:
        if not history:
            return "无"

        formatted = []
        for role, content in history:
            if role == "user":
                formatted.append(f"客户: {content}")
            else:
                formatted.append(f"助手: {content}")

        return "\n".join(formatted)

    def is_product_related(self, question: str) -> bool:
        product_keywords = [
            "产品", "商品", "货品", "型号", "款式", "系列", "品牌", "牌子", "什么", "哪些",
            "哪款", "介绍", "推荐", "有啥", "有什么", "手机", "电脑", "笔记本", "台式机",
            "平板", "智能", "设备", "配件", "耳机", "手表", "家电", "应用", "软件", "App",
            "服务", "规格", "配置", "参数", "尺寸", "大小", "重量", "容量", "内存", "硬盘",
            "存储", "屏幕", "分辨率", "处理器", "CPU", "显卡", "GPU", "电池", "续航", "待机",
            "能用多久", "系统", "OS", "操作系统", "平台", "网络", "接口", "端口", "颜色",
            "材质", "用料", "功能", "性能", "特点", "特色", "优势", "好处", "作用", "用处",
            "能做什么", "支持", "是否支持", "有没有", "有没有...功能", "特性", "速度", "快不快",
            "流畅", "卡不卡", "效果", "画质", "音质", "清晰度", "灵敏度", "准确度", "防水",
            "防尘", "耐用", "质量", "品质", "稳定性", "价格", "价钱", "售价", "卖价", "多少钱",
            "贵不贵", "优惠", "折扣", "打折", "促销", "活动", "特价", "划算", "性价比", "值不值",
            "购买", "买", "下单", "订购", "预定", "预售", "渠道", "哪里买", "官网", "电商",
            "店铺", "门店", "库存", "有货", "缺货", "补货", "期货", "服务", "支持", "客服",
            "售后", "保修", "保固", "质保", "期限", "多久", "几年", "维修", "修理", "修",
            "换新", "换货", "退货", "退款", "退换", "退", "换", "政策", "条款", "条件",
            "发票", "订单", "物流", "快递", "配送", "送货", "安装", "设置", "激活", "注册",
            "绑定", "初始化", "教程", "指南", "说明书", "手册", "怎么用", "如何使用", "操作方法",
            "操作指南", "对比", "比较", "哪个好", "区别", "差异", "不同", "优缺点", "优劣势",
            "评价", "口碑", "反馈", "评论", "测评", "怎么样", "好不好", "值不值得买", "推荐",
            "排行榜", "排名", "竞品", "对手", "同类", "问题", "故障", "毛病", "bug", "错误",
            "异常", "不能用", "不好用", "失灵", "死机", "卡死", "重启", "黑屏", "花屏", "没声音",
            "不充电", "发热", "发烫", "耗电", "信号", "连不上", "兼容", "冲突", "升级", "更新",
            "固件", "驱动", "恢复", "重置", "解决", "怎么办", "如何处理", "如何解决", "原因",
            "为什么", "为何", "如何避免", "设置", "配置", "调节", "调整", "连接", "配对",
            "联网", "绑定", "下载", "安装", "卸载", "更新", "升级", "恢复出厂", "重置", "刷机",
            "越狱", "root", "解锁", "密码", "账户", "登录", "注册"
        ]

        question_lower = question.lower()
        comparison_phrases = ["哪一款", "哪款", "哪个", "哪一", "比较", "更好", "更强", "最高", "最优", "最便宜"]
        is_comparison = any(phrase in question_lower for phrase in comparison_phrases)
        is_product_keyword = any(keyword in question_lower for keyword in product_keywords)
        is_product_name = any(name.lower() in question_lower for name in self.product_names)
        is_price_related = re.search(r"\d+元|\d+块|\d+块钱", question_lower) is not None

        return is_comparison or is_product_keyword or is_product_name or is_price_related

    def answer_question(self, session_id: str, question: str) -> str:
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []

        history = self.conversation_history[session_id]

        if any(greeting in question.lower() for greeting in ["你好", "hello", "hi", "您好"]):
            response = "您好！我是专业的销售助手，很高兴为您服务。如果您对我们的产品或服务有任何问题，请随时告诉我！"
            history.append(("user", question))
            history.append(("assistant", response))
            return response

        history.append(("user", question))

        if self.is_product_related(question):
            try:
                query_with_context = f"{self.format_history(history[-3:])}\n当前问题: {question}"
                result = self.knowledge_base.invoke({"query": query_with_context})
                context = result.get("result", "暂时无法获取产品信息")
                formatted_history = self.format_history(history[:-1])

                prompt = self.system_prompt.format(
                    history=formatted_history,
                    context=context,
                    question=question
                )

                response = self.llm._call(prompt)

                if self.contains_unauthorized_products(response):
                    response = "根据我们的产品目录，暂无相关信息。如果您有其他问题，我很乐意帮助您。"
            except Exception as e:
                response = "暂时无法获取产品信息，请稍后再试。"
        else:
            if history:
                prompt = f"作为销售助手，请根据以下对话历史回答客户的最新问题：\n\n{self.format_history(history)}\n\n回答："
                response = self.llm._call(prompt)
            else:
                response = "您好，我是产品销售助手，主要解答关于我们产品的疑问。如果您有产品相关问题，请随时提出。"

        history.append(("assistant", response))

        if len(history) > 10:
            history = history[-10:]
            self.conversation_history[session_id] = history

        return response


# 创建示例产品目录


# 主程序
def main():
    if not os.getenv("KIMI_API_KEY"):#添加kimiAPI接口
        print("错误: 请设置环境变量 KIMI_API_KEY")
        return

    llm = KimiLLM(model_name="moonshot-v1-8k")#调用KIMI的moonshot-v1-8k模型兼容所有支持openai库掉接口的ai
    embeddings = LocalEmbeddings(model_name="shibing624/text2vec-base-chinese")#使用sentence_transformers嵌入本地模型当前使用的是shibing624/text2vec-base-chinese对于中文有特别优化

    try:
        knowledge_base = setup_knowledge_base("sample_product_catalog.txt", embeddings, llm)#初始化知识库
        print("知识库初始化成功")
    except Exception as e:
        print("知识库初始化失败，程序将无法正常运行")
        return

    # 使用上下文感知的销售助手
    sales_assistant = ContextAwareSalesAssistant(knowledge_base, llm, "sample_product_catalog.txt")#使用上下文感知的销售助手knowledge_base为初始化后的知识库,llm为ai调用

    # 为当前会话生成唯一ID
    session_id = f"session_{int(time.time())}"

    print("\n==== 销售助手已启动 (支持多轮对话) ====")
    print("输入问题，输入 'exit' 结束对话")
    print("您可以像正常对话一样连续提问\n")

    while True:
        try:
            user_input = input("\n客户: ")
            if user_input.lower() == "exit":
                break
            if user_input.lower() == "clear":#如果输入clear清楚对话历史
                # 清除当前会话历史
                if session_id in sales_assistant.conversation_history:
                    del sales_assistant.conversation_history[session_id]
                print("对话历史已清除")
                continue

            response = sales_assistant.answer_question(session_id, user_input)#读取session_id和user_input,保留五条历史会话
            print(f"销售助手: {response}")

        except KeyboardInterrupt:
            print("\n\n程序已被用户中断")
            break
        except Exception as e:
            print(f"处理请求时发生错误: {e}")


if __name__ == "__main__":
    main()
