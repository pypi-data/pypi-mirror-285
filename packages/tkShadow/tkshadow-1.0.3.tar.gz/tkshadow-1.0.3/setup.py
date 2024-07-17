import setuptools

with open("README.md", "r", encoding="utf-8") as fh:

    long_description = fh.read()
    setuptools.setup(
        name="tkShadow",  # 用自己的名替换其中的YOUR_USERNAME_
        version="1.0.3",  # 包版本号，便于维护版本
        author="CodeCrafter-TL",  # 作者，可以写自己的姓名
        author_email="1825456084@qq.com",  # 作者联系方式，可写自己的邮箱地址
        description="在您的 tkinter 项目上为控件或 Canvas 元素添加阴影",  # 包的简述
        long_description=long_description,  # 包的详细介绍，一般在README.md文件内
        long_description_content_type="text/markdown",
        url="https://github.com/codecrafter-tl/tkshadow",  # 自己项目地址，比如github的项目地址
        packages=setuptools.find_packages(
        ), 
        classifiers=["Programming Language :: Python :: 3", "License :: OSI Approved :: MIT License", "Operating System :: OS Independent"],
        python_requires='>=3.10',)
