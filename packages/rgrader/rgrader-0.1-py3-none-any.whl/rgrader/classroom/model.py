"""Models for interacting with Google Classroom API."""
from dataclasses import dataclass


@dataclass
class Course:
    """Course in classroom"""
    id: str
    name: str
    section: str = None
    description: str = None


@dataclass
class CourseWork:
    """CourseWork in classroom"""
    id: str
    title: str
    description: str
    course_id: str
    link: str


@dataclass
class Attachment:
    """Attachment to google classroom submission"""
    id: str
    title: str
    link: str


@dataclass
class Submission:
    """Submission in classroom"""
    id: str
    user_id: str
    course_id: str
    coursework_id: str
    creation_time: str
    update_time: str
    attachments: list[Attachment]
    link: str


@dataclass
class GradingRule:
    """
    Keeps data on testing of separate entry in submission
    (i.e. file in submitted archive )
    """

    filename: str
    weight: str
    test_path: str

    @property
    def task_name(self) -> str:
        return self.filename.split('.')[0]


@dataclass
class GradingSchema:
    """
    Contains data on how to test and grade submission
    Attributes:
        name: The name of grading scheme
        total_grade: The total grade of the grading

    """

    name: str
    total_grade: int
    rules: list[GradingRule]

    def __post_init__(self):
        """
        Validate passed data.
        1. total_grade > 0
        2. test rules weights sum up to 100
        """
        if self.total_grade <= 0:
            raise ValueError("Total grade must be greater than 0")
        if sum(rule.weight for rule in self.rules) != 100:
            raise ValueError("Weights in grading rules must sum up to 100")


@dataclass
class GradingResult:
    """Keeps data about grade and comment to submission"""
    submission: Submission
    grade: float
    comment: str


@dataclass
class Student:
    id: str
    name: str
