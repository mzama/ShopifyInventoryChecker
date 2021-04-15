##################################################

## This is a simple ruby script to check the /products.json of a 
## shopify store, and send an email notification if a specific item is in stock.

##################################################

## Author: Matteo Zamaria, 2021

##################################################
require 'json'
require 'open-uri'
require 'net/smtp'

# App Stuff
interval = 3600 # Time in seconds to poll the shop 

# Product stuff
url = ""    # Link to the products in a shopify store in the format https://store_url.com/products.json
prodcut_link = ""   # Link to the actual store page for the product of interest
product_title = ""  # Title of the product as it appears under the 'title' key in the products.json file

# Email Stuff
from_email = "" # Email for sender account used by the app
from_name = "Shopify Inventory Checker <#{from_email}"  # How the From field should appear in the email, can be useful to include the name of the specific store
to_email = ""   # The receiver email account to send availability notifications to
to_name = " <#{to_email}"   # How the To field should appear in the email
subject = "Product Availbility: #{product_title}"   # Subject field for the email
mail_server = "" # The smtp server to use, e.g. smtp.gmail.com
port = 25   # Port for the smtp server
mail_domain = "localhost"   # Domain being used to send this
app_password = ""   # The app password for the smtp server.

puts "The program started succesfully and is now checking #{url} for the item #{product_title} every #{interval} seconds."

### MAIN LOOP ###
while true do
    sleep interval
    # Get the file and convert it to json
    begin
        doc = URI.open(url).read
    rescue
        puts "Error: An error occurred trying to contact the store database. Will try again next cycle in #{interval} seconds."
        next
    end

    # Convert to JSON and find the product of interest
    begin
        json = JSON.parse(doc)
        # Find the product of interest
        item = json['products'].select { |prod| prod['title'] == product_title }[0]
        available_variants = ""

        item['variants'].each do |i|
            available_variants += "<li>Size #{i['title']} is available.</li>\n" if i['available']
        end
    rescue
        puts "Error: Could not find the product in the store. Will try again next cycle in #{interval} seconds."
        next
    end

    # If no available variant was found, skip to the next cycle
    if available_variants&.empty?
        puts "Notice: No availability found. Skipping to next cycle in #{interval} seconds."
        next
    end

    ## IF AVAILABLE ##

    # Create and format the actual email
    message = <<MESSAGE_END
From: #{from_name}
To: #{to_name}
Content-type: text/html
Subject: #{subject}

<h1>#{product_title} is now available with the following options: </h1>
<ul>
#{available_variants}
</ul
<br />
<p>
You can purchase it here: #{prodcut_link}
</p
MESSAGE_END

    # Start the smtp link and send the email
    begin
        smtp = Net::SMTP.new mail_server, port
        smtp.enable_starttls
        smtp.start(mail_domain, from_email, app_password, :login) do
            smtp.send_message(message, from_email, to_email)
        end
        puts "Notice: Sent the following email from #{from_email} to #{to_email}: \n#{message}"
    rescue
        puts "Error: An error occurred sending the email. Will try again next cycle in #{interval} seconds."
        next
    end
end