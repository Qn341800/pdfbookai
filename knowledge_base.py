import os
import time
from tqdm import tqdm
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
import transformers

# 配置参数
PDF_FOLDER = "./pdfs"  # PDF存储目录
PERSIST_DIR = "./chroma_db"  # 向量数据库存储目录
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # 嵌入模型
CHUNK_SIZE = 1500  # 文本块大小
CHUNK_OVERLAP = 300  # 文本块重叠

# 优化文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    add_start_index=True
)

# 初始化嵌入模型
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={"device": "cpu"}  # 使用GPU可改为"cuda"
)

# 创建或加载向量数据库
def init_vectorstore():
    if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
        print("加载已有向量数据库...")
        return Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=embeddings
        )
    else:
        print("创建新的向量数据库...")
        return Chroma(
            embedding_function=embeddings,
            persist_directory=PERSIST_DIR
        )

# 处理单个PDF文件
def process_pdf(file_path, vectorstore):
    try:
        loader = PyPDFLoader(file_path)
        doc = loader.load()
        texts = text_splitter.split_documents(doc)
        
        # 添加元数据
        for text in texts:
            text.metadata["source"] = os.path.basename(file_path)
            text.metadata["import_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        vectorstore.add_documents(texts)
        vectorstore.persist()
        return True, f"成功导入: {os.path.basename(file_path)}"
    except Exception as e:
        return False, f"导入失败: {os.path.basename(file_path)} - {str(e)}"

# 批量导入PDF
def import_pdfs(pdf_folder=PDF_FOLDER):
    vectorstore = init_vectorstore()
    results = []
    
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)
        return results
    
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    
    for filename in tqdm(pdf_files, desc="处理PDF文件"):
        file_path = os.path.join(pdf_folder, filename)
        success, message = process_pdf(file_path, vectorstore)
        results.append(message)
    
    return results

# 知识查询
def query_knowledge(question, k=5):
    vectorstore = init_vectorstore()
    docs = vectorstore.similarity_search(question, k=k)
    
    results = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get('source', '未知来源')
        page = doc.metadata.get('page', 0) + 1
        content = doc.page_content
        
        results.append({
            "rank": i+1,
            "source": source,
            "page": page,
            "content": content,
            "score": 0  # 由于相似度搜索返回的文档没有score，这里设为0
        })
    
    return results

# 可选：集成本地大模型
def init_llm():
    # 使用一个较小的模型，例如 flan-t5-base
    model_id = "google/flan-t5-base"
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)
    model = transformers.AutoModelForSeq2SeqLM.from_pretrained(model_id)
    pipe = transformers.pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=512
    )
    return HuggingFacePipeline(pipeline=pipe)

def ask_question(question):
    vectorstore = init_vectorstore()
    llm = init_llm()
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        return_source_documents=True
    )
    
    result = qa_chain({"query": question})
    return {
        "answer": result["result"],
        "sources": [{"source": doc.metadata.get("source", "未知"), "page": doc.metadata.get("page", 0)} for doc in result["source_documents"]]
    }