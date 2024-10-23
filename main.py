from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from os import listdir
from os.path import isfile, join
import PyPDF2
import time
import os
import string
import nltk
from openai import RateLimitError, BadRequestError
from openai import OpenAI
from nltk.corpus import stopwords
from fastapi import FastAPI
from concurrent.futures import ThreadPoolExecutor, as_completed
from pymongo import MongoClient
from urllib.parse import unquote
from pathlib import Path

# setting up for mongo DB
client = MongoClient('mongodb://localhost:27017/')
db = client['db_from_API']
collection = db['Information']

api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key= api_key)

# setting fastapi
app = FastAPI()

# Downloading stopwords
nltk.download('stopwords')
Stopwords = set(stopwords.words('english'))
additional_stopwords = ["are", "a", "an", "shall", "may","also",
                        "under","within","every","any","all"]

def getting_all_files(user_path):
    path = Path(user_path).resolve()
    all_files = [f for f in listdir(path) if isfile(join(user_path, f)) and f.lower().endswith('pdf')]
    return all_files

def reading_text(file_name, user_path):
    try:
        path = join("r", user_path)
        pdf_reader = PyPDF2.PdfReader(join(path, file_name))
        text = ""
        for i in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[i]
            text += page.extract_text()
        return text
    except Exception:
        return ""

def getting_domains(text):
    prompt = f"""You are helfpful AI assistant. your task is to generate the most relevant domain and subdomains collectively which are point of focus from the 
            text which will be provided to you matches the most.
            the text is {text}
            """
    response = client.chat.completions.create(
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ],
        model = "gpt-3.5-turbo-0125"
    )
    return response.choices

def getting_summarization(text):
    prompt = f"""You are helfpul AI assistant. Your task is to generate a summary for the text which will be provided to you please make sure that all the numerical
            number, percentages and dates that is shown should to be included in this summary.
            the text is {text}
            """
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="gpt-3.5-turbo-0125"
    )
    return response.choices[0].message.content.replace("Summary: ","")

def getting_keywords(text, domain):
    prompt = f"""You are helpful AI assistant. Your task is to generate only 5 most prominent keywords from the text which 
    will be provided to you which matches best to the domain={domain}, the text is: {text}
            """
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="gpt-3.5-turbo-0125"
    )
    return response.choices[0].message.content

def handling_sentences(file_name, user_path):
    path = join("r", user_path)
    final_path = join(path, file_name)
    pdf = PyPDF2.PdfReader(final_path)
    text = ""
    for i in range(len(pdf.pages)):
        page = pdf.pages[i]
        text += page.extract_text()
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences)
    sentence_scores = np.sum(tfidf_matrix.toarray(), axis=1)
    top_n = int(len(sentences)*0.1)
    d = getting_domains(text[:1000])
    return [sentences[i] for i in sentence_scores.argsort()[-top_n:][::-1]], d, getting_keywords(text[:1000], d)

def summarize_text(text):
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences)
    sentence_scores = np.sum(tfidf_matrix.toarray(), axis=1)
    top_n = len(sentences)
    important_sentences = [sentences[i] for i in sentence_scores.argsort()[-top_n:][::-1]]

    domains = getting_domains(text[:1000])
    all_domains = domains[0].message
    final_domains = all_domains.content   # here all domains are present

    ind = 0
    count = 0
    max_tokens = 2500
    new_summary = ""
    # new_keywords = ""
    start = 0
    while ind<int(len(important_sentences)*0.1):
        length = len(important_sentences[ind].split())
        if count + length <= max_tokens:
            count += length
            ind = ind + 1
        else:
            new_summary += getting_summarization(important_sentences[start: ind])
            # new_keywords += getting_keywords(sentences[start: ind], final_domains)
            count = 0
            start = ind
    if count != 0 and count < max_tokens:
        new_summary += getting_summarization(important_sentences[start:ind+1])
        # new_keywords += getting_keywords(sentences[start: ind+1], final_domains)

    # SECTION - of code for finding keywords
    words = set(word.strip(string.punctuation).lower() for word in text.split())
    Stopwords.update(additional_stopwords)
    filtered_words = words - Stopwords
    new_keywords = getting_keywords(' '.join(filtered_words), final_domains)

    return new_summary, new_keywords, final_domains
def process_file(file_name, user_path):
    text = reading_text(file_name, user_path)
    summary, keywords, all_domains = summarize_text(text)
    return file_name, summary, keywords, all_domains

# FASTAPI ROUTE

@app.get('/')
def welcome():
    return {"message":
            "to use the function go to the end point - /process_pdf/{give_your_path_name}"}

@app.get('/process_pdf/{user_path:path}')

def process(user_path: str):
    decoded_path = unquote(user_path)
    abs_path = Path(decoded_path).resolve()
    all_files = getting_all_files(str(abs_path))

    max_threads = os.cpu_count()

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=max_threads) as pool:
        futures = {pool.submit(process_file, f, user_path): f for f in all_files}

        for future in as_completed(futures):
            curr_file = futures[future]
            try:
                file_name, summary, keywords, all_domains = future.result()
                document = {
                    "filename": file_name,
                    "summary": summary,
                    "keywords": keywords
                }
                print(f"File: {file_name} is processed and entered in database")
                collection.insert_one(document)

            except BadRequestError:
                summed_up, domain, keywords = handling_sentences(curr_file, user_path)
                cleaned = summed_up[0].replace('\n', '')
                document1 = {
                    "filename": curr_file,
                    "summary": cleaned,
                    "keywords": keywords
                }
                print(f"File: {curr_file} is processed and entered in database")
                collection.insert_one(document1)

            except RateLimitError:
                time.sleep(60)

    end_time = time.time()

    return {
        "process_completed": end_time-start_time
    }