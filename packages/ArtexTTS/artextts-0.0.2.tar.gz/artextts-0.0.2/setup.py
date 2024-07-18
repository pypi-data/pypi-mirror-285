from setuptools import setup, find_packages

setup(
    name='ArtexTTS',
    version='0.0.2',
    author='Artex AI',
    description='A python text to speech library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/JunaidParkar/Python-TTS',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'selenium==4.22.0',
        'webdriver_manager==4.0.1',
        'mtranslate==1.8',
        'pathlib==1.0.1'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Boost Software License 1.0 (BSL-1.0)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    project_urls={
        'Documentation': 'https://github.com/JunaidParkar/Python-TTS',
        'Source': 'https://github.com/JunaidParkar/Python-TTS',
        'Tracker': 'https://github.com/JunaidParkar/Python-TTS',
    },
)
