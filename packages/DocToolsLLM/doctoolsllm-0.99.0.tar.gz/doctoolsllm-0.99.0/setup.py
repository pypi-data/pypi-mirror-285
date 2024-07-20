from setuptools import setup, find_packages

long_description = """This package redirects to [winston_doc](https://pypi.org/project/wdoc/)"""

setup(
    name="DocToolsLLM",
    version="0.99.0",
    description="(Now winston_doc) A perfect AI powered RAG for document query and summary. Supports ~all LLM and ~all filetypes (url, pdf, epub, youtube (incl playlist), audio, anki, md, docx, pptx, oe any combination!)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thiswillbeyourgithub/WinstonDoc/",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    license="GPLv3",
    keywords=["RAG", "search", "summary", "summarize", "pdf", "documents", "doc", "docx",
              "youtube", "mp3", "embeddings", "AI", "LLM", "openai", "logseq", "doctools", "doctoolsllm", "winston_doc"],
    entry_points={
        'console_scripts': [
            'wdoc=WinstonDoc.__init__:cli_launcher',
            'winston_doc=WinstonDoc.__init__:cli_launcher',
        ],
    },
    python_requires=">=3.10",
    install_requires=[
        'wdoc',
    ],
)
