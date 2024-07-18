import os
import re
import cv2
import time
import fitz

import numpy as np
import pandas as pd

import DevoteamLib
from DevoteamLib import OCRLayouting

from PIL import Image

from datetime import datetime
from pdf2image import convert_from_path

from DevoteamLib.BankStatementParser import CIMB,BCA,OCBC,BNI,BNI,BRI,Permata,Danamon,BTPN,Allo,MEGA,Artha_Graha,HANA,Mandiri


BankCIMB        = CIMB.CIMB()
BankCIMB_Credit = CIMB.CIMB_Credit()
BankBCA         = BCA.BCA()
BankOCBC        = OCBC.OCBC()
BankBNI         = BNI.BNI()
BankBRI         = BRI.BRI()
BankPermata     = Permata.Permata()
BankDanamon     = Danamon.Danamon()
BankBTPN        = BTPN.BTPN()
BankAllo        = Allo.Allo()
BankMEGA        = MEGA.MEGA()
BankArtha       = Artha_Graha.Artha_Graha()
BankHANA        = HANA.HANA()
BankMandiri     = Mandiri.Mandiri()

def extract(BankType,df):
    if BankType == 'CIMB':
      return BankCIMB.extract(df)

    elif BankType == 'BCA':
      return BankBCA.extract(df)

    elif BankType == 'BNI':
      return BankBNI.extract(df)

    elif BankType == 'BRI':
      return BankBRI.extract(df)

    elif BankType == 'OCBC':
      return BankOCBC.extract(df)

    elif BankType == 'Permata':
      return BankPermata.extract(df)

    elif BankType == 'Danamon':
      return BankDanamon.extract(df)

    elif BankType == 'BTPN':
      return BankBTPN.extract(df)

    elif BankType == 'Allo':
      return BankAllo.extract(df)

    elif BankType == 'MEGA':
      return BankMEGA.extract(df)

    elif BankType == 'Artha_Graha':
      return BankArtha.extract(df)

    elif BankType == 'HANA':
      return BankHANA.extract(df)

    elif BankType == 'CIMB_Credit':
      return BankCIMB_Credit.extract(df)

    elif BankType == 'Mandiri':
      return BankMandiri.extract(df)
    
def detailExtraction(index,result_text,regexDetail,bankName):
  if DevoteamLib.BankStatementStatus('detailExtraction'):
    dataIndexer =0
    if bankName == 'BCA':
      dataIndexer = [indexer.start() for indexer in re.finditer('\d\d\/\d\d', result_text[-1])][0]
    elif bankName == 'CIMB':
      dataIndexer = [indexer.start() for indexer in re.finditer('\d{4}-\d\d-\d\d', result_text[-1])][0]

    textData = result_text[-1][dataIndexer:]
    dataTake = re.findall(regexDetail[index],textData)
    try:
      save_data = dataTake[0][0]
    except:
      if index < len(regexDetail)-1:
        return detailExtraction(index+1,result_text,regexDetail,bankName)
      else:
        return result_text

    result_text[-1] = [result_text[-1].replace(save_data,''),save_data]
    result_text[-1] = [rt.replace('\n',' ') for rt in result_text[-1]]
    return result_text
  else:
      return "You not allowed to used this function"

def bankExtraction(path_file,filter_trash,sufix_filter,extract_table,extract_detail,bankName,additional_page_split = [0,0],check = True):
  if DevoteamLib.BankStatementStatus('detailExtraction'):
    print("Process",path_file)
    start = time.time()
    images = convert_from_path(path_file)

    prefix                 = ''
    sufix                  = ''
    result_text            = []
    datatext_save_check    = {
        "page":[],
        "text":[]
    }

    for index,img in enumerate(images[additional_page_split[0]:len(images)+additional_page_split[1]]):
      print(f"Halaman {index}")
      data_img = np.asarray(img)
      angle, corrected    = OCRLayouting.correct_skew(data_img)
      img                 = Image.fromarray(corrected)

      width, height       = img.size
      newsize             = (width*2, height*2)
      img                 = img.resize(newsize)

      if bankName == 'BRI':
        img               = np.asarray(img)
        gray              = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh            = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        img               = Image.fromarray(thresh)

      img.save('image_save.jpeg',quality=100)
      df_x_result         = OCRLayouting.horizontal_read('image_save.jpeg')

      print("Coba cek aku disini",df_x_result)

      if bankName == 'BTPN':
        width *= 2
        width = width*3.2/4

      elif bankName == 'Allo':
        width *= 2
        width = width*6/8

      elif bankName == 'Artha_Graha':
        width *= 2
        width = width*5/8

      elif bankName == 'HANA':
        width *= 2
        width = width*6/10

      elif bankName == 'Danamon':
        width *= 2
        width = width*7/10

      elif bankName == 'CIMB_Credit':
        width *= 2
        width = width*2/3

      data_regex        = ''
      for df_x in df_x_result:
        if bankName in ['BTPN', 'Allo', 'Artha_Graha', 'HANA', 'Danamon', 'CIMB_Credit']:
          df_x['x_pos'] = df_x['x_pos'].apply(lambda x:x[0])
          data          = df_x[df_x['x_pos']>width]
          other         = df_x[df_x['x_pos']<=width]

          data['text']  = data['text'].apply(lambda x :x+'_CREDIT' if re.search("[0-9]+", x) else x)
          df_x          = pd.concat([other,data])

        df_x = df_x.sort_values(by=['x_pos']).reset_index(drop=True)
        data_regex += ' '.join(df_x.text.values.tolist()).replace(' , ',',').replace(' . ','.').replace(' / ','/')+'\n'

      data_regex = data_regex.upper()

      datatext_save_check['page'].append(index)
      datatext_save_check['text'].append(data_regex)
      
      data_regex = re.sub(r"(\d\d)\.(\d\.\d\d)", r"\1.00 \2", data_regex)

      if prefix != '':
          data_regex = data_regex.replace(prefix,'')

      data_regex   = re.sub(filter_trash,'', data_regex)
      data_regex   = data_regex.replace('⁰','')

      if check:
        print(data_regex)

      if sufix_filter != '':
        try:
            sufix_start  = re.findall(sufix_filter,data_regex)[0]
            sufix        = data_regex[data_regex.index(sufix_start):]
            data_regex   = data_regex.replace(sufix,'')
        except:
          pass

      r1 = []
      for x in data_regex.split('\n'):
        x_re = re.findall(extract_table,x)
        if len(x_re)!=0:
          if 'tuple' in str(type(x_re[0])):
            print(x_re[0][0])
            r1.append(x_re[0][0])
          else:
            print(x_re[0])
            r1.append(x_re[0])

      print(r1)
      r1_position  = []
      print('Halaman '+str(index+1)+' '+str(len(r1)))
      for r in r1:
        try:
          r=r.replace('\\','\\\\')
          r=r.replace('+','\\+')
          r=r.replace('$','\\$')
          r=r.replace('(','\\(')
          r=r.replace(')','\\)')
          r=r.replace('|','\\|')
        except:
          pass

        try:
            dataIndexer = [indexer.start() for indexer in re.finditer(r, data_regex)]
            # print(r)
            r1_position += dataIndexer
        except:
            print("Error Di",r)

      r1_position.sort()
      r1_position = list(dict.fromkeys(r1_position))
      print('Halaman '+str(index+1)+' '+str(len(r1_position)))

      for i in range(len(r1_position)):
        try:
          result_text.append(data_regex[r1_position[i]:r1_position[i+1]])
        except:
          result_text.append(data_regex[r1_position[i]:])

        if check:
          print("==================================")
          print("Hasil Ekstraksi Pertama : ",result_text[-1])
        result_text = detailExtraction(0,result_text,extract_detail,bankName)

        print("Hasil Ekstraksi Kedua : ",result_text[-1])
        print("==================================")

      if check:
        print("==================================")

      if prefix == '':
        prefix       = data_regex[:r1_position[0]]

    end = time.time()
    print("Done",(end-start), "s")

    return prefix,result_text,sufix  
  else:
    return "You not allowed to used this function"
  
def BatchBSExtraction(FolderPath,bankName,filter_trash,sufix_filter,extract_table,extract_detail):
  if DevoteamLib.BankStatementStatus('BatchBSExtraction'):
    data_extract = {
        "prefix":[],
        "transaction":[],
        "sufix":[]
    }

    additional_page_split = [0,0]

    if bankName == 'OSBC':
      additional_page_split = [0,-2]

    if bankName == 'CIMB_Credit':
      additional_page_split = [0,-1]

    for data_file in os.listdir(FolderPath):
        if 'pdf' in data_file:
            extraction_result = bankExtraction(FolderPath+'/'+data_file,filter_trash = filter_trash,sufix_filter = sufix_filter,extract_table = extract_table,extract_detail = extract_detail,bankName=bankName,additional_page_split=additional_page_split)
            data_extract["prefix"].append(extraction_result[0])
            data_extract["sufix"].append(extraction_result[2])
            # data_extract["transaction"].append(BankParser.extract(bankName,extraction_result))
            data_extract["transaction"].append(extract(bankName,extraction_result))

    data_extract                    = pd.DataFrame.from_dict(data_extract)
    Transaction_data                = pd.concat(data_extract["transaction"].values.tolist()).reset_index(drop=True).sort_values(by=['TANGGAL'])
    return Transaction_data,data_extract
  else:
    return "You not allowed to used this function"
  
def DateNormalisation(x):
  if 'str' in str(type(x)):
    return datetime.strptime(x, '%Y-%m-%d')
  else:
    return x
  
def BSBalencing(Transaction_data,bankName):
  if DevoteamLib.BankStatementStatus('BSBalencing'):
    Transaction_data['TANGGAL']     = Transaction_data['TANGGAL'].apply(lambda x:datetime.strptime(x, '%Y-%m-%d'))
    Transaction_data                = Transaction_data.sort_values(by=['TANGGAL', 'INDEX'],ascending=[True,False])
    dataFor_Extract                 = Transaction_data[['TANGGAL','INDEX']].groupby('TANGGAL')['INDEX'].min().copy()

    Transaction_data['TANGGAL']     = Transaction_data['TANGGAL'].apply(DateNormalisation)
    
    if bankName in ['CIMB','CIMB NIAGA']:
      Transaction_data                = Transaction_data.sort_values(by=['TANGGAL', 'INDEX'],ascending=[True,False])
    else:
      Transaction_data                = Transaction_data.sort_values(by=['TANGGAL', 'INDEX'],ascending=[True,True])
    
    dataFor_Extract                   = Transaction_data[['TANGGAL','INDEX']].groupby('TANGGAL')['INDEX'].min().copy()

    Transaction_data2 = None
    DiffDate              = []
    print(len(dataFor_Extract))
    for i in range(len(dataFor_Extract)):
        Transaction_data2 = pd.concat([Transaction_data2,Transaction_data.loc[(Transaction_data['TANGGAL'] == dataFor_Extract.index[i]) & (Transaction_data['INDEX'] == dataFor_Extract[i])]])
        print(Transaction_data.loc[(Transaction_data['TANGGAL'] == dataFor_Extract.index[i]) & (Transaction_data['INDEX'] == dataFor_Extract[i])])
        print("========================")
        try:
            DiffDate.append((dataFor_Extract.index[i+1]-dataFor_Extract.index[i]).days)
        except:
            DiffDate.append(1)

    Transaction_data2 = Transaction_data2.drop_duplicates()

    print(len(Transaction_data2))
    print(len(DiffDate))

    Transaction_data2["DIFF_DATE"] = np.array(DiffDate)
    Transaction_data2['BALENCE']   = Transaction_data2['SALDO']*Transaction_data2['DIFF_DATE']

    return Transaction_data2
  else:
    return "You not allowed to used this function"
  
def BalenceCalculation(df,df2):
  if DevoteamLib.BankStatementStatus('BalenceCalculation'):  
    df_result = {
      "Bulan Tahun":[],
      "Jumlah Debit":[],
      "Total Debit":[],
      "Jumlah Credit":[],
      "Total Credit":[],
      "Transaksi Maksimum":[],
      "Transaksi Minimum":[],
      "Transaksi Rata-rata":[],
    }
    for BT in df["BULAN_TAHUN"].unique():
        df_result['Bulan Tahun'].append(BT)
        df_result['Jumlah Debit'].append(df2[(df2["BULAN_TAHUN"] == BT) & (df2["STATUS"] == 'DEBIT')]['INDEX'].count())
        df_result['Total Debit'].append(df2[(df2["BULAN_TAHUN"] == BT) & (df2["STATUS"] == 'DEBIT')]['AMMOUNT'].sum())
        df_result['Jumlah Credit'].append(df2[(df2["BULAN_TAHUN"] == BT) & (df2["STATUS"] == 'CREDIT')]['INDEX'].count())
        df_result['Total Credit'].append(df2[(df2["BULAN_TAHUN"] == BT) & (df2["STATUS"] == 'CREDIT')]['AMMOUNT'].sum())
        df_result['Transaksi Maksimum'].append(df[(df["BULAN_TAHUN"] == BT)]['BALENCE'].max())
        df_result['Transaksi Minimum'].append(df[(df["BULAN_TAHUN"] == BT)]['BALENCE'].min())
        df_result['Transaksi Rata-rata'].append(df[(df["BULAN_TAHUN"] == BT)]['BALENCE'].mean())

    return pd.DataFrame.from_dict(df_result)
  else:
    return "You not allowed to used this function"
  
def BSExtraction(FolderPath,bankName):
  if DevoteamLib.BankStatementStatus('BSExtraction'):
    filter_trash   = None
    sufix_filter   = None
    extract_table  = None
    extract_detail = None

    #Import Set Up CIMB Parser
    if bankName == "CIMB_Credit":
        filter_trash              = 'TERIMA\s+KASIH\s+ATAS'
        sufix_filter              = ''
        extract_table             = "((\d\d\/\d\d)\s+(\d\d\/\d\d).*([\-\+]*\d{1,3}([\.,]\d{3})*([\.,]\d{2}(_CRE\DIT)*)){2})"
        extract_detail            = ["(([\-\+\s]*\d{1,3}([\.,]\d{3})*([\.,]\d{2}(_CRE\DIT)*)){2})"]

    elif bankName == 'CIMB':
        filter_trash              = 'PT Bank CIMB Niaga Tbk is registered and under supervision of Financial Services Authority ( OJK ).OCTO Clicks Copyright © 2020. All rights reserved .'
        sufix_filter              = 'Begining\s+Balance'
        extract_table             = "\d\d\d\d-\d\d-\d\d.*?.+"
        extract_detail            = ["((-|\+)*[\s,\d]+\.\d\d[\s,\d]+\.\d\d)"]

    #Import Set Up BCA Parser
    elif bankName == 'BCA':
        filter_trash              = 'Bersambung ke Halaman berikut'
        sufix_filter              = '\\nSALDO\s+AWAL'
        extract_table             = "^.{0,2}\d\d\/\d\d.*[BV(\d\d)]"
        extract_detail            = ['((\s+\d{4}\s+(\d{0,3}(,\d{3})*?[,\.]\d\d.{0,4})\s+(\d{0,3}(,\d{3})*[,\.]\d\d).{0,4}))',
                                    '((\s+\d{4}\s+(\d{0,3}(,\d{3})*[,\.]\d\d.{0,4})))',
                                    '(((\s+\d{0,3}(,\d{3})*[,\.]\d\d).{0,4})((\d{0,3}(,\d{3})*[,\.]\d\d).{0,4}))',
                                    '(((\s+\d{0,3}(,\d{3})*[,\.]\d\d).{0,4}))']

    #Import Set Up BNI Parser
    elif bankName == 'BNI':
        filter_trash              = ''
        sufix_filter              = ''
        extract_table             = "\d+\s+\d{2}\/\d{2}\/\d{4}.*\d{0,3}.*?.\d\d$"
        extract_detail            = ["(\d{1,3}([\.,]\d{3})+(\.\d\d)[\sC\D]+\d{1,3}([\.,]\d{3})+(\.\d\d))"]

    #Import Set Up Artha_Graha Parser
    elif bankName == 'Artha_Graha':
        filter_trash              = '((PIN\DAH\s+KE\s+HALAMAN\s+BERIKUTNYA)|(TOTAL\s+AKHIR)).*'
        sufix_filter              = 'ACCOUNT\s+STATEMENT.*'
        extract_table             = "(\d\d\/\d\d\/\d{4}.*?(.+(\d{1,3})([\.,]\d{3})*([\.,]\d\d)){2}(_CRE\DIT)*)"
        extract_detail            = ["(((\d{1,3})([\.,]\d{3})*([\.,]\d\d)){2}(_CRE\DIT)*.+)"]

    #Import Set Up MEGA Parser
    elif bankName == 'MEGA':
        filter_trash              = ''
        sufix_filter              = 'SALDO\s+AWAL.*'
        extract_table             = "(\d{1,2}\/\d{1,2}\/\d{2}\s\d{1,2}:\d{1,2}\s(?:AM|PM).*\.\d{2})"
        extract_detail            = ["((\s+(\d{1,3})([\.,]\d{3})*([\.,]\d\d)){3})"]

    #Import Set Up Allo Parser
    elif bankName == 'Allo':
        filter_trash              = ''
        sufix_filter              = 'BALANCE\s+AT\s+PERIO\D\s+EN\D\s+'
        extract_table             = "(\d{1,2}\s+-\s+[A-Z]{3}\s+-\s+\d\d.*?(\s+\d{1,3}([\.,]*\d{3})*([\.,]\d\d)(_CRE\DIT)*){2})"
        extract_detail            = ["((\s+\d{1,3}([\.,]*\d{3})*([\.,]\d\d)(_CRE\DIT)*){2})"]

    #Import Set Up BTPN Parser
    elif bankName == 'BTPN':
        filter_trash              = ''
        sufix_filter              = 'INFORMATION\nACCOUNT.*'
        extract_table             = "(\d{2}\/\d{2}\/\d{4}\s+.*?\.\d{2}('CRE\DIT')*)"
        extract_detail            = ["((I\DR\s+.*\.\d{2}(_CRE\DIT)*))"]

    #Import Set Up Danamon Parser
    elif bankName == 'Danamon':
        filter_trash              = ''
        sufix_filter              = 'TOTAL\s+\d*\.(?:\d{1,3}.)*,\d{2}.*'
        extract_table             = "(\d{2}\/\d{2}\s+.*(?:\d{1,3}\.)*,\d{2}(_CRE\DIT)*)"
        extract_detail            = ["((\s+(\d{1,3})([\.,]\d{3})*([\.,]\d\d)(_CRE\DIT)*){2})"]

    #Import Set Up HANA Parser
    elif bankName == 'HANA':
        filter_trash              = ''
        sufix_filter              = '\nSTARTING\s+BALANCE.*'
        extract_table             = "(\d{2}\/\d{2}\/\d{4}\s+.*?(US\D\s+\d{1,3}([\.,]\d{3})*([\.,]\d\d)*(_CRE\DIT)*\s*){2})"
        extract_detail            = ["((US\D\s+\d{1,3}([\.,]\d{3})*([\.,]\d\d)*(_CRE\DIT)*\s*){2})"]

    #Import Set Up Permata Parser
    elif bankName == 'Permata':
        filter_trash              = ''
        sufix_filter              = ''
        extract_table             = "((SALDO|\d{4}).*?(\s+(\d{1,3})([\.,]\d{3})*([\.,]\d\d)){1,2})"
        extract_detail            = ["(((\s*(\d{1,3})([\.,]\d{3})*([\.,]\d\d)){1,2}))"]

    #Import Set Up OCBC Parser
    elif bankName == 'OCBC':
        filter_trash              = 'BILAMANA \DALAM 7 HARI.*'
        sufix_filter              = 'MATA\S+UANG/SALDO\S+MINIMUM/SALDO.*'
        extract_table             = "((\d{1,2}\/\d{1,2}\/\d\d\s*){2}.*?(\s*\d{1,3}([\.,]\d{3})*([\.,]\d{2})){3})"
        extract_detail            = ["((\s+\d{1,3}([\.,]\d{2,3})*){3})"]

    #Import Set Up BRI Parser
    elif bankName == 'BRI':
        filter_trash              = '\d+\s+\DARI\s+\d+'
        sufix_filter              = 'OPENING.*'
        extract_table             = "(\d\d\/\d\d\/\d\d\s.*?([\s]*\d{1,3}([\.,]\d{3})*([\.,]\d{2})))"
        extract_detail            = ["(([\s]*\d{1,3}([\.,]\d{3})*([\.,]\d{2})){3})"]

    elif bankName == 'Mandiri':
        filter_trash              = ''
        sufix_filter              = ''
        extract_table             = "(\d\d\/\d\d\/\d{4})"
        extract_detail            = ["(([\s]*\d{1,3}([\.,]\d{3})*([\.,]\d{2})){3})"]

    #Run The Extraction
    return BatchBSExtraction(FolderPath,bankName,filter_trash,sufix_filter,extract_table,extract_detail)
  
  else:
    return "You not allowed to used this function"