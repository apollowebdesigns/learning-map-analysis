# Crawler

This is using a different method to cross compare against the original method using the XML and focus on specific cases.
```
scrapy startproject wikipedia_crawler
cd wikipedia_crawler
scrapy genspider wikispider en.wikipedia.org
```

How to run the spiders

```
scrapy crawl wikispider -a max_depth=3
```

And for the second spider, use 
```
scrapy crawl wikilearningspider -a max_depth=1
```

Note, the crawlers above 1 take ages! I have never completed it.
