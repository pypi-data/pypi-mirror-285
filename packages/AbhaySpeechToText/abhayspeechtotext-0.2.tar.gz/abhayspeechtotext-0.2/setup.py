from setuptools import setup,find_packages
setup(
    name='AbhaySpeechToText',
    version='0.2',
    author='Abhay Agnihotri',
    author_email='abhayagnihotri976@gmail.com',
    description='This is the awesome speech to text package created by Me(Abhay Agnihori)'

)
packages=find_packages(),
install_requirements=[
    'selenium',
    'webdriver-manager'
]