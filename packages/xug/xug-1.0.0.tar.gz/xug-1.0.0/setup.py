from setuptools import setup, find_packages

setup(
    name='xug',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'pywin32',
        'cryptography',
        'requests',
        'tqdm',
        'pyautogui',
        'numpy',
        'opencv-python',
        'openpyxl',
        'pandas'
    ],
)
