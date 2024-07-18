import setuptools  # 导入setuptools打包工具

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SGML",
    version="2.0.0",
    author="Ruijin_Wang",
    author_email="wangrjcn@shu.edu.cn",
    description="A package for solution-guided machine learning method",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wangrjcn/SGML",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
