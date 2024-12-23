# learning-map-analysis
For University project on creating learning journeys

## How to use this project

See [TOOLING.md](TOOLING.md) for what tools are used and how to set them up.

### Generating figures inside of the project report

```
cd src/learning_map_analysis/crawler_test/wikipedia_crawler
```

Once in that directory, run the following notebooks:

| Experiment | Notebook | Summary of Analysis Conducted |
|---|---|---|
|David Eppstein Analysis|evaluate_wikibooks.ipynb|Analysis is of the David Eppstein Wikibooks|
|Coursera Module Analysis|evaluate_coursera.ipynb|Analysis of the Coursera courses|
|Case Study of Generating Learning Maps|generate_learning_maps.ipynb|Used for the case study and Aedes Albopictus and Aegypti are used from there|
|Statistics for the web pages scraped|data_pipeline_stats.ipynb|Used to find a few statistics about the web pages scraped on David Eppstein Wikibooks|


The above notebooks can be ran without anything run before. Once these have been ran, more data is generated which the following books can be used for:

| Experiment | Notebook | Summary of Analysis Conducted |
|---|---|---|
|Wikibook percentage coverage stats|detailed_chapter_analysis.ipynb|Creates a few stats for the report based on code|
|Coursera percentage coverage stats|coursera_detailed_chapter_analysis.ipynb|Creates a few stats for the report based on code|

### Further notes

There are plenty of exploratory notebooks in that directory.

The code was made to be very flexible and extensible - for example, other languages on different Wikipedias can be used by changing key
constants.

### Future work

1. Different language investigation
2. Mosquito disease clustering 
3. Switching web scraper for exhaustive database
