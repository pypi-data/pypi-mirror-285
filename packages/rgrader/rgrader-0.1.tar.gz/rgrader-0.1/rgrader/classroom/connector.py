"""Classroom API connector"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .model import Course, CourseWork, Attachment, Submission, Student
from ..exceptions import EntityNotFound


class ClassroomConnector:
    """Connector to classroom API"""

    SCOPES = ["https://www.googleapis.com/auth/classroom.courses.readonly",
              "https://www.googleapis.com/auth/classroom.coursework.students",
              "https://www.googleapis.com/auth/classroom.rosters"]

    def __init__(self, credentials: str) -> None:
        """
        Initialize classroom connector

        :param credentials_file str: path to credentials file
        """

        self._service = build("classroom", "v1", credentials=credentials)
        self.courses = []

    def get_courses(self) -> list[Course]:
        """
        Return dict of (course_name, course_info)
        """

        try:
            page_token = None

            while True:
                response = self._service.courses().list(pageToken=page_token, pageSize=100).execute()

                page_courses = [Course(id=course['id'],
                                       name=course['name'],
                                       section=course.get('section'),
                                       description=course.get('descriptionHeading')) for course in
                                response.get("courses", [])]
                self.courses.extend(page_courses)
                page_token = response.get("nextPageToken", None)

                if not page_token:
                    break

            return self.courses
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise error

    def get_courseworks(self, course_id: str):
        """
        Return list of all courseworks from specified course

        :param course_id: course from which list courseworkd
        :return:
        """

        coursework = []
        page_token = None

        try:
            while True:
                response = self._service.courses().courseWork().list(
                    pageToken=page_token, courseId=course_id,
                    pageSize=10
                ).execute()
                page_courseworks = [
                    CourseWork(id=coursework['id'],
                               title=coursework['title'],
                               description=coursework.get("description"),
                               course_id=course_id,
                               link=coursework['alternateLink'])
                    for coursework in response.get("courseWork", [])
                ]

                coursework.extend(page_courseworks)

                page_token = response.get("nextPageToken", None)
                if not page_token:
                    break
        except HttpError as error:
            print(f"An error occurred: {error}")

        return coursework

    def get_coursework_by_uuid(self, course_id, coursework_uuid):
        """
        Get coursework entity by course_id and coursework_uuid [id from the
        URL address in Classroom web client]
        :param course_id: id of course
        :param coursework_uuid: uuid of coursework [id from the
        URL address in Classroom web client]
        :return: coursework entity
        :raises: EntityNotFound if search failed
        """

        coursework = [coursework for coursework in self.get_courseworks(course_id=course_id)
                      if coursework.link.split('/')[6] == coursework_uuid]
        if not coursework:
            raise EntityNotFound(f"There is no coursework with id {coursework_uuid}")

        coursework = coursework[0]

        return coursework

    def get_submissions(self, course_id: str, coursework_id: str) -> list:
        """
        Return all submissions from course with [course_id] for assignment [coursework_id]
        :param course_id:
        :param coursework_id:
        :return:
        """

        submissions = []
        page_token = None

        try:
            while True:
                coursework = self._service.courses().courseWork()
                response = (
                    coursework.studentSubmissions()
                    .list(
                        pageToken=page_token,
                        courseId=course_id,
                        courseWorkId=coursework_id,
                        pageSize=10,
                    )
                    .execute()
                )

                for submission in response.get("studentSubmissions", []):
                    attachments = []

                    for attachment in submission['assignmentSubmission'].get('attachments', []):
                        attachment = attachment['driveFile']
                        attachments.append(Attachment(id=attachment['id'], title=attachment['title'],
                                                      link=attachment['alternateLink']))
                    submissions.append(Submission(id=submission['id'], user_id=submission['userId'],
                                                  attachments=attachments, course_id=course_id,
                                                  coursework_id=coursework_id, link=submission['alternateLink'],
                                                  creation_time=submission.get("creationTime"),
                                                  update_time=submission.get("updateTime")))

                page_token = response.get("nextPageToken", None)

                if not page_token:
                    break

        except HttpError as error:
            print(f"An error occurred: {error}")
            submissions = None

        return submissions

    def get_submission_by_uuid(self, course_id: str, coursework_id: str, submission_uuid: str) -> Submission:
        """
        Get submission entity by course_id, coursework_id and submission_uuid
        [id from the URL address in Classroom web client]
        :param course_id: id of course
        :param coursework_id: id of coursework
        :param submission_uuid: id of submission [id from the
        URL address in Classroom web client]
        :return: submission entity
        :raises: EntityNotFound if search failed
        """

        submission = [submission for submission in self.get_submissions(course_id=course_id,
                                                                        coursework_id=coursework_id)
                      if submission.link.split('/')[-1] == submission_uuid
                      ]
        if not submission:
            raise EntityNotFound(f"There is no coursework with id {submission_uuid}")

        submission = submission[0]

        return submission

    def grade_submission(self, submission: Submission, grade: int) -> None:
        """Grade submission with grade"""

        studentSubmission = {
            'assignedGrade': 99,
            'draftGrade': 80
        }
        self._service.courses().courseWork().studentSubmissions().patch(
            courseId=submission.course_id,
            courseWorkId=submission.coursework_id,
            id=submission.id,
            updateMask='assignedGrade,draftGrade',
            body=studentSubmission).execute()

    def get_students(self, course_id: str):
        """
        Return list of all students from specified course

        :param course_id: course from which list students
        :return:
        """

        students = {}
        page_token = None

        try:
            while True:

                response = self._service.courses().students().list(
                    pageToken=page_token, courseId=course_id,
                    pageSize=10
                ).execute()

                for student in response.get("students", []):
                    students[student['userId']] = Student(id=student["userId"],
                                                          name=student["profile"]["name"]["fullName"], )

                page_token = response.get("nextPageToken", None)
                if not page_token:
                    break
        except HttpError as error:
            print(f"An error occurred: {error}")

        return students
