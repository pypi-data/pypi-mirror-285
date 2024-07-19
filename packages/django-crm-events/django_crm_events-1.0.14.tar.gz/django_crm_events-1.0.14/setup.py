from setuptools import setup, find_packages

setup(
    name="django-crm-events",
    version="1.0.14",
    packages=find_packages(include=["crm_events", "crm_events.*"]),
    install_requires=["Django", "requests", "cachetools"],
)
