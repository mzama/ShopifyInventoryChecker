##################################################

## This is a simple python script to check the /products.json of a shopify store, 
## and send an email notification if a specific item is in stock.
## Once the appropriate variables are set, it can easily be converted into a 
## portable application through pyinstaller and left running in the background.

##################################################

## Author: Matteo Zamaria, 2021

##################################################

import requests, smtplib, ssl, time

# App stuff
interval = 3600 # Time in seconds to poll the shop
def FindProductByTitle(_arr, _title):   # Helper function to get the specific product from the json
    for i in _arr:
        if i['title'] == _title:
            return i
    return False

# Product stuff
url = ""    # Link to the products in a shopify store in the format https://store_url.com/products.json
prodcut_link = ""   # Link to the actual store page for the product of interest
product_title = ""  # Title of the product as it appears under the 'title' key in the products.json file

# Email stuff
from_email = "" # Email for sender account used by the app
from_name = "Shopify Inventory Checker <%s>" % (from_email) # How the From field should appear in the email, can be useful to include the name of the specific store
to_email = [""]   # List of receiver emails, works best with just one. Can take multiple but only configured to show one name in the email.
to_name = " <%s>" % (to_email[0])   #   How the To field should appear in the email, will only show first email of receiver list
subject = "Product Availability: %s" % (product_title)  # Subject field for the email
mail_server = ""    # The smtp server to use, e.g. smtp.gmail.com
port = 25   # Port for the smtp server
app_password = ""   # The app password for the smtp server.
context = ssl.create_default_context()

# Start message
print("The program started succesfully and is now checking %s for the item %s every %s seconds." % (url, product_title, interval)) 

### MAIN LOOP ###
while(True):
    # Delay an interval before checking the shop again
    time.sleep(interval)
    
    # Actually get the shop info and product
    try:
        r = requests.get(url)
    except:
        print("Error: An error occurred trying to contact the store database. Will try again next cycle in %s seconds." % interval)
        continue
    
    try:
        product = FindProductByTitle(r.json()['products'], product_title)
    except:
        print("Error: An error occurred while looking for the product. The 'products' key may not currently exist. Will try again next cycle in %s seconds." % interval)
        continue

    if not product:
        print("Error: Could not find the product in the store. Will try again next cycle in %s seconds." % interval)
        continue

    # Check if any variant of the product is available, format a string if so
    availabilies_message = ""
    for i in product['variants']:
        if i['available']:
            availabilies_message += "\t-Size %s is currently available.\n" % (i['title'])

    # Check if availabilities_message was filled with any content, skip next steps if not
    if not availabilies_message:
        print("Notice: No availability found. Skipping to next cycle in %s seconds." % interval)
        continue

    ## IF AVAILABLE: ##

    # Format the email body
    email_text = """\
%s is now available in the following sizes:

%s
You can purchase it here: %s
    """ % (product_title, availabilies_message, prodcut_link)

    # Setup the email itself with appropriate headers
    message = """\
From: %s
To: %s
Subject: %s

%s
    """ % (from_name, to_name, subject, email_text)

    # Try to actually send the email
    try:
        with smtplib.SMTP(mail_server, port) as server:
            server.starttls(context=context)
            server.login(from_email, app_password)                 
            server.sendmail(from_email, to_email, message)
            print("Sent the following email from %s to %s: \n%s" % (from_email, to_email, message))
    except:
        print("Error: An error occurred sending the email. Will try again next cycle.")
        continue