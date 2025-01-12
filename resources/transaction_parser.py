import os
import re
import streamlit as st
from datetime import datetime, timedelta
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
#from dotenv import load_dotenv

#load_dotenv()
groq_key = st.secrets["api_keys"]["GROQ_API_KEY"]
#os.getenv("GROQ_API_KEY")
# Initialize ChatGroq LLM
llm = ChatGroq(
    api_key=groq_key,
    model_name="llama-3.1-70b-versatile",
    temperature=0,
    max_tokens=2048
)


def extract_json(raw_response):
    try:
        match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if match:
            return match.group(0)
        else:
            raise ValueError("No valid JSON found in the response.")
    except Exception as e:
        raise ValueError(f"Error extracting JSON: {str(e)}")


def parse_transaction(desc):
    """
    Use ChatGroq LLM to parse the financial transaction description and extract details.
    """
    current_date = datetime.now()
    today_date = current_date.strftime("%Y-%m-%d")

    prompt_text = f"""
    Extract the following details from this transaction description: <<<desc>>>

    - Transaction Date: If the description mentions "today", return today's date: {today_date}. 
        If "yesterday", return today's date minus one: {(current_date - timedelta(days=1)).strftime("%Y-%m-%d")}. 
        If "last week", return today's date minus seven: {(current_date - timedelta(days=7)).strftime("%Y-%m-%d")}. 
        If "last month", return today's date minus thirty: {(current_date - timedelta(days=30)).strftime("%Y-%m-%d")}. 
        If "last year", return today's date minus thirty: {(current_date - timedelta(days=365)).strftime("%Y-%m-%d")}.      
        If no date is mentioned, return today's date: {today_date}.

    - Bank Name: Extract the bank name, or return null if not mentioned.
    - Account Type: Extract the type of account (e.g., "Savings Account", "Debit Card", "Forex Card", "Cash", 
        "Current Account", "Credit Card"), or return null if not mentioned.
    - Transaction Amount: Extract the amount spent, or return 0 if not mentioned.
    - Transaction Currency: Extract the currency (e.g., INR), or return null if not mentioned.
        String values like 'Rs' or 'Rs.' should be assumed as Ruppes and converted into INR 
    - Transaction Category: Classify the transaction into one of these categories: 
        ["Leisure", "Education", "Utilities", "Groceries", "Health", "Transport", "Entertainment", "Other"], 
        based on the description.
    - Transaction desc: Extract the description of the transaction (e.g., "Netflix subscription" or "Petrol") 
        from the sentence. Truncate the text to Keep the length of the text to a maximum of 50 characters.
    
    Return the details as a JSON object. Ensure that you return only the JSON object without any additional text, 
    comments, or explanations. The JSON object must have the following keys:
    - Transaction Date
    - Bank Name
    - Account Type
    - Transaction Amount
    - Transaction Currency
    - Transaction Category
    - Transaction desc
    """
    prompt_extract = PromptTemplate.from_template(prompt_text.replace('<<<desc>>>', '{desc}'))
    chain_extract = prompt_extract | llm
    res = chain_extract.invoke(input={"desc": desc})
    # print(res)
    try:
        raw_json = extract_json(res.content)
        json_parser = JsonOutputParser()
        return json_parser.parse(raw_json)
    except OutputParserException as e:
        raise OutputParserException(f"Error parsing transaction: {str(e)}")
