# -*- coding: utf-8 -*-
"""
File name: test_atlas.py
Author: Bowen
Date created: 17/7/2024
Description: This Python file provides an example of mathematical operations.

Copyright information: © 2024 QDX
"""

import getpass, os, pymongo, pprint
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pymongo import MongoClient
import certifi

MONGODB_ATLAS_CLUSTER_URI = "mongodb+srv://bowenzhang0101:QoLQBmQ0XkYmkvqE@cluster0.czwptpj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to your Atlas cluster
client = MongoClient(MONGODB_ATLAS_CLUSTER_URI, tlsCAFile=certifi.where())

# Define collection and index name
db_name = "langchain_db"
collection_name = "test"
atlas_collection = client[db_name][collection_name]
vector_search_index = "vector_index"

# Load the PDF
loader = PyPDFLoader("https://query.prod.cms.rt.microsoft.com/cms/api/am/binary/RE4HkJP")
data = loader.load()

# Split PDF into documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
docs = text_splitter.split_documents(data)

# Print the first document
docs[0]

# Create the vector store
vector_store = MongoDBAtlasVectorSearch.from_documents(
    documents = docs,
    embedding = OpenAIEmbeddings(disallowed_special=()),
    collection = atlas_collection,
    index_name = vector_search_index
)
