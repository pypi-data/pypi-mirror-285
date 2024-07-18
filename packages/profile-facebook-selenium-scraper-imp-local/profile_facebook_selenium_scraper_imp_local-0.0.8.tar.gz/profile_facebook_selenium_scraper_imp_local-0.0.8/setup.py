import setuptools

PACKAGE_NAME = "profile-facebook-selenium-scraper-imp-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.8',  # https://pypi.org/project/profile-facebook-selenium-scraper-imp-local/
    author="Circles",
    author_email="info@circlez.ai",
    description=f"PyPI Package for Circles {PACKAGE_NAME} Python",
    long_description=f"PyPI Package for Circles {PACKAGE_NAME} Python",
    long_description_content_type='text/markdown',
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'selenium>=4.20.0',
        'logger-local>=0.0.135',
        'profile-local>=0.0.65',
        'language-remote>=0.0.20',
        'python-sdk-remote>=0.0.75',
    ],
)
