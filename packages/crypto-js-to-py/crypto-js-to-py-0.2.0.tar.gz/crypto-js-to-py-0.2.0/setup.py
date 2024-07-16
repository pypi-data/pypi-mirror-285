import setuptools

with open("./README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

about = {}
with open('./crypto_py/__version__.py') as f:
    exec(f.read(),None, about)


setuptools.setup(
    name="crypto-js-to-py",
    version=about['__version__'],
    author="Primice",
    author_email="1121796946@qq.com",
    description="基于pycryptodomex的二次封装,对CryptoJS的AES和CBC进行了简单的复刻",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    license='MIT',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[  # 依赖列表
       "pycryptodomex",
       "pydantic"
    ]
)