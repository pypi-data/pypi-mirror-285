from setuptools import setup, find_packages

setup(
    name="ultralytics-8.2.30_no_kpts_filtering",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "ultralytics==8.2.30",
    ],
    author="YBHello",
    author_email="yll.berisha@hellocare.ai",
    description="A modified version of Ultralytics library version 8.2.30 that has no keypoints filtering.",
    # long_description=open("README.md").read(),  # Remove or comment out this line
    # long_description_content_type="text/markdown",  # Remove or comment out this line
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
