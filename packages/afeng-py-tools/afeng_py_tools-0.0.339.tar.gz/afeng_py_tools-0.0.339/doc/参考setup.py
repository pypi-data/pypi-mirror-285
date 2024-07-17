from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='thekey',
    version='2.0.0',
    description='Help You Find Any Text Queqly!|帮你快速查询文本！',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='xxxx',
    author_email='python@xxxx.com',
    py_modules=['thekey'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'findit=thekey:findit']
    }
)