#Prompt.py
from colored import Fore,Style,Back
import random
import re,os,sys
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.Prompt import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.DatePicker import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes import VERSION
import inspect,string
import json
from pathlib import Path
from datetime import date,time,datetime
fm_data={'Name':{
            'type':'str',
            'default':'',
            },
        'Value':{
            'type':'int',
            'default':0,
            },
        'Price':{
           'type':'float',
           'default':0.0,
            },
        'Barcode':{
            'type':'str',
            'default':'000000000000',
            },
        'Code':{
            'type':'str',
            'default':'12345678',
            },
        'DOE':{
            'type':'date',
            'default':None,
            },
        'TOE':{
            'type':'time',
            'default':None,
            },
        'DTOE':{
            'type':'datetime',
            'default':None,
            },
        'DEFAULT':{
            'type':'bool',
            'default':False,
            },
        'List':{
            'type':'list',
            'default':[],
            },
      }
def FormBuilderMkText(text,data):
    try:
        if text in ['f','m','p','d']:
            return text
        if text == '':
            return 'd'
        value=None
        if data.lower() == 'float':
            try:
                value=float(eval(text))
            except Exception as e:
                try:
                    value=float(text)
                except Exception as e:
                    return 'd'
        elif data.lower() in ['int','integer']:
            try:
                value=int(eval(text))
            except Exception as e:
                try:
                    value=int(text)
                except Exception as e:
                    return 'd'
        elif data.lower() in ['bool','boolean']:
            try:
                value=bool(eval(text))
            except Exception as e:
                try:
                    if text.lower() in ['y','yes','true','t','1']:
                        value=True
                    elif text.lower() in ['n','no','false','f','0']:
                        value=False
                    else:
                        try:
                            value=bool(eval(text))
                        except Exception as e:
                            return 'd'
                except Exception as e:
                    return 'd'
        elif data.lower() in ['str','string',"varchar"]:
            value=text
        elif data.lower() == 'date':
            if text.lower() in ['y','yes','1','t','true']:
                value=DatePkr()
        elif data.lower() == 'time':
            if text.lower() in ['y','yes','1','t','true']:
                value=TimePkr()
        elif data.lower() == 'datetime':
            if text.lower() in ['y','yes','1','t','true']:
                value=DateTimePkr()
        elif data.lower() == 'list':
            splitBy=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Split the String by?",helpText="what character to use to make a list default=,",data="str")
            if splitBy in [None,]:
                value=[]
            elif splitBy == 'd':
                value=text.split(",")
            else:
                value=text.split(splitBy)
        return value
    except Exception as e:
        print(e)
        

def FormBuilder(data):
    index=None
    item={}
    for num,k in enumerate(data.keys()):
        item[k]=data[k]['default']
    review=False
    finalize=False
    while True:
        if finalize:
            break
        while True:
            if finalize:
                break
            for num,k in enumerate(data.keys()):
                if isinstance(index,int):
                    if num < index:
                        continue
                    else:
                        index=None
                ht=''
                if data[k]['type'].lower() in ['date','datetime','time']:
                    ht="type 'y' or 'n' to start"
                elif data[k]['type'].lower() in ['list']:
                    ht="type your $DELIMITED list, the you will be asked for $DELIMITED character to use!"
                elif data[k]['type'].lower() in ['bool','boolean']:
                    ht="type y|yes|t|true|1 for yes/True, and n|no|0|false|f for no/False"

                cmd=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"You(m):{item.get(k)}|Default(d):{data[k]['default']} Field:{str(k)}",helpText=f'{ht}',data=data[k]['type'])
                if cmd in [None,]:
                    return
                elif isinstance(cmd,str):
                    if cmd.lower() in ['p',]:
                        if num == 0:
                            index=len(data.keys())-1
                        else:
                            index=num-1
                        break
                    elif cmd.lower() in ['d',]:
                        item[k]=data[k]['default']
                    elif cmd.lower() in ['f','finalize']:
                        finalize=True
                        break
                    elif cmd.lower() in ['m',]:
                        print(f"Not changing User set value '{k}':'{item.get(k)}'")
                        pass
                    else:
                        item[k]=cmd
                else:
                    item[k]=cmd
        review=Prompt.__init2__(None,func=FormBuilderMkText,ptext="review?",helpText="",data="bool")
        #print(review)
        if review in [None,]:
            return 
        elif review in [True,'d']:
            finalize=False
            continue
        else:
            break
    return item            

'''
form=FormBuilder(data=fm_data)
print(form)
'''