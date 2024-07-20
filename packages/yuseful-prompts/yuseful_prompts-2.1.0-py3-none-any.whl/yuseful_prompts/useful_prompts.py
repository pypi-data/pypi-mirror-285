import json
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate

current_model = "llama3"


def classify_headline_category(headline_text: str, model_name: str = current_model):
    template = """You are a stocks market professional. Your job is to give a headline a category.

Here is the headline text you need to categorize, delimited by dashes:

--------------------------------------------------
{headline_text}
--------------------------------------------------

Here is the list, delimited by commas, of the authorized categories:

,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
analyst-ratings,
buybacks,
dividends,
economic-indicators,
earnings,
global-events,
industry-trends,
institutional-indices,
legal,
management,
media-coverage,
mergers-acquisitions,
product-related,
regulatory,
strategy
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

You are to output ONLY ONE DISTINCT CATEGORY, unchanged, from the list of authorized categories.
DO NOT add additional content, punctuation, explanation, characters, or any formatting in your output.
DON'T MAKE UP CATEGORIES THAT ARE NOT IN THE LIST!"""
    category_prompt = PromptTemplate.from_template(template)
    chain = category_prompt | get_model(model_name)
    output = chain.invoke({"headline_text": headline_text})
    return output.content.strip().lower()


def classify_headline_sentiment(headline_text: str, model_name: str = current_model):
    template = """You are a stocks market professional. Your job is to label a headline with a sentiment IN ENGLISH.

Headlines that mention upside range from slightly bullish to very bullish.
Uncertainty or mixed signals are never in the range of bullish headlines.

Headlines that range from slightly bearish to volatile mention or imply one or more of the following:
- drop in stock prices
- economic slowdown
- factory glut
- increased shares selling pressure
- legal issues or lawsuits
- negative economic indicators
- sales decline
- uncertainty in the market

Legal issues, lawsuits, and any other legal proceedings are NEVER TO BE LABELED AS NEUTRAL and should be classified within the range of slightly bearish to uncertain depending on the severity implied by the headline.

Only label a headline as neutral if it is only informative and not uncertain, and does not allow to derive any negative or positive outlook on the market.

Only label a headline as "very" bearish or bullish if it indicates far-reaching consequences or a significant change in the market.

Here is the headline text you need to label, delimited by dashes:

--------------------------------------------------
{headline_text}
--------------------------------------------------

Here is the list of the possible sentiments, delimited by commas:

,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
very bullish
bullish
slightly bullish
neutral
slightly bearish
bearish
very bearish
uncertain
volatile
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

You are to output ONLY ONE DISTINCT SENTIMENT, unchanged, from the list of possible sentiments.
DO NOT add additional content, punctuation, explanation, characters, or any formatting in your output.
DON'T MAKE UP SENTIMENTS THAT ARE NOT IN THE LIST!"""
    sentiment_prompt = PromptTemplate.from_template(template)
    chain = sentiment_prompt | get_model(model_name)
    output = chain.invoke({"headline_text": headline_text})
    return output.content.strip().lower()


def get_model(model_name: str = current_model):
    return ChatOllama(model=model_name)


def verifies_if_question_is_fully_answered(
    question: str, answer: str, model_name: str = current_model
):
    fully_answered_prompt = PromptTemplate(
        template="""You will determine if the provided question is fully answered by the provided answer.\n
Question:
{question}

Answer:
{answer}

You will respond with a JSON having 'fully_answered' as key and exactly either 'yes' or 'no' as value.""",
        input_variables=["question", "answer"],
    )
    fully_answered_chain = fully_answered_prompt | ChatOllama(
        format="json", model="phi3"
    )
    return json.loads(fully_answered_chain.invoke({"question": question, "answer": answer}).content)
