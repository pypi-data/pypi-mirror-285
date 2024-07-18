from setuptools import setup, find_packages

setup(
    name='event_listener',
    version='0.0.1',
    packages=find_packages(),
    author='Aniket Tiratkar',
    author_email='info@coredge.io',
    description='An asynchronous kafka event listener to make action dispatching easier',
    url='https://github.com/coredgeio/event_listener',
    install_requires=open('event_listener/requirements.txt', encoding='utf-8').read().split()
)
