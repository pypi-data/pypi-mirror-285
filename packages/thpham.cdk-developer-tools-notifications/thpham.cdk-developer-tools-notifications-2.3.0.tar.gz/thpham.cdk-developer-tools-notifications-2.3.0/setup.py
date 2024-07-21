import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "thpham.cdk-developer-tools-notifications",
    "version": "2.3.0",
    "description": "#slack / msteams / email notifications for developer tools: CodeCommit, CodeBuild, CodeDeploy, CodePipeline",
    "license": "MIT",
    "url": "https://github.com/thpham/cdk-constructs",
    "long_description_content_type": "text/markdown",
    "author": "thpham",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/thpham/cdk-constructs.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "thpham.cdk_developer_tools_notifications",
        "thpham.cdk_developer_tools_notifications._jsii"
    ],
    "package_data": {
        "thpham.cdk_developer_tools_notifications._jsii": [
            "cdk-developer-tools-notifications@2.3.0.jsii.tgz"
        ],
        "thpham.cdk_developer_tools_notifications": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "aws-cdk-lib>=2.141.0, <3.0.0",
        "constructs>=10.3.0, <11.0.0",
        "jsii>=1.95.0, <2.0.0",
        "publication>=0.0.3",
        "thpham.cdk-chatops>=2.3.0, <3.0.0",
        "typeguard~=2.13.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
