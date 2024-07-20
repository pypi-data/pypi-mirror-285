import argparse
import os
import shutil
from argparse import ArgumentParser

import inquirer
import yaml

from .model import Course, CourseWork, GradingRule, GradingResult, Student
from ..classroom.model import Submission, GradingSchema
from ..services import drive_service, classroom_service
from ..test_runner import run_tests_for
from ..utils import create_unique_dir, extract_zip, get_current_course, write_course_yaml, read_course_yaml, \
    write_course_work_yaml, read_sumbission_yaml, write_submission_yaml, read_course_work_yaml


def run_no_args_argparse(argument_parser: argparse.ArgumentParser) -> None:
    """Add necessary arguments to argparse"""
    # argument_parser.add_argument()
    pass


def get_course(*args):
    courses = classroom_service.get_courses()

    course_choices = {course.name: course for course in courses}

    questions = [
        inquirer.List('course', message="Select course", choices=list(course_choices.keys())),
    ]

    selected_course = course_choices[inquirer.prompt(questions)['course']]

    new_path = create_unique_dir(os.getcwd(), selected_course.name)

    write_course_yaml(selected_course, new_path)


def choose_course_work(*args):
    if not os.path.exists(".course.yaml"):
        raise FileNotFoundError(".course.yaml not found. What course do you want?")

    course_info = read_course_yaml(os.getcwd())

    course_works = {assignment.title: assignment for assignment in classroom_service.get_courseworks(course_info.id)}

    questions = [
        inquirer.List('assignment', message="Select assignment", choices=list(course_works.keys())),
    ]

    selected_course = course_works[inquirer.prompt(questions)['assignment']]

    get_course_work(course_info, selected_course)


def get_submission(submission: Submission, target_dir: str, student: Student):
    attachments_updated = True

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    if os.path.exists(os.path.join(target_dir, ".submission.yaml")):
        submission_info = read_sumbission_yaml(target_dir)

        if submission_info.update_time == submission.update_time:
            attachments_updated = False
        else:
            write_submission_yaml(submission, student, target_dir)
    else:
        write_submission_yaml(submission, student, target_dir)

    if attachments_updated:
        for attachment in submission.attachments:
            target_download_path = os.path.join(target_dir, attachment.title)
            drive_service.download_file(attachment.id, target_download_path)
            if attachment.title.endswith(".zip"):
                extract_zip(target_download_path, target_dir)
                os.remove(target_download_path)


def get_course_work(course_info: Course, course_work: CourseWork, target_dir: str = "."):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    course_work_dir = os.path.join(target_dir, course_work.title)
    if not os.path.exists(course_work_dir):
        os.makedirs(course_work_dir)

    if not os.path.exists(os.path.join(course_work_dir, ".course_work.yaml")):
        write_course_work_yaml(course_work, course_work_dir)

    students = classroom_service.get_students(course_info.id)

    for submission in classroom_service.get_submissions(course_info.id, course_work.id):
        get_submission(submission, os.path.join(course_work_dir, students[submission.user_id].name),
                       students[submission.user_id])


def get_assignments(*args):
    if not os.path.exists(".course.yaml"):
        raise FileNotFoundError(".course.yaml not found. What course do you want?")

    with open(".course.yaml", "r", encoding="utf-8") as f:
        course_info = yaml.safe_load(f)
        print(course_info)

    course_works = {assignment.title: assignment for assignment in classroom_service.get_courseworks(course_info["id"])}

    questions = [
        inquirer.List('assignment', message="Select assignment", choices=list(course_works.keys())),
    ]

    selected_course = course_works[inquirer.prompt(questions)['assignment']]
    print(selected_course)


def setup_grade_submissions(argument_parser: ArgumentParser) -> None:
    """Setup argument parser for using action grade_submissions"""
    argument_parser.add_argument('-cw', '--coursework', help="Id of the coursework from URL in classroom")
    argument_parser.add_argument('-sid', '--submission-id', help="Id of the submission from URL in classroom")
    argument_parser.add_argument('-sf', '--submission-folder', help="Path to the folder with submissions of coursework")
    argument_parser.add_argument('-cg', '--classroom-grade',
                                 help="If this option is provided, automatically grade submission in classroom."
                                      "Otherwise, create csv with grades.", action="store_true")
    argument_parser.add_argument('-e', '--export-file', help="Path to the CSV file with grades.")
    argument_parser.add_argument("-gs", "--grading-schema", help="Path to the grading_schema YAML file")


def get_submissions_to_grade(course: Course, coursework: CourseWork, args: argparse.Namespace) -> list[Submission]:
    """
    Return the list of all submissions that must be graded
    If only course and coursework are provided (no additional data in args), then return all submissions
    If --submission-id is provided, grade only submission with that ID [from URL in classroom web]
    If --submission-folder provided, return all submissions from that folder

    :param course: Course, where to search for submissions
    :param coursework: CourseWork, where to search for submissions
    :param args: args from command line
    :return: list of submissions
    :raises: EntityNotFound if could not find any submissions with provided arguments
    """

    if args.submission_id is not None:
        return [classroom_service.get_submission_by_uuid(course_id=course.id, coursework_id=coursework.id,
                                                         submission_uuid=args.submission_id)]

    return classroom_service.get_submissions(course_id=course.id, coursework_id=coursework.id)


def parse_grading_schema(grading_schema_path: str) -> GradingSchema:
    """
    Parse grading schema from YAML file
    :param grading_schema_path: path to YAML file
    :return: GradingSchema instance
    """

    with open(grading_schema_path, 'r', encoding='utf8') as grading_schema_file:
        grading_schema_dict = yaml.safe_load(grading_schema_file)

    rules = []
    for rule in grading_schema_dict['schema']['rules'].values():
        rules.append(GradingRule(**rule))

    return GradingSchema(name=grading_schema_dict['schema']['name'],
                         total_grade=grading_schema_dict['schema']['total_grade'],
                         rules=rules)


def grade_submission(submission: Submission, grading_schema: GradingSchema, working_dir: str) -> GradingResult:
    """Grade submission by"""

    gained_grade = 0
    tester_output = ""

    for rule in grading_schema.rules:
        test_path = os.path.join(TMP_TESTS_DIR, f"{rule.task_name}_tests.py")

        script_destination = os.path.join(working_dir, rule.filename)

        if not os.path.exists(script_destination):
            tester_output += f"File {rule.filename} was not found\n"
            continue

        result = run_tests_for(script_path=script_destination, test_script_path=test_path)

        result.stream.seek(0)
        tester_output += result.stream.read()

        success_percentage = result.gained_points / result.total_points

        gained_grade += success_percentage * rule.weight * grading_schema.total_grade / 100

    return GradingResult(submission=submission, grade=gained_grade, comment=tester_output)


def export_grades_and_comments(results: list[GradingResult], students: list[Student], export_file_path: str) -> None:
    """
    Write all grades and comments to grading to CSV file
    :param results: list of GradingResult for each submission
    :param students: list of Students of course
    :param export_file_path: path to export file
    :return: None
    """

    with open(export_file_path, 'w', encoding='utf8') as export_file:
        export_file.write("Student,Grade,Comment\n")
        for result in results:
            export_file.write(f"{students[result.submission.user_id].name},{result.grade},\"{result.comment}\"\n")


TMP_SUBMISSIONS_DIR = '.submissions'
TMP_TESTS_DIR = '.rgrader_tests'


def collect_submissions(course: Course, coursework: CourseWork, submissions: list[Submission],
                        students: list[Student], args: argparse.ArgumentParser) -> None:
    """Download all submissions attachments for this grading"""

    if not os.path.exists(TMP_SUBMISSIONS_DIR):
        os.mkdir(TMP_SUBMISSIONS_DIR)

    if args.submission_id is not None:
        student = students[submissions[0].user_id]
        target_dir = os.path.join(TMP_SUBMISSIONS_DIR, coursework.title, student.name)
        get_submission(submission=submissions[0], student=student, target_dir=target_dir)
    else:
        get_course_work(
            course_info={"id": course.id},
            course_work=coursework,
            target_dir=TMP_TESTS_DIR
        )


def collect_test_scripts(grading_schema: GradingSchema) -> None:
    """Copy tests, specified in grading_schema to TMP_TESTS_DIR"""

    if not os.path.exists(TMP_TESTS_DIR):
        os.mkdir(TMP_TESTS_DIR)

    for rule in grading_schema.rules:
        copied_tests_path = os.path.join(TMP_TESTS_DIR, f"{rule.task_name}_tests.py")
        shutil.copyfile(rule.test_path, copied_tests_path)


def read_submission_from_dir(path: str) -> list[Submission]:
    """
    Read submissions from a directory
    :param path: path to base folder of coursework
    """

    if not os.path.exists(os.path.join(path, '.course_work.yaml')):
        raise ValueError(f"There is not .course_work.yaml in the given path {path}")

    submissions = []
    for submission_dir in os.listdir(path):
        base_path = os.path.join(path, submission_dir)
        if not os.path.isdir(base_path):
            continue

        if not os.path.exists(os.path.join(base_path, '.submission.yaml')):
            continue

        submissions.append(read_sumbission_yaml(base_path))

    return submissions


def grade_submissions(args: argparse.Namespace) -> None:
    """Grade submission from classroom"""

    course = get_current_course()
    students = classroom_service.get_students(course_id=course.id)
    grading_schema = parse_grading_schema(args.grading_schema)
    collect_test_scripts(grading_schema)

    if args.submission_folder is None:
        coursework = classroom_service.get_coursework_by_uuid(course_id=course.id, coursework_uuid=args.coursework)
        submissions = get_submissions_to_grade(course=course, coursework=coursework, args=args)
        collect_submissions(course, coursework, submissions, students, args)
    else:
        coursework = read_course_work_yaml(args.submission_folder)
        submissions = read_submission_from_dir(args.submission_folder)

    results = []

    for submission in submissions:

        if args.submission_folder is None:
            working_dir = os.path.join(TMP_SUBMISSIONS_DIR, coursework.title, students[submission.user_id].name)
        else:
            working_dir = os.path.join(coursework.title, students[submission.user_id].name)

        results.append(grade_submission(submission=submission, grading_schema=grading_schema, working_dir=working_dir))

    if args.export_file is not None:
        export_grades_and_comments(results, students=students, export_file_path=args.export_file)

    if args.submission_folder is None:
        shutil.rmtree(TMP_SUBMISSIONS_DIR)

    shutil.rmtree(TMP_TESTS_DIR)
