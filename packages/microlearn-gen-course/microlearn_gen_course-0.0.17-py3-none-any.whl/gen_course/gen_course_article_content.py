"""
Generator for course's article's content.
"""
import json
import logging
from typing import List

from .gen_base_v3 import GenBaseV3
from .models import CourseArticleWTitleModel
from .utils import extract_json_from_text

logger = logging.getLogger(__name__)


class GenCourseContentForAllArticles(GenBaseV3):
    """
    Generator class for course's article's content in batch using previous articles.
    """
    PROMPT_NAME = "gen_course_content_for_all_articles"

    def __init__(self, llm, lang: str, verbose: bool = False):
        self.logger = logging.getLogger(__name__)
        super().__init__(llm, lang, verbose, self.logger)

    def parse_output(self, output: str) -> List[CourseArticleWTitleModel]:
        try:
            self.logger.debug(f"Parsing output: {output}")
            articles = extract_json_from_text(output)
            return [CourseArticleWTitleModel(**article) for article in articles]
        except json.JSONDecodeError:
            self.logger.error(f"Output is not a valid JSON: {output}")
            raise

    def generate(self,
                 course_title: str,
                 course_description: str,
                 articles_count: int = 10,
                 article_title_length_words: int = 8,
                 content_length_words: int = 150,
                 ) -> List[CourseArticleWTitleModel]:
        return self.generate_output(
            course_title=course_title,
            course_description=course_description,
            articles_count=articles_count,
            article_title_length_words=article_title_length_words,
            content_length_words=content_length_words,
        )


class GenCourseContentForAllArticlesCoherently(GenBaseV3):
    PROMPT_NAME = "gen_course_content_coherently"

    def __init__(self, llm, lang: str, verbose: bool = False):
        self.logger = logging.getLogger(__name__)
        super().__init__(llm, lang, verbose, self.logger)
        self.generator_base = GenCourseContentForAllArticles(llm, lang, verbose)

    def parse_output(self, output: str) -> List[CourseArticleWTitleModel]:
        return self.generator_base.parse_output(output)

    def generate(self,
                 course_title: str,
                 course_description: str,
                 articles_count: int = 10,
                 article_title_length_words: int = 8,
                 content_length_words: int = 150,
                 ) -> List[CourseArticleWTitleModel]:
        article_list = self.generator_base.generate(
            course_title=course_title,
            course_description=course_description,
            articles_count=articles_count,
            article_title_length_words=article_title_length_words,
            content_length_words=content_length_words,
        )

        articles_text = ""
        for i, article in enumerate(article_list, start=1):
            articles_text += f"- Article {i}\n"
            articles_text += article.to_plain_text()
            articles_text += "\n"

        return self.generate_output(
            articles_text=articles_text,
        )
