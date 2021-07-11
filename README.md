# Scrapy Crawler


## Summary

* this is appstore crawler by python Scrapy
* basic setup plus added progress bar etc.
* the result saved as csv file with icon image


## Setup

```bash
brew install pyenv
brew install pipenv

pipenv install
pipenv install --dev
```


## Run

```bash
pipenv shell
cd appstore_crawler
export LANG=en_US.utf8  # to avoid ParserError
```

* run one category

```bash
# set category
CATEGORY=photo-video

# this example will crawl urls includes /genre/ios-{category}
# i.e. https://apps.apple.com/us/genre/ios-photo-video/id6008

scrapy crawl appstore \
    -a category=${CATEGORY} \
    -s JOBDIR=crawls/${CATEGORY}-1  # update this number or delete the dir
```

* or run all categories

```bash
scrapy crawl appstore \
    -s JOBDIR=crawls/appstore-1 \
    -o csvdata/appstore.csv
```

* you can stop the spider safely at any time (by pressing Ctrl-C)
* and resume it later by issuing the same command
  - the csv will be appended
* c.f. https://doc.scrapy.org/en/latest/topics/jobs.html


## Read icon image

```python
from PIL import Image
import numpy as np

icon = Image.open('appstore_crawler/icondata/photo-video/1006639052.png')
img = np.array(icon, 'f')

print(img.dtype)   # dtype('float32')
print(img.shape)   # (246, 246, 3)
# NOTE: the order is RGB (c.f. OpenCV is BGR)
```


## Read CSV result

```python
import pandas as pd

df = pd.read_csv('appstore_crawler/csvdata/photo-video.csv')

df.head()

df.columns
Index(['id', 'category', 'name', 'subtitle', 'url', 'date_published',
       'rating_value', 'rating_count', 'rating_ratio', 'price_category',
       'price', 'price_currency', 'has_in_app_purchases', 'author_name',
       'author_url', 'description'],
      dtype='object')

# show rating ranking for example
df.sort_values(
    ['rating_value', 'rating_count'], ascending=False
    )[['rating_value', 'rating_count', 'name']].head()
```


## Debug scrapy

```bash
# for example Evernote
scrapy shell https://apps.apple.com/us/app/evernote/id281796108
# another example Dropbox
scrapy shell https://apps.apple.com/us/app/dropbox/id327630330
```


## (reference) command log of initial setup

```bash
export PIPENV_VENV_IN_PROJECT=true
pipenv --python 3.6
pipenv install scrapy tqdm python-dateutil pandas
pipenv run pip list
pipenv graph
```

```bash
pipenv shell
scrapy startproject appstore_crawler
cd appstore_crawler
scrapy genspider appstore example.com
```

```bash
# check
pipenv update --outdated

# do update
pipenv update
pipenv update --dev
pipenv clean

# re-crete virtual env
pipenv --rm
pipenv install
pipenv install --dev
```


## Reference

### Scrapy

* https://scrapy.org/
* https://docs.scrapy.org/en/latest/intro/tutorial.html
* https://doc.scrapy.org/en/latest/topics/spiders.html#crawlspider-example
* https://note.nkmk.me/python-scrapy-tutorial/
* https://casualdevelopers.com/tech-tips/lets-get-started-with-scrapy-and-selenium-on-python/
* http://kzkohashi.hatenablog.com/entry/2018/08/23/094844

### App Store

* https://itunes.apple.com/us/genre/ios-productivity/id6007?mt=8
* https://www.apple.com/itunes/charts/top-grossing-apps/
* https://rss.itunes.apple.com/
