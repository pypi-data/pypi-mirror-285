from setuptools import setup, find_packages
import os

# 读取文件内容
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="qtmodel",
    version="0.5.1",
    author="dqy-zhj",
    author_email="1105417715@qq.com",
    description="python modeling for qt  24/07/11 ",
    long_description=long_description,  # 使用读取的 README.md 文件内容
    long_description_content_type="text/markdown",  # 指明内容格式为markdown
    url="https://github.com/Inface0443/pyqt",
    packages=find_packages(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        "Operating System :: OS Independent",
    ],
)
