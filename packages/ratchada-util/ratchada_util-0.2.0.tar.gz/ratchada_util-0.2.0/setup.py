from distutils.core import setup

setup(
    name = 'ratchada_util',         
    packages = ['ratchada_processor'],   
    version = '0.2.0',      
    license='MIT',        
    description = 'A Python lib/util for Ratchada Whisper model',   
    author = 'tm-zoon',                   
    author_email = 'zoon_p@thinkingmachin.es',      
    url = 'https://github.com/tm-zoon-patcharawiwatpong/ratchada_util',     
    keywords = ['RATCAHA-WHISPER'],   
    install_requires=[            
            'regex==2023.10.3 ; python_version >= "3.10" and python_version < "3.12"',
            'more-itertools==10.1.0 ; python_version >= "3.10" and python_version < "3.12"',
        ],
    classifiers=[
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
    ],
)