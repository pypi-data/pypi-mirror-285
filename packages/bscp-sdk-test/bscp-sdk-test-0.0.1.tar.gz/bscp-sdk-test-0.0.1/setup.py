# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
import setuptools

about = {}
# with open("pyproject.toml") as f:
#     exec(f.read(), about)

with open("readme.md") as f:
    readme = f.read()

requires = [
    "grpcio>=1.60.0",
    "typing-extensions>=4.9.0",
    "protobuf >=4.25.2",
]

setuptools.setup(
    name="bscp-sdk-test",
    packages=setuptools.find_packages(),
    install_requires=requires,
    zip_safe=True,
    version="0.0.1",
    description="The Python SDK for blueking bscp project.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="blueking <blueking@tencent.com>",
    url="https://github.com/LidolLxf/bscp-sdk-test",
    keywords=["python", "bscp"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)