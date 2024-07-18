from typing import List

from pydantic import BaseModel, Field


class CourseArticleKeypointsModel(BaseModel):
    title: str = Field(description="Article title")
    key_points: str = Field(description="Article content")

    def to_plain_text(self) -> str:
        return f"Title: {self.title}\nKeypoints: {self.key_points}"


class CourseArticleModel(BaseModel):
    content: str = Field(description="Article content")
    questions: List[str] = Field(
        description="List of questions related to the article", default=[])

    def get_article_content(self) -> str:
        return f"""{self.content}"""

    def get_article_questions(self) -> str:
        if not self.questions:
            return ""
        return f"""Questions the reader may be interested in making after reading the article:
1. {self.questions[0]}
2. {self.questions[1]}
3. {self.questions[2]}"""


class CourseArticleWTitleModel(CourseArticleModel):
    title: str = Field(description="Article title")
    type: str = Field(description="Article type")

    def to_plain_text(self):
        result = ""
        result += f"-- Title: {self.title}"
        result += f"\n-- Content: {self.content}"
        result += f"\n-- Questions:"
        for q in self.questions:
            result += f"\n--- {q}"
        return result + "\n"
