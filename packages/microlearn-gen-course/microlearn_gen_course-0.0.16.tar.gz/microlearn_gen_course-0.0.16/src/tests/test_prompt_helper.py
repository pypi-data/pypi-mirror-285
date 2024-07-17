"""
Test PromptHelper

Usage:
    pytest src/tests/test_prompt_helper.py -v --log-cli-level INFO
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from gen_course.prompt_helper import PromptHelper


load_dotenv(override=True)

logger = logging.getLogger(__name__)


def test_prompt_helper_get_prompt_course_title_desc_en():
    helper = PromptHelper()
    prompt_container = helper.get_prompt("gen_course_title_desc", "en")
    assert prompt_container.system_prompt == "Act like a copywriter expert in course editing"
    assert prompt_container.user_prompt == """Write a title of only 3 words and an introduction article to a course of approximately 40 words based on the following:
---
Description: {course_description}
---
Strictly output in JSON format. The JSON should have the following format:
{{
    "title": "...",
    "description": "..."
}}"""
    for expected_input_var in ["course_description"]:
        assert expected_input_var in prompt_container.input_vars


def test_prompt_helper_get_prompt_course_title_desc_it():
    helper = PromptHelper()
    prompt_container = helper.get_prompt("gen_course_title_desc", "it")
    assert prompt_container.system_prompt == "Sei uno scrittore specializzato nella creazione di materiali didattici per corsi."
    assert prompt_container.user_prompt == """Scrivi un titolo di sole 3 parole ed una prefazione al corso di circa 40 parole. Il corso è sul seguente argomento:
---
Descrizione: {course_description}
---
L'output deve essere in formato JSON. Il JSON deve avere il seguente formato:

{{
    "title": "...",
    "description": "..."
}}"""
    for expected_input_var in ["course_description"]:
        assert expected_input_var in prompt_container.input_vars


def test_prompt_helper_get_prompt_course_content_for_all_articles_en():
    helper = PromptHelper()
    prompt_container = helper.get_prompt("gen_course_content_for_all_articles", "en")
    assert prompt_container.system_prompt == "Act as a copywriter for a microlearning course"
    assert prompt_container.user_prompt == """Using the information provided below, generate {articles_count} articles for the course "{course_title}". Each article title should be a maximum of {article_title_length_words} words, and the content should be strictly minimum of {content_length_words} words in length. Each article should complete a topic of the course. Never use phrase such as "this article is about...". After each article, list 3 questions that a reader might have after reading the article.

Course information:
{course_description}

Strictly output in JSON format. The JSON should have the following format:
[
    {{
        "title": "...",
        "content": "...",
        "questions": [
            "...",
            "...",
            "..."
        ]
    }}
]"""
    for expected_input_var in ["articles_count", "course_title", "article_title_length_words", "content_length_words", "course_description"]:
        assert expected_input_var in prompt_container.input_vars


def test_prompt_helper_get_prompt_course_content_for_all_articles_it():
    helper = PromptHelper()
    prompt_container = helper.get_prompt("gen_course_content_for_all_articles", "it")
    assert prompt_container.system_prompt == "Sei uno scrittore specializzato nella creazione di materiali didattici per corsi."
    assert prompt_container.user_prompt == """Utilizzando l'informazione fornita sotto, genera {articles_count} articoli per il corso "{course_title}". Il titolo di ciascun articolo deve contenere al massimo {article_title_length_words} parole ed il contenuto di ogni articolo deve essere composto da un minimo di {content_length_words} parole. Ogni articolo deve completare in modo esauriente un capitolo del corso.  Non usare mai frasi come "questo articolo parlerà di..." . Dopo ogni articolo elenca tre domande che il lettore potrebbe avere in mente dopo aver letto l'articolo. 

Informazioni sul corso:
{course_description}

L'output deve essere in formato JSON. Il JSON deve avere il seguente formato:

[
    {{
        "title": "...",
        "content": "...",
        "questions": [
            "...",
            "...",
            "..."
        ]
    }}
]"""
    for expected_input_var in ["articles_count", "course_title", "article_title_length_words", "content_length_words", "course_description"]:
        assert expected_input_var in prompt_container.input_vars


def test_prompt_helper_get_prompt_course_content_coherently_en():
    helper = PromptHelper()
    prompt_container = helper.get_prompt("gen_course_content_coherently", "en")
    assert prompt_container.system_prompt == "You're a professional content writer for microlearning courses."
    assert prompt_container.user_prompt == """Following is the microlearning course generated:
===
{articles_text}
===
Rewrite each article content in such a way that there is no repeating concept, or there's no explicit reference to the course. Remove references such as "In this course", "This course covers", etc. Do not change title or questions for the articles.
Strictly output in JSON format. The JSON should have the following format:
[
    {{
        "title": "...",
        "content": "...",
        "questions": [
            "...",
            "...",
            "..."
        ]
    }}
]"""
    for expected_input_var in ["articles_text"]:
        assert expected_input_var in prompt_container.input_vars


def test_prompt_helper_get_prompt_course_content_coherently_it():
    helper = PromptHelper()
    prompt_container = helper.get_prompt("gen_course_content_coherently", "it")
    assert prompt_container.system_prompt == "Sei un redattore professionale di contenuti per corsi di microlearning"
    assert prompt_container.user_prompt == """Di seguito trovi un corso di microlearning:
===
{articles_text}
===
Riscrivi ciascun articolo in modo tale che non ci siano ripetizioni di concetti né riferimenti al corso stesso. Rimuovi frasi come "in questo corso ", "questo corso parlerà di… ", eccetera. Non cambiare nè i titoli nè le domande degli articoli. 
L'output deve essere in formato JSON. Il JSON deve avere il seguente formato:

[
    {{
        "title": "...",
        "content": "...",
        "questions": [
            "...",
            "...",
            "..."
        ]
    }}
]"""
    for expected_input_var in ["articles_text"]:
        assert expected_input_var in prompt_container.input_vars


def test_prompt_helper_get_prompt_image_gen_en():
    helper = PromptHelper()
    prompt_container = helper.get_prompt("gen_image_prompt", "en")
    assert prompt_container.system_prompt == """Act like a photo editor that defines the perfect image for an article and craft a prompt directing Midjourney to generate a photo-realistic image that will be published with the article. Include essential details and do not exceed 30 words.
No textual or letter elements should be included in the image.
Only write the prompt."""
    assert prompt_container.user_prompt == """The image I need is for the course described below:
---
Description: {description}
---
Strictly output in JSON format. The JSON should have the following format:
{{
    "prompt": "..."
}}"""
    for expected_input_var in ["description"]:
        assert expected_input_var in prompt_container.input_vars
