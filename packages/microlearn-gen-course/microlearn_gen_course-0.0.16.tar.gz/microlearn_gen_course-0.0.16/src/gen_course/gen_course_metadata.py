"""
Generator for course's metadata(title, description, etc.) using the description as text.
"""
import json
import logging
from pydantic import BaseModel, Field

from .gen_base_v3 import GenBaseV3


class CourseMetadataModel(BaseModel):
    title: str = Field(
        description="title of the course of only 3 words")
    description: str = Field(
        description="description of the course which is an introduction article of maximum 40 words")


class GenCourseMetadata(GenBaseV3):
    """
    Generator class for course metadata(title, description, etc.) using the description as text.
    """
    PROMPT_NAME = "gen_course_title_desc"

    def __init__(self, llm, lang: str, verbose: bool = False):
        self.logger = logging.getLogger(__name__)
        super().__init__(llm, lang, verbose, self.logger)

    def parse_output(self, output: str) -> CourseMetadataModel:
        try:
            self.logger.debug(f"Parsing output: {output}")
            metadata = json.loads(output)
            return CourseMetadataModel(**metadata)
        except json.JSONDecodeError:
            self.logger.error(f"Output is not a valid JSON: {output}")
            raise

    def generate(self,
                 course_description: str,
                 ) -> CourseMetadataModel:
        return self.generate_output(
            course_description=course_description,
        )
