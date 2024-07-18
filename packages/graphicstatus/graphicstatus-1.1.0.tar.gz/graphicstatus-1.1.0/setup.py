from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
      name='graphicstatus',
      version='1.1.0',
      packages=find_packages(),  
      install_requires=[],
      author='Ruikang Sun',
      author_email='srk888666@qq.com',  # 添加作者邮箱
      description='GPUstatus is a fork of GPUtil ( https://github.com/anderskm/gputil ) ',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/RuikangSun/gpustatus',
      keywords=['gpu', 'utilization', 'load', 'memory', 'available', 'usage', 'free', 'select', 'nvidia'],
      classifiers=[
          # 添加合适的分类器，比如：
          'Topic :: System :: Hardware :: Hardware Drivers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
      ],
      license='MIT',
      python_requires='>=3.7',
)
