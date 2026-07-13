We have created a free tool to convert WIX data into Shopify-compatible format.
You can use this tool to convert your product, customer, and order data into files that are ready to import into Shopify.
Once converted, you can simply upload the new data files to Shopify.

Please see the detailed instructions at 

See the code and guide below.


**Step 1 — Install Python (one-time setup)**

Python is the free program that runs the script. If you already have Python installed, skip to Step 2.
1.	Go to python.org/downloads in your web browser.
2.	Click the yellow “Download Python” button.
3.	Open the downloaded file and run the installer.

**Important**

On the first install screen, tick the box that says
“Add Python to PATH” before clicking Install.

4.	Click Install Now and wait for it to finish.

To check it worked, open your terminal (Command Prompt on Windows, Terminal on Mac) and type:
python --version

If you see a version number like “Python 3.12.0”, you are ready for Step 2.


**Step 2 — Install the Required Add-ons**

The script needs two free add-on packages to read Excel/CSV files. Open your terminal and type this single line:
pip install pandas openpyxl

Press Enter and wait a few seconds for it to finish. You only need to do this once.


**Step 3 — Save Your Files in One Folde**r

Create a new folder on your Desktop (for example, “Wix_to_Shopify_migration”). 
Inside it, create another folder called “input” — this is where all your WIX export files will go.
Your folder structure should look like this:
Wix_to_Shopify_migration/
  converter.py
  input/
    wix_products.csv
    wix_customers.csv
    wix_orders.csv

Place the script file directly inside “Wix_to_Shopify_migration”, and place your WIX CSV exports inside the “input” folder:

•	input/wix_products.csv  (your WIX product export — if migrating products)

•	input/wix_customers.csv  (your WIX customer export — if migrating customers)

•	input/wix_orders.csv  (your WIX order export — if migrating orders)

You do not need all three files. Only include the ones you want to convert.


**Step 4 — Run the Script**

5.	Open your terminal.
6.	Navigate to the folder you created. For example:
cd Desktop/Wix_to_Shopify_migration
7.	Run the script by typing:

python converter.py --type products (If you want convert only products)

python converter.py --type orders (If you want convert only orders)

python converter.py --type customers (If you want convert only customers)

python converter.py --type all (If you want convert all (products, customers and orders) )


**Step 5 — Find Your Converted Files**

Once the script finishes, it creates a new folder called “output” inside your project folder. Open it to find:
File Name	What It Contains
shopify_products.csv	Your products, ready for Shopify
shopify_customers.csv	Your customers, ready for Shopify
shopify_orders.csv	Your orders, ready for the Matrixify app


**Step 6 — Import Into Shopify**

Products
9.	In Shopify Admin, go to Products.
10.	Click the Import button (top right).
11.	Choose the file shopify_products.csv and click Upload.
12.	Review the preview, then click Import products.

Customers

13.	In Shopify Admin, go to Customers.
14.	Click Import customers.
15.	Choose the file shopify_customers.csv and click Upload.
16.	Review the preview, then click Import customers.

Orders (needs one extra free app)

Shopify does not allow orders to be imported directly. You need the free Matrixify app first:

17.	In Shopify Admin, go to Apps → Shopify App Store.
18.	Search for “Matrixify” and install it (free plan available).
19.	Open Matrixify → click Import → Add file → choose shopify_orders.csv.
20.	Review and click Import.

**Troubleshooting — Common Questions**

Problem	- Solution

“python is not recognized”	Reinstall Python and make sure to tick “Add Python to PATH”

“No module named pandas”	Run: pip install pandas openpyxl

File not found Make sure the CSV file is in the same folder structure as described in Step 3, and that you typed the correct command as mentioned in Step 4.

Some images are missing in Shopify	This happens when WIX image links are private/demo links — upload those images manually after import

Order import fails	Make sure you are using the Matrixify app, not Shopify's built-in import — Shopify cannot import orders directly

Quick Reference — Every Time You Run It

1. Open terminal in your project folder
2. Type: python converter.py --type all
3. Find your results in the output folder

That's it — no coding required. If you run into any issue not listed above, check that your CSV files were exported correctly from WIX and try again.

At FirstWire, we can do the complete migration and make sure that your new Shopify store is setup properly and optimized for Design, User Experience, Performance, SEO and CRO.

Please Contact Us for a custom proposal at https://firstwireapp.com/get-a-quotation/

You can also check our other Shopify Services at https://firstwireapp.com/e-commerce/shopify/
