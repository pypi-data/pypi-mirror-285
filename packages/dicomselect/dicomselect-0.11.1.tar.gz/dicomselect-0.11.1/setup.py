import setuptools

version = '0.11.1'

if __name__ == '__main__':
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

    setuptools.setup(
        name='dicomselect',
        version=version,
        author_email='Stan.Noordman@radboudumc.nl',
        long_description=long_description,
        long_description_content_type="text/markdown",
        url='https://diagnijmegen.github.io/dicomselect/',
        project_urls={
            "GitHub": "https://github.com/DIAGNijmegen/dicomselect"
        },
        license='MIT License',
        install_requires=[
            'pydicom~=2.3',
            'SimpleITK~=2.3',
            'tqdm~=4.65',
            'pandas~=2.0',
            'pylibjpeg~=2.0',
            'pylibjpeg-libjpeg~=2.2',
            'rapidfuzz~=3.0',
            'python-Levenshtein~=0.21',
            'treelib~=1.6'
        ],
        extras_require={
            'dev': [
                'pytest',
                'flake8',
                'sphinx'
            ]
        },
    )
