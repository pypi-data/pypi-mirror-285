# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 20:36:58 2017

@author: a
"""
# python setup.py sdist build --compiler=mingw32 bdist_wheel
package='scient'#包名,需与文件夹名一致
version='0.6.0'
#cythons 需要编译或已编译为.c的.py文件，需明确列出不包含后缀的文件名，否则打包wheel时无法定位ext_modules
#cythons=['elect/test']
cythons=[
"scient/calc_expr", "scient/process", "scient/service",

"scient/algorithm/binning","scient/algorithm/bktree",
"scient/algorithm/correlate","scient/algorithm/distance",
"scient/algorithm/entropy","scient/algorithm/gene","scient/algorithm/kdtree",
"scient/algorithm/linear_regression","scient/algorithm/metric","scient/algorithm/pca",
"scient/algorithm/similar","scient/algorithm/trie","scient/algorithm/weight",

"scient/associate/apriori","scient/associate/rule_merge","scient/associate/sbar",

"scient/cluster/bestkmeans","scient/cluster/fourstep","scient/cluster/seqsim",

"scient/graph/louvain",

"scient/image/edge","scient/image/dedup","scient/image/feature","scient/image/friqa",
"scient/image/hash","scient/image/kernel","scient/image/process",
"scient/image/threshold",

"scient/language/cut","scient/language/document","scient/language/entity",
"scient/language/hash","scient/language/keyword","scient/language/longest_common",
"scient/language/process","scient/language/tagging","scient/language/tokenize",
"scient/language/topic","scient/language/vocab",

"scient/neuralnet/utils","scient/neuralnet/activate","scient/neuralnet/attention",
"scient/neuralnet/bert","scient/neuralnet/crf","scient/neuralnet/dataset",
"scient/neuralnet/dropout","scient/neuralnet/embedding",
"scient/neuralnet/esim","scient/neuralnet/function",
"scient/neuralnet/glove","scient/neuralnet/hypernet","scient/neuralnet/lora",
"scient/neuralnet/loss","scient/neuralnet/lstm","scient/neuralnet/lstm_crf",
"scient/neuralnet/mask_linear","scient/neuralnet/optimize","scient/neuralnet/prepare",
"scient/neuralnet/resnet","scient/neuralnet/skip_gram","scient/neuralnet/fit",
"scient/neuralnet/transformer",

"scient/timeseries/filter","scient/timeseries/outlier","scient/timeseries/segment"
    ]
#include 需要复制tar.gz包中的资源文件或文件夹，必须是tar.gz中包含的资源
#include=['elect/data','elect/pkgs/jieba/analyse/idf.txt','elect/pkgs']
include=['scient/data','scient/test']
#exclude 需要排除的文件或文件夹，
# import os
#exclude=['elect/apps','elect/guard.py','elect/data/brand.json','elect/pkgs']+sum([[os.path.join(dirpath,f) for f in filenames if f.startswith('__') and f.endswith('.py') and f not in ['__init__.py']] for dirpath,_,filenames in os.walk(package)],[])
exclude=[]
#include和exclude同时存在的内容，会exclude

#setup
keywords = ('science compute','image','natural language','machine learning','neural network','optimize algorithm','graphic algorithm')
description = "A python package about science compute algorithm, include natural language, image, neural network, optimize algorithm, machine learning, graphic algorithm, etc."
long_description = ""#如果有README.md，该项会被README.md内容覆盖
author = "scient"
author_email = "yaomsn@live.cn"
platforms = "any"
python_requires=">=3.10"
install_requires = ['numpy>=1.24.0,<2.0.0', 'scipy>=1.12.0','pillow','tqdm']#,'torch>=2.2.0']
#%%以下内容不可修改
import os,io,shutil
from setuptools import setup

#切换到文件所在目录
# os.chdir(os.path.dirname(__file__))

#路径分隔符统一
include=[i.replace('\\','/') for i in include]
exclude=[i.replace('\\','/') for i in exclude]
cythons=[i.replace('\\','/') for i in cythons]

#README.md
if os.path.exists('README.md'):
    with io.open('README.md',encoding='utf-8') as f:
        long_description = f.read()

#生成MANIFEST.in
with open('MANIFEST.in','w') as f:
    for i in include:
        if os.path.isdir(i):
            f.write('recursive-include %s *\n'%i)
        if os.path.isfile(i):
            f.write('include %s\n'%i)
    for i in exclude:
        if os.path.isdir(i):
            f.write('recursive-exclude %s *\n'%i)
        if os.path.isfile(i):
            f.write('exclude %s\n'%i)

import re
from Cython.Build import cythonize
from setuptools import Extension
ext_modules=[]
for i in cythons:
    #如果.py存在.重新编译成.c
    if os.path.exists(i+'.py'):
        #如果.c存在，先删
        if os.path.exists(i+'.c'):
            os.remove(i+'.c')
        #将build_py编译为.c
        ext_modules+=cythonize(i+'.py')
        #clear comment
        expr=re.compile(r'/\*.*?\*/',re.S)
        with open(i+'.c') as f:
            text=f.read()
            text=re.sub(expr,'',text)
        with open(i+'.c','w') as f:
            f.write(text)
    else:
        ext_modules.append(Extension(i.replace('/','.'),sources=[i+'.c']))

#py_modules排除exclude文件夹、include文件夹
py_modules=[(dirpath,[i for i in dirnames if os.path.join(dirpath,i).replace('\\','/') not in exclude
                     and os.path.join(dirpath,i).replace('\\','/') not in include],filenames)
           for dirpath, dirnames, filenames in os.walk(package) if dirpath.replace('\\','/') not in exclude
           and dirpath.replace('\\','/') not in include]
#py_modules所有py文件
py_modules=sum([[os.path.join(dirpath,i).replace('\\','/') for i in filenames if i.endswith('.py')]
               for dirpath, _, filenames in py_modules],[])
#py_modules排除exclude文件、include文件、cythons文件
py_modules=[i for i in py_modules if i not in exclude+include and i.replace('.py','') not in cythons]

setup(
    name = package,
    version = version,
    keywords = keywords,
    description = description,  
    long_description = long_description,
    long_description_content_type="text/markdown",
    author = author,
    author_email = author_email,
    platforms = platforms,
    python_requires=python_requires,
    install_requires = install_requires,
    #打包范围
    py_modules=[i.replace('.py','') for i in py_modules],
    ext_modules=ext_modules,
    #没有packages、include_package_data，不影响打包tar.gz，但是打包whl会缺少include
    packages=[i.replace('/','.') for i in include if os.path.isdir(i)],
    include_package_data = True,
    )

#删除MANIFEST.in、.egg-info
os.remove('MANIFEST.in')
shutil.rmtree(package+'.egg-info')
if os.path.exists('build'):
    shutil.rmtree('build')

