from dotenv import load_dotenv
import snowflake.connector
import os
from multiprocessing import Process
import webbrowser
from random import randint
import boto3
from bs4 import BeautifulSoup
import re
from multiprocessing import Pool
import pandas as pd
from glob import glob

load_dotenv(dotenv_path='creds.env')



def snowflake_connector():
    username = os.getenv('username')
    password = os.getenv('password')

    ctx = snowflake.connector.connect(
        user=username,
        password=password,
        account='infoscout',
        database='infoscout',
        authenticator='externalbrowser'
    )

    cs = ctx.cursor()
    return cs


class DisplayReceipts:
    def __init__(self, receipt_type, banner_key, keywords, views, limit):
        self.type = receipt_type
        self.banner_key = banner_key
        self.keywords = keywords
        self.views = views
        self.limit = limit
        self.receipt_type()

    def receipt_type(self):
        if self.type == 'paper':
            self.view_paper()
        else:
            self.view_ereceipt()

    def view_paper(self):
        if glob('Receipt_csv/' + self.banner_key + '_*'):
            for keyword in self.keywords:
                print(f"Viewing receipts for {keyword}")
                df = pd.read_csv('Receipt_csv/' + self.banner_key + '_' + keyword + '.csv')
                receipt_url = df['Receipt_url']
                self.view_receipts(receipt_url, keyword, len(receipt_url))
            print("Receipts of all keywords viewed!")
        else:
            return

    def view_ereceipt(self):
        df = pd.read_csv('Receipt_csv/' + self.banner_key + '.csv')
        for keyword in self.keywords:
            ereceipts = df.loc[df['Keyword_Matched'] == keyword]
            ereceipt_urls = ereceipts['Ereceipt_url'].values.tolist()
            print(f"Viewing ereceipts for {keyword}")
            self.view_receipts(ereceipt_urls, keyword, len(ereceipt_urls))
            print("Receipts of all keywords viewed!")

    def view_receipts(self, receipt_url, keyword, length):
        while length:

            if length < self.views:
                views = length
            else:
                views = self.views

            for i in range(views):
                j = randint(0, length-1)
                webbrowser.open(receipt_url[j], new=2)
            print(f"Continue viewing random receipts for keyword-{keyword} (Y/N):")
            option = input()
            if option.lower() == 'y':
                continue
            else:
                break


class SearchPaperReceipts:
    def __init__(self, banner_key, keywords, views, start_date, limit):
        self.banner_key = banner_key
        self.keywords = list(keywords.split(','))
        self.views = int(views)
        self.start_date = start_date
        self.limit = limit
        self.get_receipts()
        DisplayReceipts('paper', self.banner_key, self.keywords, self.views, self.limit)

    def fetch_receipts(self, keyword, cs):

        print(f"Getting receipts for the keyword:{keyword}")

        receipts = cs.execute(
            '''
            SELECT R.ID
            FROM INFOSCOUT.PRICESCOUT.RDL_RECEIPT r
            INNER JOIN INFOSCOUT.PRICESCOUT.RDL_RECEIPTINFO ri
              ON r.ID = ri.RECEIPT_ID
            WHERE (ri.TRANSCRIBED_TEXT ILIKE '% {} %')
            AND r.BANNER_KEY = '{}'
            AND r.transaction_datetime  >= '{}'
            LIMIT {}
            '''.format(keyword, self.banner_key, self.start_date, self.limit)).fetchall()

        receipt_id = []
        receipt_url = []

        url = "https://admin.infoscoutinc.com/admin/rdl/receipt/"
        if receipts:
            for receipt in receipts:
                receipt_id.append(receipt[0])
                receipt_url.append(url + str(receipt[0]) + "/details/")

            receipt_info = {
                "Receipt_ID": receipt_id,
                "Receipt_url": receipt_url,
            }

            try:
                os.mkdir('Receipt_csv/')
            except:
                pass

            df = pd.DataFrame(receipt_info)
            df.to_csv('Receipt_csv/' + self.banner_key + '_' + keyword + '.csv', mode='w', index=False)
            print(f"CSV file created for keyword '{keyword}'")
        else:
            print(f"Sorry, receipts not found for the keyword {keyword}")

    def get_receipts(self):

        cs = snowflake_connector()
        cs.execute("USE warehouse ISC_DW")

        for keyword in self.keywords:
            t = Process(target=self.fetch_receipts, args=(keyword, cs,))
            t.start()
            t.join()

        cs.close()


class SearchEreceipt:
    def __init__(self, banner_key, keywords, views, start_date, limit):
        self.banner_key = banner_key
        self.keywords = list(keywords.split(','))
        self.views = int(views)
        self.start_date = start_date
        self.limit = limit
        if self.get_ereceipts():
            DisplayReceipts('ereceipt', self.banner_key, self.keywords, self.views, self.limit)

    def get_ereceipts(self):
        cs = snowflake_connector()
        cs.execute("USE warehouse ISC_DW")

        ereceipts = cs.execute('''
        SELECT ID, HTML_EMAIL 
        FROM INFOSCOUT.PRICESCOUT.RDL_ERECEIPT
        WHERE BANNER_KEY = '{}'
        AND TRANSACTION_DATETIME > '{}'
        ORDER BY RANDOM()
        LIMIT {}
        '''. format(self.banner_key, self.start_date, self.limit)).fetchall()

        cs.close()

        ereceipt_info = []

        for ereceipt in ereceipts:
            ereceipt_info.append([ereceipt[0], ereceipt[1]])

        p = Pool()
        result = p.map(self.search_receipt, ereceipt_info)
        p.close()
        p.join()

        if None not in result:
            df = pd.DataFrame(result, columns=['Ereceipt_ID', 'Ereceipt_url', 'Keyword_Matched'])
            df = df.sort_values(by='Keyword_Matched', ascending=True)
            try:
                os.mkdir('Receipt_csv/')
            except:
                pass

            df.to_csv('Receipt_csv/' + self.banner_key + '.csv', mode='w', index=False)
            print(f"CSV file created for {self.banner_key}")
            return True
        else:
            print(f"Ereceipts not found for the keywords {self.keywords}")
            return False

    def search_receipt(self, ereceipt):

        ACCESS_KEY_ID = os.getenv('ACCESS_KEY_ID')
        SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')

        s3 = boto3.client(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=SECRET_ACCESS_KEY
        )
        try:
            ereceiptobj = s3.get_object(
                Bucket='isc.pricescout.ecomm',
                Key=ereceipt[1]
            )

            ereceipthtml = ereceiptobj['Body'].read().decode('utf-8')
            soup = BeautifulSoup(ereceipthtml, features="html.parser")
            ereceipttext = soup.get_text()

            ereceipttext = re.sub(r'[\x00-\x09\x0B-\x1F]+', '', ereceipttext)
            ereceipttext = re.sub(r'&nbsp;', ' ', ereceipttext)

            url = 'https://admin.infoscoutinc.com/admin/rdl/ereceipt/'
            matched_ereceipts = []
            for keyword in self.keywords:
                if re.search(keyword, ereceipttext, re.IGNORECASE):
                    matched_ereceipts = [ereceipt[0], url + str(ereceipt[0]) + '/emulate/', keyword]
            return matched_ereceipts if matched_ereceipts else None
        except Exception as e:
            print(f'Error: {e}')
