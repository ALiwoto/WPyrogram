#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import re
import runpy
from setuptools import Extension, setup, find_packages
from setuptools.command.build_py import build_py

with open("requirements.txt", encoding="utf-8") as r:
    requires = [i.strip() for i in r]

with open("pyrogram/__init__.py", encoding="utf-8") as f:
    version = re.findall(r"__version__ = \"(.+)\"", f.read())[0]

with open("README.md", encoding="utf-8") as f:
    readme = f.read()


class BuildPy(build_py):
    def run(self):
        runpy.run_path("compiler/api/compiler.py")["start"]()
        runpy.run_path("compiler/errors/compiler.py")["start"]()
        self.distribution.packages = find_packages(exclude=["compiler*", "tests*"])
        self.packages = self.distribution.packages
        super().run()


setup(
    name="WPyrogram",
    version=version,
    description="Elegant, modern and asynchronous Telegram MTProto API framework in Python for users and bots - Woto's experimental fork",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/ALiwoto/WPyrogram",
    download_url="https://github.com/ALiwoto/WPyrogram",
    author="Dan",
    author_email="dan@pyrogram.org",
    license="LGPLv3",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet",
        "Topic :: Communications",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
    keywords="telegram chat messenger mtproto api client library python",
    project_urls={
        "Tracker": "https://github.com/ALiwoto/WPyrogram/issues",
        "Community": "https://t.me/Pyrogram",
        "Source": "https://github.com/ALiwoto/WPyrogram",
        "Documentation": "https://docs.pyrogram.org",
    },
    python_requires=">=3.14",
    package_data={
        "pyrogram": ["py.typed"],
    },
    packages=find_packages(exclude=["compiler*", "tests*"]),
    zip_safe=False,
    install_requires=requires,
    cmdclass={"build_py": BuildPy},
    ext_modules=[
        Extension(
            "pyrogram.crypto._tgcrypto",
            sources=[
                "pyrogram/crypto/tgcrypto/tgcrypto.c",
                "pyrogram/crypto/tgcrypto/aes256.c",
                "pyrogram/crypto/tgcrypto/ige256.c",
                "pyrogram/crypto/tgcrypto/ctr256.c",
                "pyrogram/crypto/tgcrypto/cbc256.c",
            ],
            define_macros=[("Py_LIMITED_API", "0x030E0000")],
            py_limited_api=True,
        )
    ],
    options={"bdist_wheel": {"py_limited_api": "cp314"}},
)
