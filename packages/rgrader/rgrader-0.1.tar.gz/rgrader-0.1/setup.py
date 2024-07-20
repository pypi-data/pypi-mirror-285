from setuptools import setup, find_packages

setup(
    name="rgrader",
    version='0.1',
    packages=find_packages(),
    description="A simple grader for python problems",
    install_requires=[
        'inquirer==3.3.0',
        "google-api-core==2.19.0",
        "google-api-python-client==2.131.0",
        "google-auth==2.29.0",
        "google-auth-httplib2==0.2.0",
        "google-auth-oauthlib==1.2.0",
        "googleapis-common-protos==1.63.0",
    ],
    entry_points={
        'console_scripts': [
            "grade = rgrader:grade"
        ]
    }
)
