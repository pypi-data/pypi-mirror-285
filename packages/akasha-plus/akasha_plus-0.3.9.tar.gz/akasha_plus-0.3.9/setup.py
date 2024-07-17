import setuptools
from pathlib import Path
# Read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

requirements = ['akasha-terminal==0.8.47',
                'numpy~=1.24.4',
                'sentencepiece~=0.1.98',
                'transformers>=4.35.2,<5.0.0',
                'gguf>=0.1.0',
                'protobuf>=4.21.0,<5.0.0',
                'torch~=2.0.1',
                'einops~=0.7.0',
                'click',        
                'auto_gptq>=0.3.1', # 'auto_gptq>=0.5.0',
                'psycopg2==2.9.9',
                'pandas==2.2.2',
                'pymssql==2.3.0',
                'mysql-connector-python==9.0.0']
setuptools.setup(
    name='akasha-plus',
    version='0.3.9',
    description='Extension tools for akasha-terminal',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='shihiyang',
    author_email='shihiyang@iii.org.tw',
    packages=['akasha_plus', 
              'akasha_plus.agents'
              ], # setuptools.find_packages(),
    # scripts=['akasha/quantize_linux', 'akasha/quantize_win.exe'],
    package_data={'akasha_plus': ['*']},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'akasha-plus = akasha_plus.cli:main',
        ]
    },
    python_requires=">=3.8",
)