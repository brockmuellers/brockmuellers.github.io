---
layout: post
title:  "Web scraper to find new products"
categories: software
---

I'm a huge fan of the REI used gear program. Unfortunately, they don't always have all products available. It's a pain to keep checking the used gear website until the product is available, and I'm often inclined to go buy it new. So, I thought I'd write a little script to scrape the site and do the work for me!

I'm starting off with a local script that I can run manually. The next step will be to automate it, but that's a topic for another time.

This is my first foray into web scraping! I don't know why it took me so long - it's not particularly hard. Here's my process.

---

## Getting started

Let's get set up!

For starters, I'm using python 3.6.9 and pip3 as a package installer. (I should probably get to the modern age and update to 3.8, but this works just fine.)

Since I'm doing something new, I did a bit of web sleuthing to find out how people typically do this sort of thing. Python seems to be a common choice, which makes sense - it's a great language for quick scripts and munging data. The `requests` library is a clear choice for making HTTP requests, and Beautiful Soup is popular for pulling data from HTML.

Let's go ahead and install those dependencies:

```
$ pip3 install requests
$ pip3 install beautifulsoup4
```

In fact, we can be good Python developers and pin those versions in a `requirements.txt` file. (I wouldn't typically care for a little project like this, but I'd like to be able to deploy this to something like AWS Lambda. Being explicit about your dependencies is nice when you're running stuff externally like that.) This file can go in the project root directory and looks like this:

```
beautifulsoup4==4.8.2
requests==2.23.0
```

We can install dependencies from that file by running `pip3 install -r requirements.txt`.

---

I'll start out by playing around in IPython (`pip3 install ipython`). It's my favorite way to play around with python. I'll also create a file to hold code that I want to keep. Let's call it `scrape.py`. (People like using Jupyter Notebooks for this sort of interactive development, but I've never tried that and it doesn't seem necessary in this case.)

Starting IPython is easy: just run `ipython`.

---

## Playing around with our new libraries

Great! We can start writing code now. First, I know that we'll need to make an HTTP request to get the page we're scraping.

The requests library is easy to use - docs are [here](<https://requests.readthedocs.io/en/master/>). Let's try getting the HTML for a page in IPython.

```python
>> import requests
>> r = requests.get("http://www.google.com")
>> html = r.text
```

That's some HTML! Now we need to choose the right URL to scrape. This project is automating something that I already do - making a search for a product I'm interested in. So let's use the URL for that search. There may be a better way to scrape the site for products, but this is a decent place to start.

A big blob of HTML text isn't particularly useful on it's own. That's where Beautiful Soup comes in. We'll follow the quick start instructions in the [docs](https://beautiful-soup-4.readthedocs.io/en/latest/) and get soup for our page:

```python
>> url = "https://www.rei.com/used/shop/search?q=magma%2030%20sleeping%20bag"
>> html = requests.get(url).text
>> from bs4 import BeautifulSoup
>> soup = BeautifulSoup(html, 'html.parser')
```

Now we have a soup object! We can run stuff like `soup.a` to get `<a>` tags in the HTML.

---

I'm going to want to run this repeatedly as I play around, so I'm going to make a function in my `scrape.py` file to hold that logic.

(I had to google how to write a python function, yikes. It's been a while.)

```python
from bs4 import BeautifulSoup
import requests

def get_soup(url):
    r = requests.get(url)
    return BeautifulSoup(r.text, 'html.parser')
```

To use this in IPython, import the module: `import scrape`. When we make changes to the file, we need to reload the module. The simplest way to do that is restart IPython, but I usually prefer:

```python
>> import importlib
>> importlib.reload(scrape)
```
---

Now things get a little tricky. What do we want to pull out of the page? How do we select the right thing, and make sure it won't break when REI makes minor changes to the website?

Let's use Chrome DevTools to examine the page. All of the products that come up in the search are in a `<ul>` list, and each `<li>` item has the class `"TileItem`". Nothing else on the page has the class `"TileItem"`, so that seems like a safe thing to filter by.

```python
>> items = search_soup.find_all("li", class_="TileItem")
```

Now we have the correct items, but each of those is still a long blob of HTML. We just want the title of the item. Titles are located in a `<span>` with class `"title"`. So, for an individual item, we can run:

```python
>> title = item.find_all("span", class_="title")[0].contents[0]
"Magma 30 Sleeping Bag"
```

Beautiful Soup is a powerful tool, and you can filter HTML in almost any way imaginable. [The docs](https://beautiful-soup-4.readthedocs.io/en/latest/) are pretty comprehensive. It's a bit of a challenge to choose filters that are not too brittle, but otherwise it's easy to use. I'm a fan.

---

## Setting up an executable script

Finally this is starting to come together. I'd like to run what we have as a script. To do this, we need a) our file to be executable, and b) an entrypoint.

To make the file executable, we need to put this line at the top: `#!/usr/bin/env python3`. Additionally, in the command line, we run `chmod +x scrape.py` to give us permission to execute the file.

There needs to be an entrypoint that specifies the code to run. In `scrape.py`, let's add this block at the bottom of the file:

```python
if __name__ == '__main__':
    # We'll replace this with the code we want to run.
    print("This is a script!")
```

Now run the script!

```
$ python3 main.py
This is a script!
```

---

## Putting it all together

Now we can put it all together!

To do this, there are a couple of important decisions we need to make: program input and program output.

### Search URL input

We could just be lazy and hardcode URLs in. But it's nice to be able to edit code and the input URLs separately, especially if this is deployed to a service like AWS Lambda. You don't necessarily want to redeploy your Lambda every time you want to look for a new product. So, for now, we'll just put them in a file in the project root directory.

Open the file (use a [context manager](https://www.geeksforgeeks.org/context-manager-in-python/) so resources are released appropriately).

```python
with open('rei_used_gear_searches.txt', 'r') as file:
    urls = file.read().splitlines()
```

Apparently we need to use `read().splitlines()` instead of `readlines()`, otherwise we'll end up with `\n` at the end of every value. Good to know.

Hmmm...we could make this a bit better. Search URLs are pretty obtuse and hard to read. It's not very user-friendly to spit out a bunch of URLs in the results. So let's label them. A CSV of `$LABEL, $URL` should work.

```python
urls = []
with open(filename, "r") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        urls.append({"label": row[0], "url": row[1]})
```

And our CSV file:
```
magma30regular,https://www.rei.com/used/shop/search?q=magma%2030%20sleeping%20bag&size=REGULAR%20-%20RIGHT%20ZIP
altras,https://www.rei.com/used/shop/womens-footwear?brand=Altra&size=6
```

### Results to output

We could just print the results of each search URL. That would be easy. But, from experience, I know that sometimes I want to know which products have been added instead of which products exist. 

For example, perhaps I'm looking for a particular brand of shoe. I really like Altra shoes, for their zero drop and natural foot shape. There are a number of models I'd be interested in. I might do a search for them today, and not want any of the models currently available on the used gear site. In this case, I'll want my tool to tell me if a new model has been added, so I can check it out.

With this goal, we need to come up with a way to tell if a product has been added since we last ran this tool. To do that, we need to save results somewhere, so we can compare results from this run with the last run.

Writing our results to a file is a simple way to do this. We'll timestamp each file, so we know which is most recent. (A naive way to do that would be to delete the old results file and write a new file. But there's a gotcha - this isn't robust to failure. If the program dies in between deleting the old results file and writing the new file - totally possible - we won't be able to rerun the program and make a comparison.) We'll also choose to write one file per product. It's an arbitrary choice. Here's the code for writing the results of one search.

```python
def save_products_list(results, label, target_dir):
    timestamp = str(int(round(time.time())))
    filename = target_dir + label + '_' + timestamp + ".txt"
    with open(filename, "w") as file:
        [file.write(r + "\n") for r in results]
```

Now that we have a list saved, let's run a comparison. This is a bit messy, but it'll do the job. It runs once per search URL.

```python
def compare_to_previous_products(current_products, label, target_dir):
    # Get and sort all result files (so they're in order of timestamp)
    sorted_results_files = sorted(os.listdir(target_dir))
    # Pick out the result files corresponding to this particular search label
    previous_files = [f for f in sorted_results_files if label in f]

    with open(target_dir + previous_files[-1], 'r') as file:
        previous_products = file.read().splitlines()

    if sorted(previous_products) != sorted(current_products):
        print("FOUND A DIFFERENCE FOR PRODUCT {} (from {})".format(
            label, previous_files[-1]))
        print("OLD: " + str(previous_products))
        print("NEW: " + str(current_products))
```

Good enough!

---

It's also worth trying to make this a bit robust to changes on the REI website. 

* What if items no longer have the class `"TileItem"`? This could be a problem - then our list of items will just be empty and it'll appear as if there are no products. Let's use a handy feature of the website: when you do a search, it shows you how many results were found in a div that says "x results". That div has the class `"count`", and doesn't exist if no products were found. So we'll compare that to the number of `"TileItem"`s we found.
  ```python
  expected_count_div = search_soup.find("div", class_="count")

  if expected_count_div is None:
      print("No products found.")

  else:
      expected_count = int(expected_count_div.find("span").contents[0])
      if len(items) != expected_count:
          raise AssertionError(
              "Error on page {}: found {} items, but page said there would be {}".format(
                  url, len(items, expected_count)))

  ```
* What if the "x results" div ceases to exist, or its class name has changed so we can't find it? I'm going to be lazy and not solve this problem right now, but its worth noting.

* What if there isn't a `<span>` containing the item's title? The code will blow up if that happens. Not elegantly, but we'll know. This line will happily throw an error.
  ```python
  title = item.find_all("span", class_="title")[0].contents[0]
  ```

---

Besides that, there's not too much to think about. We can clean it up, handle some edge cases, etc. We'll also liberally sprinkle in print statements so it's clear what's happening when the code runs. 

---

## Results

So what do we end up with? Our first run is not particularly interesting.

```
$ python3 main.py
Opening search URL file rei_used_search_urls.csv
Found 2 search URLS

----------------------------

EXAMINING PRODUCT: magma30regular
Search URL: https://www.rei.com/used/shop/search?q=magma%2030%20sleeping%20bag&size=REGULAR%20-%20RIGHT%20ZIP&size=REGULAR%20-%20LEFT%20ZIP&size=REGULAR
No products found.

RESULT:
This is the first search for product magma30regular

----------------------------

EXAMINING PRODUCT: altras
Search URL: https://www.rei.com/used/shop/womens-footwear?brand=Altra&size=6
Found product Olympus 2.0 Trail-Running Shoes
Found product Torin 2.5 Road-Running Shoes
Found product Torin 2.5 Road-Running Shoes
Found product Paradigm 2.0 Road-Running Shoes

RESULT:
This is the first search for product altras

```

But when we run it the next day:

```
$ python3 main.py
Opening search URL file rei_used_search_urls.csv
Found 2 search URLS

----------------------------

EXAMINING PRODUCT: magma30regular
Search URL: https://www.rei.com/used/shop/search?q=magma%2030%20sleeping%20bag&size=REGULAR%20-%20RIGHT%20ZIP
Found product Magma 30 Sleeping Bag

RESULT:
FOUND A DIFFERENCE FOR PRODUCT magma30regular (from magma30regular_1582257372.txt)
OLD: []
NEW: ['Magma 30 Sleeping Bag']

----------------------------

EXAMINING PRODUCT: altras
Search URL: https://www.rei.com/used/shop/womens-footwear?brand=Altra&size=6
Found product Olympus 2.0 Trail-Running Shoes
Found product Torin 2.5 Road-Running Shoes
Found product Torin 2.5 Road-Running Shoes
Found product Paradigm 2.0 Road-Running Shoes

RESULT:
No difference found for product altras

```

Hooray! The REI Magma 30 sleeping bag that I've been waiting for is finally available used. This little tool is proving useful already.

Coming another day: running this automatically, probably via AWS Lambda.

See the proof-of-concept code [here](https://github.com/brockmuellers/find-products/tree/303bc37141469ad2776830618ed1832f056808ae).
