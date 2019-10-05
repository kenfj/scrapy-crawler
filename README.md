# Scrapy Crawler


## Summary

* this is appstore crawler by python Scrapy
* basic setup plus added progress bar etc.
* the result saved as json file with icon jpg


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
```

* run one category

```bash
pipenv shell
CATEGORY=photo-video
scrapy crawl appstore \
    -a category=${CATEGORY} \
    -o jsondata/${CATEGORY}.json \
    -s JOBDIR=crawls/${CATEGORY}-1
```

* or run all categories

```bash
scrapy crawl appstore \
    -o jsondata/appstore.json \
    -s JOBDIR=crawls/appstore-1
```

* you can stop the spider safely at any time (by pressing Ctrl-C)
* and resume it later by issuing the same command
  - but maybe with different json file name
  - otherwise the json will be appended so need to fix manually
* c.f. https://doc.scrapy.org/en/latest/topics/jobs.html


## Read jpg result

```python
from PIL import Image
import numpy as np

icon = Image.open('icondata/photo-video/1006639052.jpg')
img = np.array(icon, 'f')

print(img.dtype)   # dtype('float32')
print(img.shape)   # (246, 246, 3)
# NOTE: the order is RGB (c.f. OpenCV is BGR)
```


## Read json result

```python
import json

with open('jsondata/photo-video.json') as f:
    j = json.load(f)
```

```python
import pandas as pd

df = pd.read_json('jsondata/photo-video.json')

# show rating ranking for example
df.sort_values(
    ['rating_value', 'rating_count'], ascending=False
    )[['rating_value', 'rating_count', 'name']].head()
```


## Convert json result to csv

```bash
COLS=".id, .category, .rating_value, .rating_count, .date_published"
jq -r ".[] | [$COLS] | @csv" jsondata/photo-video.json
```

* `csvkit` is also handy. https://eng-blog.iij.ad.jp/archives/934

```bash
pip install csvkit
in2csv jsondata/photo-video.json
```


## Debug scrapy

```bash
# for example Evernote
scrapy shell https://itunes.apple.com/us/app/evernote/id281796108?mt=8
```


## (reference) command log of initial setup

```bash
export PIPENV_VENV_IN_PROJECT=true
pipenv --python 3.6
pipenv install scrapy tqdm
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
