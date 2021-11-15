from dotenv import load_dotenv
import argparse

from search_receipts import SearchPaperReceipts, SearchEreceipt

load_dotenv(dotenv_path='creds.env')


class GetMatchingReceipts:
    def __init__(self):
        parser = argparse.ArgumentParser()
        args = self.get_args(parser)
        self.run_args(args)

    def get_args(self, parser):
        parser.add_argument('-banner_key', '--banner_key', help='Enter banner key')
        parser.add_argument(
            '-keywords', '--keywords',
            help='Enter keywords separated by , to search',
        )
        parser.add_argument('-views', '--views', help='Enter the number of receipts to open per keyword')
        parser.add_argument('-receipt_type', '--receipt_type', help='Enter receipt type [paper/ereceipt]')
        parser.add_argument('-start_date', '--start_date', help='Enter the receipt start date')
        parser.add_argument('-limit', '--limit', help='Enter number of receipts to search', default=100)
        args = parser.parse_args()
        return args

    def run_args(self, args):
        if args.receipt_type.lower() == 'paper':
            SearchPaperReceipts(args.banner_key, args.keywords, args.views, args.start_date, args.limit)
        elif args.receipt_type.lower() == 'ereceipt':
            SearchEreceipt(args.banner_key, args.keywords, args.views, args.start_date, args.limit)
        else:
            print('Wrong choice!!!')


if __name__ == '__main__':
    GetMatchingReceipts()