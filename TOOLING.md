# Tooling

## Setup

1. Have Python 3.12 installed
2. Install [PDM for dependency management](https://pdm-project.org/en/latest/) and installation (see troubleshooting if any issues)


## Troubleshooting

### PDM Installation Issues

If you have issues or lack of permissions to install PDM, pip install the dependencies from the pyproject.toml file.

### Package installation issues after pdm is installed

Any issues, delete the `pdm.lock` file and then run `pdm install` to reinstall the packages.

### Key packages used

1. Scrapy for web scraping
2. Jupyter for experiments
3. NetworkX for network exploration and generating the recommendations
