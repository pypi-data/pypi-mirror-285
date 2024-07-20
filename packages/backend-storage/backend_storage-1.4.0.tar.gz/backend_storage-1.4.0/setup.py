from setuptools import setup, find_packages

setup(
    name="backend-storage",
    version="1.4.0",
    packages=find_packages(),
    install_requires=["requests", "fastapi"],
    description="提供了基于 Node.js 开发的 RESTful 接口，可以方便地进行数据的增删改查（CRUD）操作以及高效的数据搜索",
)
