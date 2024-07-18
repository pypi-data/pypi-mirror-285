"""
Generator for course's image generation prompt via other tools like MidJourney.
"""
import json
import logging
from pydantic import BaseModel, Field

from .gen_base_v3 import GenBaseV3


class CourseImagePromptModel(BaseModel):
    prompt: str = Field(
        description="prompt of maximum 30 words for image generation of the course.")


class GenCourseImagePrompt(GenBaseV3):
    """
    Generator class for course image prompt.
    """
    PROMPT_NAME = "gen_image_prompt"

    def __init__(self, llm, verbose: bool = False):
        self.logger = logging.getLogger(__name__)
        super().__init__(llm, lang=None, verbose=verbose, logger=self.logger)

    def parse_output(self, output: str) -> CourseImagePromptModel:
        try:
            self.logger.debug(f"Parsing output: {output}")
            prompt = json.loads(output)
            return CourseImagePromptModel(**prompt)
        except json.JSONDecodeError:
            self.logger.error(f"Output is not a valid JSON: {output}")
            raise

    def generate(self,
                 description: str,
                 prompt_length_words: int = 30,
                 ) -> CourseImagePromptModel:
        return self.generate_output(
            description=description,
            prompt_length_words=prompt_length_words,
        )
