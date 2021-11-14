# keyword_matching_automation
 Use this tool to view paper receipts and ereceipts containing given keywords

 
 #**Installation steps:**
 
 Create a virtual environment by using command `pipenv shell --python 3.7`.
 
 Run the command `pip install -r requirements.txt` to install all the packages.
 
 **Credentials require for accessing snowflake:**
 
Create a creds.env file in the same directory and add the following credentials in it-

`username=` SSO username

`password=` SSO password

`ACCESS_KEY_ID=` AWS access key id

`SECRET_ACCESS_KEY=` ASW access secret key


**Follow steps to use this repository:**

**Step:1** Run the following command to search the receipts of the given banner with the given keywords:

`python get_receipts.py --receipt_type={paper/ereceipt} --banner_key={banner_key} --keywords={keywords separated by commas} 
--views={number of receipts to view per keyword} --start_date={starting date of receipts to search} --limit={number of receipts to search}`

Example:

`python get_receipts.py --receipt_type=paper --banner_key=lowes --keywords=EBT,SNAP,WIC --views=5
--start_date=2020-01-01 --limit=100`

**Step:2** Display receipts:

After the csv files are created, the code will display random receipts on the browser whose count is equal to value provided in `--view={}`

If the receipts viewed are enough press N on the terminal to view random receipts for the next keyword or else press Y to view random receipts of the same keyword.


You can also view the csv file generated in the `Receipt_csv` directory

