# keyword_matching_automation
 Use this tool to view receipts containing given keywords

 
 #**Installation steps:**
 
 Create a virtual environment by using command `pipenv shell --python 3.7`.
 
 Run the command `pip install -r requirements.txt` to install all the packages.
 
 **Credentials require for accessing snowflake:**
 
Create a creds.env file in the same directory and add the following credentials in it-

`username=` SSO username

`password=` SSO password


**Follow step to use this repository:**

**Step:1** Run the following command to search the receipts of the given banner with the given keywords:

`python get_receipts.py --banner_key={banner_key} --keywords={keywords separated by commas} --views={number of receipts to view per keyword}`

Example:

`python get_receipts.py --banner_key=lowes --keywords=EBT,SNAP,WIC --views=5`

**Step:2** Display receipts:

After the csv files are created, the code will display random receipts on the browser whose count is equal to value provided in `--view={}`

If the receipts viewed are enough press N on the terminal to view random receipts for the next keyword or else press Y to view random receipts of the same keyword.

