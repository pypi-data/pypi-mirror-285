from setuptools import setup, find_packages

setup(
    name='ostutor',
    version='0.3.1',
    description='The goal of the App is to develop a new tool that, after receiving a few keywords given by the user, returns possibly relevant commands and other further relevant help information.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Zhenxin Liang,Zijian Chen,Qiyong Wu',
    author_email='t202414655993206@eduxiji.net',
    url='https://gitlab.eduxiji.net/T202414655993206/project2210132-239674',
    license='Mulan PSL v1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click==8.1.7',
        'colorama==0.4.6',
        'nltk==3.8.1',
        'npyscreen==4.10.5',
        'pandas==2.2.2',
        'prompt_toolkit==3.0.43',
        'rich==13.7.1',
        'scikit_learn==1.5.1',
        'tqdm==4.66.4',
        'wcwidth==0.2.13',
        # windows-curses==2.3.3
        #'requirements.txt'
        #'some_dependency',  # 依赖项
    ],
    entry_points={
        'console_scripts': [
            'ostutor=OSTutor.__main__:cmd',
        ],
    },
)