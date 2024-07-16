from setuptools import setup, find_packages

setup(
    name='PathLikeDict',
    version='0.0.1',
    packages=find_packages(),
    author='colorthoro',
    author_email='dream.0112@qq.com',
    description='借鉴 pathlib.Path 链式操作方式，简化深字典的操作。',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://gitee.com/colorthoro/py-path-like-dict',
    license='MIT',
    python_requires='>=3.10',
)
