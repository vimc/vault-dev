from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(name="vault_dev",
      version="0.0.2",
      description="Run vault in dev mode from python scripts",
      long_description=long_description,
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      url="https://github.com/vimc/vault-dev",
      author="Rich FitzJohn",
      author_email="r.fitzjohn@imperial.ac.uk",
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      # Extra:
      long_description_content_type="text/markdown",
      setup_requires=["pytest-runner"],
      tests_require=["pytest"],
      requires=[
          "hvac",
          "requests"
      ])
