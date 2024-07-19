import os
from setuptools import setup, find_packages

package_name_prefix = os.environ.get("PACKAGE_NAME_PREFIX", "")

setup_args = dict(
    name=f"{package_name_prefix}jupyter-activity-monitor-extension",
    version="0.2.0",
    url="https://aws.amazon.com/sagemaker/",
    author="Amazon",
    description="Jupyter Server Extension for checking last activity time",
    license="Amazon Software License",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "jupyter_server >= 2.0.0",
        "tornado",
        "jmespath",
    ],
    include_package_data=True,
    data_files=[
        (
            "etc/jupyter/jupyter_server_config.d",
            [
                "jupyter-config/jupyter_server_config.d/jupyter_activity_monitor_extension.json"
            ],
        ),
    ],
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "JupyterLab"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Framework :: Jupyter",
    ],
    extras_require={
        "dev": [
            "pytest >= 6",
            "pytest-cov",
            "black",
            "pytest_jupyter",
        ]
    },
)

if __name__ == "__main__":
    setup(**setup_args)
