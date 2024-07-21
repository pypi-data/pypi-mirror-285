"""
# File       : setup.py
# Time       ：2023/9/14 15:29
# Author     ：xuewei zhang
# Email      ：jingmu_predict@qq.com
# version    ：python 3.8
# Description：
"""
from setuptools import setup, find_packages

setup(
    name="ai_tools_zxw",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'xlwt',
        'psutil',
        'ultralytics',
        'opencv-python',
        'matplotlib',
        'tqdm',
        'pycocotools'
        # 依赖的其他包，例如：'requests>=2.0.0'
    ],
    author="XueWei Zhang",
    author_email="tonson_predict@qq.com",
    description="常用的人工智能操作的中文工具包。",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sunshineinwater/",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
