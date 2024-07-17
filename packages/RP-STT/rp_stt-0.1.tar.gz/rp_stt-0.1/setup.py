from setuptools import setup,find_packages

setup(
    name="RP-STT",
    version=0.1,
    author="Roy Perry",
    author_email="roypery2010@gmail.com",
    description="this is speech to text package created by Roy Perry"
)
packages = find_packages(),
install_requirements = [
    "selenium",
    "webdriver_manager"
]