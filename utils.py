import os
import PyPDF2
import re
from chromadb import Client, Settings
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader
from typing import List, Dict
from openai import OpenAI
import requests

ef = embedding_functions.DefaultEmbeddingFunction()
messages = []

openapiclient = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY'))


client = Client(settings=Settings(persist_directory="./", is_persistent=True))
_collection = client.get_or_create_collection(name="PDFQA", embedding_function=ef)

async def save_uploaded_file(file, filename):
    print(f'in save_uploaded_file. Got file {filename}')
    with open(os.path.join('uploads', filename), 'wb') as f:
        f.write(file.read())


    return os.path.join('uploads', filename)
def delete_collection():
    client.delete_collection(_collection.name)
    print("Collection deleted successfully")


def verify_pdf_path(file_path):
    try:
        print(file_path)
        with open(file_path, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            if len(pdf_reader.pages) > 0:
                pass
            else:
                raise ("PDF file is empty")
    except PyPDF2.errors.PdfReadError:
        raise PyPDF2.errors.PdfReadError("Invalid PDF file")
    except FileNotFoundError:
        raise FileNotFoundError("File not found, check file address again")
    except Exception as e:
        raise (f"Error: {e}")


def get_text_chunks(text: str, word_limit: int = 1000) -> List[str]:
    """
    Divides a text into chunks with a pre-defined word limit (defaults to 1000) such that each chunk is a complete sentence

    Parameters:
        text (str): The entire text to be divided into chunks.
        word_limit (int): The desired word limit for each chunk.

    Returns:
        List[str]: A list containing the chunks of texts with the specified word limit and complete sentences.
    """
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
    chunks = []
    current_chunk = []

    for sentence in sentences:
        words = sentence.split()
        if len(" ".join(current_chunk + words)) <= word_limit:
            current_chunk.extend(words)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = words

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def load_pdf(file: str, word: int) -> Dict[int, List[str]]:
    reader = PdfReader(file)
    documents = {}
    for page_no in range(len(reader.pages)):
        page = reader.pages[page_no]
        texts = page.extract_text()
        text_chunks = get_text_chunks(texts, word)
        documents[page_no] = text_chunks
    return documents


def add_text_to_collection(file: str, word: int = 1000) -> None:
    docs = load_pdf(file, word)
    docs_strings = []
    ids = []
    meta_data = []
    id = 0
    for page_no in docs.keys():
        for doc in docs[page_no]:
            docs_strings.append(doc)
            meta_data.append({"page_no": page_no})
            ids.append(id)
            id += 1

    _collection.add(
        ids=[str(id) for id in ids],
        documents=docs_strings,
        metadatas=meta_data,
    )
    return "PDF successfully added to collection"


def query_collection(texts: str, n: int) -> List[str]:
    result = _collection.query(
        query_texts=texts,
        n_results=n,
    )
    documents = result["documents"][0]
    meta_data = result["metadatas"][0]
    resulting_strings = []
    for page_no, text_list in zip(meta_data, documents):
        resulting_strings.append(f"Page {page_no['page_no']}: {text_list}")
    return resulting_strings


def get_response(
    queried_texts: List[str],
) -> List[Dict]:
    global messages
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. You will always answer the question asked in 'question:' and include the page number at the start of your response, formatted as 'page number'.",
        },
        {"role": "user", "content": "".join(queried_texts)},
    ]

    response = openapiclient.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        logprobs=True,
    )
    response_msg = response.choices[0].message.content.strip()
    messages = messages + [{"role": "assistant", "content": response_msg}]
    return response_msg


def get_answer(query: str, n: int):
    queried_texts = query_collection(texts=query, n=n)
    queried_string = ["".join(text) for text in queried_texts]
    queried_string = queried_string[0] + f"ques: {query}"
    answer = get_response(
        queried_texts=queried_string,
    )
    return answer


def post_message_to_slack(text):
    try:
        data = {
            "token": os.environ.get("SLACK_API_KEY"),
            "channel": "some_channel",
            "text": text,
        }
        response = requests.post("https://slack.com/api/chat.postMessage", data=data)
        return response.json()
    except Exception as e:
        print(e)
