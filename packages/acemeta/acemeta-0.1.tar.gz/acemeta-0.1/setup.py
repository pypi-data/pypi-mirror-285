from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as readme:
    description = readme.read() 

setup(
    name="acemeta",
    version="0.1",
    packages=find_packages(),
    install_requires=["requests"],  # Hier können Abhängigkeiten aufgelistet werden
    author="Annhilati",
    #author_email="Ihre Email",
    #description="Eine kurze Beschreibung Ihres Pakets",
    long_description=description,
    long_description_content_type="text/markdown",
    #url="https://example.com/mypackage",  # URL zu Ihrem Projekt (optional)
)
