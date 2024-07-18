"""
Test CourseArticleWTitleModel

Usage:
    pytest src/tests/test_course_article_w_title_model.py -v --log-cli-level INFO
"""
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from gen_course.gen_course_article_content import CourseArticleWTitleModel


load_dotenv(override=True)

logger = logging.getLogger(__name__)


def test_to_plain_text():
    model = CourseArticleWTitleModel(
        content="Sample content",
        questions=[
            "Ques 1",
            "Ques 2",
            "Ques 3",
        ],
        title="Sample title",
    )
    res = model.to_plain_text()
    assert res == """-- Title: Sample title
-- Content: Sample content
-- Questions:
--- Ques 1
--- Ques 2
--- Ques 3
"""
