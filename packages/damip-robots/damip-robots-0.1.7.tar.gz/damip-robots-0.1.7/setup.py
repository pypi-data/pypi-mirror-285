from setuptools import setup, find_packages

setup(
    name='damip-robots',
    version='0.1.7',
    author='kaiwei.li',
    author_email='kaiwei.li@digitopia.com.cn',
    description='Robots SDK for Digitopia Advanced Mechanical Intelligence Platform.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://digitopia.com.cn/damip-robots',
    packages=find_packages(),
    install_requires=[
        'pyserial',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        "Topic :: Software Development :: Build Tools",
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
)

