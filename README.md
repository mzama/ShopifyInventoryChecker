# Shopify Inventory Checker
A simple python script to check a Shopify store's inventory for a particular product, and send an email notification if the product is available.
The program can be left to run in the background, and will continually check the store's inventory on a set interval.
## Usage
### From CLI:
python ShopifyInventoryChecker.py
### To Install
The script can easily be converted into a portable application using pyinstaller once the appropriate variables are set. With pyinstaller installed, navigate to the directory of the script and run:
pyinstaller ShopifyInventoryChecker.py from the CLI.