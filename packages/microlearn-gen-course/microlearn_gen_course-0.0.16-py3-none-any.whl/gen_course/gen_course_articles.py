import json
import logging
from typing import List

from .gen_base_v3 import GenBaseV3
from .models import CourseArticleWTitleModel, CourseArticleKeypointsModel
from .utils import extract_json_from_text


class GenCourseKeypoints(GenBaseV3):
    """
    Generator class for course's article's keypoints.
    """
    PROMPT_NAME = "gen_articles_keypoints"

    def __init__(self, llm, lang: str, verbose: bool = False):
        self.logger = logging.getLogger(__name__)
        super().__init__(llm, lang, verbose, self.logger)

    def parse_output(self, output: str) -> List[CourseArticleKeypointsModel]:
        try:
            self.logger.debug(f"Parsing output: {output}")
            articles = extract_json_from_text(output)["articles"]
            return [CourseArticleKeypointsModel(**article) for article in articles]
        except json.JSONDecodeError:
            self.logger.error(f"Output is not a valid JSON: {output}")
            raise

    def generate(self,
                 course_title: str,
                 course_description: str,
                 num_articles: int = 10,
                 ) -> List[CourseArticleKeypointsModel]:
        return self.generate_output(
            course_title=course_title,
            course_description=course_description,
            num_articles=num_articles,
        )


class GenCourseContent(GenBaseV3):
    """
    Generator class for course's article's content in batch using articles keypoints.
    """
    PROMPT_NAME = "gen_articles_content"

    def __init__(self, llm, lang: str, verbose: bool = False):
        self.logger = logging.getLogger(__name__)
        super().__init__(llm, lang, verbose, self.logger)
        self.keypoints_generator = GenCourseKeypoints(llm, lang, verbose)

    def parse_output(self, output: str) -> List[CourseArticleWTitleModel]:
        self.logger.debug(f"Parsing output: {output}")
        articles = extract_json_from_text(output)["articles"]
        return [CourseArticleWTitleModel(**article) for article in articles]

    def generate(self,
                 course_title: str,
                 course_description: str,
                 articles_count: int = 10,
                 max_words: int = 150,
                 min_words: int = 40,
                 ) -> List[CourseArticleWTitleModel]:

        articles_keypoints = self.keypoints_generator.generate(
            course_title=course_title,
            course_description=course_description,
            num_articles=articles_count,
        )

        titles_and_keypoints = ""
        for article in articles_keypoints:
            titles_and_keypoints += f"{article.to_plain_text()}\n\n"

        return self.generate_output(
            titles_and_keypoints=titles_and_keypoints,
            max_words=max_words,
            min_words=min_words
        )