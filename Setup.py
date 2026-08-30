from setuptools import setup, find_packages

setup(
    name="wifitest",
    version="1.0.0",
    description="Authorized WiFi security testing framework for labs and red team engagements",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Security Research Team",
    license="MIT",
    python_requires=">=3.10",
    packages=find_packages(exclude=["tests", "docs"]),
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "scapy>=2.5.0",
        "psutil>=5.9.0",
        "jinja2>=3.1.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0", "pytest-cov"],
    },
    entry_points={
        "console_scripts": [
            "wifitest=wifitest.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Security",
    ],
)
