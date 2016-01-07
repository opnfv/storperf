from setuptools import setup, find_packages


setup(
    name="storperf",
    version="0.dev0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'storperf': [
            'storperf/resources/hot/*'
        ]
    },
    url="https://www.opnfv.org",
    install_requires=["coverage>=4.0.3",
                      "flake8>=2.5.1",
                      "flask>=0.10.1",
                      "flask-restful>=0.3.5",
                      "mock>=1.3",
                      "pyyaml>=3.11",
                      "python-cinderclient>=1.5.0",
                      "python-heatclient>=0.8.0",
                      "python-keystoneclient>=2.0.0",
                      "python-novaclient>=3.1.0",
                      "six==1.10.0"
                      ],
    entry_points={
        'console_scripts': [
            'storperf=storperf.main:main',
        ],
    }
)
