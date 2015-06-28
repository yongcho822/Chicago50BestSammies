import csv
import json
import re
from bs4 import BeautifulSoup
from urllib2 import urlopen

STEM_URL = 'http://www.chicagomag.com'
BASE_URL = 'http://www.chicagomag.com/Chicago-Magazine/November-2012/Best-Sandwiches-Chicago/'

soup = BeautifulSoup(urlopen(BASE_URL).read())
sammies = soup.find_all("div", "sammy")
sammy_urls = []
for div in sammies:
    if div.a["href"].startswith("http"):
        sammy_urls.append(div.a["href"])
    else:
        sammy_urls.append(STEM_URL + div.a["href"])

restaurant_names = [div.a.b.find_next_sibling(text=True).encode("utf-8").strip() for div in sammies]


with open("YONGbest-sandwiches-chicago.tsv", "w") as f:
    fieldnames = ("rank", "sandwich", "restaurant", "description", "price", "address", "phone", "website")
    writer = csv.writer(f, delimiter = '\t')
    writer.writerow(fieldnames)
    
    for index, url in enumerate(sammy_urls):
        soup = BeautifulSoup(urlopen(url).read()).find("div",{"id":"page"})
        rank = soup.find("h1","headline").encode_contents().split()[0]
        unsandwich = soup.find("h1","headline").encode_contents().split()[1:]
        restaurant = restaurant_names[index]
        sandwich = " ".join(unsandwich)
        if sandwich.startswith(restaurant):
            sandwich = sandwich.replace(restaurant, "")
        description = soup.find("p", class_= None).encode_contents().strip()
        addy = soup.find("p","addy").em.encode_contents()
        match = re.match(r'([$\d.]+)\. (.+), ([\d-]+)', addy)
        if match:
            extracted_entities = match.groups()
        else:
            pass
        price = extracted_entities[0]
        location = extracted_entities[1] + ", Chicago"
        phone = extracted_entities[2]
        if soup.find("p","addy").em.a:
            website = soup.find("p", "addy").em.a.encode_contents()
        else:
            website = ""


        
        writer.writerow([rank, sandwich, restaurant, description, price, location, phone, website])
    
print "Done writing CSV file."

def geocode(address):
    url = ("http://maps.googleapis.com/maps/api/geocode/json?"
        "sensor=false&address={0}".format(address.replace(" ", "+")))
    return json.loads(urlopen(url).read())

with open("YONGbest-sandwiches-chicago.tsv", "r") as f:
    reader = csv.DictReader(f, delimiter='\t')

    with open("YONGbest-sandwiches-geocode.tsv", "w") as w:
        fields = ["rank", "sandwich", "restaurant", "description", "price", "address", "phone", "website",
                 "formatted_address", "lat", "lng"]
        writer = csv.DictWriter(w, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for line in reader:
            print "Geocoding: {0}".format(line["address"])
            response = geocode(line["address"])
            if response["status"] == u"OK":
                results = response.get("results")[0]
                line["formatted_address"] = results["formatted_address"]
                line["lat"] = results["geometry"]["location"]["lat"]
                line["lng"] = results["geometry"]["location"]["lng"]
            else:
                line["formatted_address"] = ""
                line["lat"] = ""
                line["lng"] = ""
            writer.writerow(line)

