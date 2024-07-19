# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 18:03:39 2024

@author: ThinkPad
"""

import os
dirpath=os.path.dirname(__file__)
import sys
sys.path.append(os.path.join(dirpath,'../..'))

from scient.image import dedup
from PIL import Image

if __name__=='__main__':
    ref_image='data/I10.BMP'
    images=['data/I10.BMP','data/i10_23_3.bmp','data/i10_23_4.bmp','data/i10_23_5.bmp',
            'data/i10_24_5.bmp',
            'data/i05.bmp']
    #编码
    dedup_task=dedup.Dedup()
    print(dedup_task.encode(Image.open(os.path.join(dirpath,ref_image))))
    print(dedup_task.encode_file(os.path.join(dirpath,ref_image)))
    print(dedup_task.encode_files([os.path.join(dirpath,i) for i in images]))
    print(dedup_task.encode_files([os.path.join(dirpath,i) for i in images],return_dict=False))
    dedup_task=dedup.Dedup(suffix=['.png','.bmp'])
    print(dedup_task.encode_folder(dirpath))
    dedup_task=dedup.Dedup(suffix=['.png','.bmp'],hash_hex=True)
    print(dedup_task.encode_folder(dirpath))
    
    #查重
    result=dedup_task.find_dup_from_folder('data/I10.BMP',dirpath)
    
    result=dedup_task.find_dup_in_folder(dirpath)
    
    dedup_task=dedup.Dedup(suffix=['.png','.bmp'])
    score={'data/I10.BMP':5,'data/i10_23_3.bmp':7,'data/i10_23_4.bmp':3,'data/i10_23_5.bmp':9,
            'data/i10_24_5.bmp':6,'data/i05.bmp':8}
    score={os.path.normcase(k):v for k,v in score.items()}
    result=dedup_task.find_dup_in_folder(dirpath,score)
    
    dedup_task=dedup.Dedup(threshold=5)
    result=dedup_task.find_dup_in_folder(dirpath,score)

