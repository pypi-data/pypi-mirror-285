import pytest

from .useful_prompts import (
    classify_headline_sentiment,
    verifies_if_question_is_fully_answered,
)

tsla_bearish = """‘It Is Desolate’: China’s Glut of Unused Car Factories - Manufacturers like BYD, 
Tesla and Li Auto are cutting prices to move their electric cars. For gasoline-powered vehicles, the surplus of 
factories is even worse."""
tsla_bearish2 = """U.S. Accuses Two Men of Stealing Tesla Trade Secrets - Federal prosecutors said the pair tried to 
sell technology to manufacture batteries for electric cars that belonged to the company."""


@pytest.mark.parametrize(
    "headline_input,expected",
    [
        (
            {
                "headline_text": (
                    "Asure Partners with Key Benefit Administrators",
                    "to Offer Proactive Health Management Plan (PHMP) to Clients",
                )
            },
            {
                "possible_sentiments": [
                    "bullish",
                    "neutral",
                    "slightly bullish",
                    "very bullish",
                ]
            },
        ),
        (
            {
                "headline_text": (
                    "Everbridge Cancels Fourth Quarter",
                    "and Full Year 2023 Financial Results Conference Call",
                )
            },
            {
                "possible_sentiments": [
                    "bearish",
                    "neutral",
                    "slightly bearish",
                    "uncertain",
                    "very bearish",
                ]
            },
        ),
        (
            {
                "headline_text": (
                    "This Analyst With 87% Accuracy Rate Sees Around 12% Upside In Masco -",
                    "Here Are 5 Stock Picks For Last Week From Wall Street's Most Accurate Analysts "
                    "- Masco (NYSE:MAS)",
                )
            },
            {"possible_sentiments": ["bullish", "slightly bullish", "very bullish"]},
        ),
        (
            {
                "headline_text": "Tesla leads 11% annual drop in EV prices as demand slowdown continues"
            },
            {"possible_sentiments": ["bearish", "slightly bearish", "very bearish"]},
        ),
        (
            {
                "headline_text": "Elon Musk Dispatches Tesla's 'Fireman' to China Amid Slowing Sales"
            },
            {"possible_sentiments": ["bearish", "slightly bearish"]},
        ),
        (
            {
                "headline_text": "OpenAI co-founder Ilya Sutskever says he will leave the startup"
            },
            {
                "possible_sentiments": [
                    "bearish",
                    "neutral",
                    "slightly bearish",
                    "uncertain",
                ]
            },
        ),
        (
            {
                "headline_text": "Hedge funds cut stakes in Magnificent Seven to invest in broader AI boom"
            },
            {
                "possible_sentiments": [
                    "bearish",
                    "bullish",
                    "neutral",
                    "slightly bearish",
                    "slightly bullish",
                ]
            },  # the "broader AI boom" part can be seen as bullish
        ),
        (
            {
                "headline_text": "Current Climate: California, Tesla And The EV Market's Mixed Signals"
            },
            {"possible_sentiments": ["neutral", "slightly bearish", "uncertain"]},
        ),
        (
            {
                "headline_text": "Musk, Tesla shareholder to propose a stay of pay ruling during appeal - court filing"
            },
            {"possible_sentiments": ["slightly bearish", "uncertain"]},
        ),
        (
            {
                "headline_text": "Tesla settles with former employee over racial discrimination claims"
            },
            {"possible_sentiments": ["bearish", "slightly bearish"]},
        ),
        (
            {
                "headline_text": "Microsoft Seeks to Dismiss Parts of Suit Filed by The New York Times"
            },
            {"possible_sentiments": ["bearish", "slightly bearish"]},
        ),
        (
            {
                "headline_text": "Any hope for a cheaper Tesla model may be on hold for now. But how about a Tesla taxi for your troubles?"
            },
            {
                "possible_sentiments": [
                    "bearish",
                    "slightly bearish",
                    "slightly bullish",
                    "neutral",
                    "uncertain",
                ]
            },
        ),
        (
            {
                "headline_text": "Musk Now Says He Opposes Tariffs On Chinese EVs—Here's What He Had Said Earlier"
            },
            {"possible_sentiments": ["neutral", "slightly bearish", "uncertain"]},
        ),
        (
            {
                "headline_text": "China's BYD, SAIC's MG undecided on EV price hikes due to tariffs, sources say"
            },
            {
                "possible_sentiments": [
                    "bearish",
                    "neutral",
                    "slightly bearish",
                    "uncertain",
                ]
            },
        ),
        (
            {
                "headline_text": "The fight over the future of plastics - As countries negotiate a landmark agreement to reduce plastic pollution, the industry is fighting a battle over regulations and over its image."
            },
            {"possible_sentiments": ["neutral", "slightly bearish", "uncertain"]},
        ),
        (
            {
                "headline_text": "Hackers for China, Russia and Others Used OpenAI Systems, Report Says - Microsoft and OpenAI said the A.I. had helped groups with ties to China, Russia, North Korea and Iran mostly with routine tasks."
            },
            {"possible_sentiments": ["bearish", "neutral", "slightly bearish"]},
        ),
        (
            {
                "headline_text": tsla_bearish,
            },
            {
                "possible_sentiments": [
                    "bearish",
                    "slightly bearish",
                    "uncertain",
                    "very bearish",
                ]
            },
        ),
        (
            {
                "headline_text": tsla_bearish2,
            },
            {
                "possible_sentiments": [
                    "bearish",
                    "slightly bearish",
                    "uncertain",
                ]
            },
        ),
    ],
)
def test_classify_sentiment(headline_input, expected):
    assert (
        classify_headline_sentiment(**headline_input) in expected["possible_sentiments"]
    )


@pytest.mark.parametrize(
    "q_a,expected",
    [
        (
            {
                "question": "What is the capital of France?",
                "answer": "Paris",
            },
            {"fully_answered": "yes"},
        ),
        (
            {
                "question": "What is the capital of France?",
                "answer": "It's a magic city with a lot of history and culture.",
            },
            {"fully_answered": "no"},
        ),
    ],
)
def test_verifies_if_question_is_fully_answered(q_a, expected):
    assert verifies_if_question_is_fully_answered(**q_a)["fully_answered"] == expected["fully_answered"]
