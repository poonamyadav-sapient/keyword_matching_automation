from dotenv import load_dotenv
import snowflake.connector
import argparse
import os
import pandas as pd
from multiprocessing import Process
import webbrowser
from random import randint

load_dotenv(dotenv_path='creds.env')


class GetMatchingReceipts:
    def __init__(self):
        parser = argparse.ArgumentParser()
        args = self.get_args(parser)
        self.args = args
        self.get_receipts(args)

    def get_args(self, parser):
        parser.add_argument('-banner_key', '--banner_key', help='Enter banner key')
        parser.add_argument(
            '-keywords', '--keywords',
            help='Enter keywords separated by , to search',
            default="EBT,SNAP,WIC"
        )
        parser.add_argument('-views', '--views', help='Enter the number of receipts to open per keyword')
        args = parser.parse_args()
        return args

    def snowflake_connector(self):

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
            LIMIT 100
            '''.format(keyword, self.banner_key)).fetchall()

        receipt_id = []
        receipt_url = []

        url = "https://admin.infoscoutinc.com/admin/rdl/receipt/"
        for receipt in receipts:
            receipt_id.append(receipt[0])
            receipt_url.append(url + str(receipt[0]) + "/details/")

        receipt_info = {
            "Receipt_ID": receipt_id,
            "Receipt_url": receipt_url,
        }

        df = pd.DataFrame(receipt_info)
        df.to_csv(self.banner_key + '_' + keyword + '.csv', mode='w', index=False)
        print(f"CSV file created for keyword '{keyword}'")

    def get_receipts(self, args):
        self.keywords = list(args.keywords.split(','))
        self.banner_key = args.banner_key
        self.views = int(args.views)

        cs = self.snowflake_connector()
        cs.execute("USE warehouse ISC_DW")

        for keyword in self.keywords:
            t = Process(target=self.fetch_receipts, args=(keyword, cs,))
            t.start()
            t.join()

        cs.close()
        self.view_receipts()

    def view_receipts(self):
        while True:
            for keyword in self.keywords:
                print(f"Viewing receipts for {keyword}")
                receipt_url = self.read_csv(self.banner_key + '_' + keyword + '.csv')
                while True:
                    for i in range(self.views):
                        j = randint(0,99)
                        webbrowser.open(receipt_url[j], new=2)
                    print((f"Continue viewing random receipts for keyword-{keyword} (Y/N):"))
                    option = input()
                    if option.lower() == 'y':
                        continue
                    else:
                        break
            print("Receipts of all keywords viewed!")
            break

    def read_csv(self, file_name):
        df = pd.read_csv(file_name)
        receipt_url = df['Receipt_url']

        return receipt_url


if __name__ == '__main__':
    GetMatchingReceipts()