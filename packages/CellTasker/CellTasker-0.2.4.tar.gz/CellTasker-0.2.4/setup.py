from setuptools import setup, find_packages

setup(
    name='CellTasker',
    version='0.2.4',
    packages=find_packages(),
    author='colorthoro',
    author_email='dream.0112@qq.com',
    description="CellTasker希望提供一个高效的任务调度和管理系统。",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://gitee.com/colorthoro/cellular',
    license='MIT',
    install_requires=['pyaml'],
    python_requires='>=3.1',
)
