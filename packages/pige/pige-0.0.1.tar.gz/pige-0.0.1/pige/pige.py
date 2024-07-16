#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   pige.py
@Time    :   2024/07/12
@Author  :   Winter.Yu 
@Version :   1.0
@Contact :   winter741258@126.com
@Desc    :   None
'''

# here put the import lib
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (answer_relevancy, context_precision, context_recall,
                           faithfulness, AnswerRelevancy)
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from typing import Literal, List


def critic_LLM(api_key: str, base_url: str, model_name: str):
    assert api_key is not None, "API_KEY is not set"
    API_KEY = api_key
    MODEL = model_name if model_name else ""
    llm = ChatOpenAI(
        model=MODEL,
        api_key=API_KEY,
        base_url=base_url,
        max_tokens=2048,
        temperature=0.01,
        n=1
    )
    return llm

def critic_Embedding(model_path: str, device: str ='cpu', normalize_embeddings: bool =False):
    embedding_model_name = model_path
    model_kwargs = {'device': device}
    encode_kwargs = {'normalize_embeddings': normalize_embeddings}
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    return embeddings


def pige(llm, embeddings, data: dict[str, List], metrics: List[str]=[]):
    assert llm is not None, "llm is not set"
    assert embeddings is not None, "embeddings is not set"
    assert data is not None, "data is not set"
    assert type(metrics) == list, "metrics is not list"
    assert all([i in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall'] for i in metrics]), \
        "metrics is not in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']"
    _metrics = []
    if 'faithfulness' in metrics:
        _metrics.append(faithfulness)
    if 'answer_relevancy' in metrics:
        _metrics.append(answer_relevancy)
        answer_relevancy = AnswerRelevancy(strictness=1)
    if 'context_precision' in metrics:
        _metrics.append(context_precision)
    if 'context_recall' in metrics:
        _metrics.append(context_recall)
    if metrics == []:
        _metrics = [faithfulness, answer_relevancy, context_precision, context_recall]

    dataset = Dataset.from_dict(data)

    results = evaluate(
        dataset,
        llm=llm,
        embeddings=embeddings,
        metrics=_metrics,
    )
    df = results.to_pandas()
    return df
