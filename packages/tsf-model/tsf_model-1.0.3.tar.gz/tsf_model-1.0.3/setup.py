from distutils.core import setup
from setuptools import find_packages

setup(name='tsf_model',  # 包名
      version='1.0.3',  # 版本号
      description='Common time series forecasting models',
      long_description='Designing statistical models may require modifications to the data format',
      author='Yuanjian Zhang',
      author_email='yuanjianzhang2003@163.com',
      url='https://qianyongdeyu.top/',
      install_requires=['numpy','xgboost','scikit-learn','statsmodels'],
      license='BSD License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development :: Libraries'
      ],
      )
