import setuptools

setuptools.setup(
    name='gru',
    version='0.0.1',
    install_requires=['requests>=2.31.0', 'typing==3.7.4.3','chardet==5.1.0','click>=8.1.7'],
    entry_points={
        'console_scripts': [
            'yugenml = gru.cookiecutter.mlops_templates_cli:mlops_template_cli',
            'yserve = gru.ml_serving.server:serve'
        ],
    },
    packages=setuptools.find_packages(),
    )