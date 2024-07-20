"""Util functions"""
import os
import sys
import zipfile
from pathlib import Path
from subprocess import run

import yaml

from .classroom.model import Course, CourseWork, Submission, Student, Attachment


def capture_io(script_name: str, inputs: list) -> str:
    """
    :param script_name:  name of the script to be tested
    :param inputs: list of inputs, one element per line
    :return: returns script output for the test case
    """
    inputs = "\n".join(inputs)
    p = run(
        f"{sys.executable} \'{script_name}\'",
        shell=True,
        input=inputs,
        text=True,
        capture_output=True,
    )

    return p.stdout.strip()


def extract_zip(source: str, destination: str) -> None:
    """
    Extract zip file at source to destination
    :param source:
    :param destination:
    :return:
    """
    with zipfile.ZipFile(source, 'r') as output:
        output.extractall(destination)


def create_unique_dir(parent_dir: str, new_dir_name: str) -> str:
    """
    creates a directory named new_dir_name
    if such a directory exists, it new directory will be created with unique name
    """
    os.chdir(parent_dir)

    if os.path.exists(new_dir_name) and os.listdir(new_dir_name):
        i = 1
        while os.path.exists(f"{new_dir_name}_{i}") and os.listdir(f"{new_dir_name}_{i}"):
            i += 1

        new_path = f"{new_dir_name}_{i}"

        os.mkdir(new_path)

        return new_path

    os.mkdir(new_dir_name)

    return new_dir_name


def get_current_course() -> Course:
    """
    Searches for .course.yaml file in current directory and returns the course entity from it
    :return:
    :raises: FileNotFoundError if .course.yaml file is not found
    """
    current_dir = [file for file in os.listdir('.') if os.path.isfile(file) and file == ".course.yaml"]
    if '.course.yaml' not in current_dir:
        raise FileNotFoundError("Can't find .course.yaml in this directory")

    with open('.course.yaml', 'r', encoding='utf8') as course_file:
        course = yaml.safe_load(course_file.read())

    return Course(id=course['id'], name=course['name'])


def find_descendant(file_name: str) -> str:
    """
    looks in previous paths for a file. returns a path to a file
    """

    path = Path(os.getcwd())

    while not os.path.exists(os.path.join(path, file_name)) and not os.path.ismount(path):
        path = path.parent.absolute()

    return_path = os.path.join(path, file_name)

    if not os.path.exists(return_path):
        raise FileNotFoundError(file_name)

    return os.path.join(path, file_name)


def write_course_yaml(course: Course, path: str) -> None:
    with open(os.path.join(path, ".course.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(course.__dict__, f)


def read_course_yaml(path: str) -> Course:
    with open(os.path.join(path, ".course.yaml"), "r", encoding="utf-8") as f:
        course_info = yaml.safe_load(f)

    return Course(id=course_info["id"], name=course_info["name"], description=course_info["description"],
                  section=course_info["section"])


def write_course_work_yaml(course_work: CourseWork, path: str) -> None:
    with open(os.path.join(path, ".course_work.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(course_work.__dict__, f)


def read_course_work_yaml(path: str) -> CourseWork:
    with open(os.path.join(path, ".course_work.yaml"), "r", encoding="utf-8") as f:
        course_work_info = yaml.safe_load(f)

    return CourseWork(id=course_work_info["id"],
                      title=course_work_info['title'],
                      description=course_work_info['description'],
                      course_id=course_work_info['course_id'],
                      link=course_work_info['link'])


def read_sumbission_yaml(path: str) -> Submission:
    with open(os.path.join(path, ".submission.yaml"), "r", encoding="utf-8") as f:
        submission_info = yaml.safe_load(f)

    return Submission(id=submission_info["id"], user_id=submission_info["user_id"],
                      course_id=submission_info["course_id"], coursework_id=submission_info["coursework_id"],
                      creation_time=submission_info["creation_time"], update_time=submission_info["update_time"],
                      attachments=[Attachment(id=value["id"], title=key, link=value["link"]) for key, value in
                                   submission_info["attachments"].items()], link=submission_info["link"])


def write_submission_yaml(submission: Submission, student: Student, path: str) -> None:
    with open(os.path.join(path, ".submission.yaml"), "w", encoding="utf-8") as f:
        submission_dict = submission.__dict__.copy()
        submission_dict["attachments"] = {attachment.title: {"id": attachment.id, "link": attachment.link} for
                                          attachment in submission_dict["attachments"]}
        submission_dict["student_name"] = student.name
        yaml.dump(submission_dict, f, allow_unicode=True)
