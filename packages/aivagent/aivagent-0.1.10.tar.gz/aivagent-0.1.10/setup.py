from setuptools import setup, find_packages

setup(
    name='aivagent',
    version='0.1.10', # 2024.7.19
    packages=find_packages(),
    install_requires=[
        # 任何依赖项都在这里列出
    ],
    author='aiv.store',
    author_email='76881573@qq.com',
    description='Aiv Agent',
    # long_description=open('./readme.rts').read(),    #显示在 pypi.org 首页的项目介绍里 2024.6
    license='MIT',
    keywords='Aiv Agent',
    url='https://www.aiv.store'
)