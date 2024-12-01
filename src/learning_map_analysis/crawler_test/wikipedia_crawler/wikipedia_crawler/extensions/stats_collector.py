import logging
import matplotlib.pyplot as plt
from scrapy import signals
from scrapy.exceptions import NotConfigured
import json
import os
import numpy as np


class StatsCollectorExtension:
    def __init__(self, stats, output_file, cumulative_file):
        self.stats = stats
        self.output_file = output_file
        self.cumulative_file = cumulative_file
        self.network_sizes = []
        self.cumulative_sizes = []
        logging.info("StatsCollectorExtension initialized")

    @classmethod
    def from_crawler(cls, crawler):
        logging.info("StatsCollectorExtension.from_crawler called")
        if not crawler.settings.getbool('MYEXT_ENABLED'):
            logging.info("StatsCollectorExtension is disabled")
            raise NotConfigured

        output_file = crawler.settings.get('NETWORK_GROWTH_FILE', 'network_growth.json')
        cumulative_file = crawler.settings.get('CUMULATIVE_NETWORK_FILE', 'cumulative_network_growth.json')
        ext = cls(crawler.stats, output_file, cumulative_file)
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_opened(self, spider):
        logging.info(f"Spider opened: {spider.name}")
        self.network_sizes = []
        self._load_cumulative_data()

    def item_scraped(self, item, response, spider):
        current_size = len(spider.network)
        self.network_sizes.append(current_size)
        logging.info(f"Network size: {current_size}")

    def spider_closed(self, spider):
        logging.info(f"Spider closed: {spider.name}. Final network size: {len(spider.network)}")
        spider.link_counter
        self._update_cumulative_data()
        self._write_network_growth()
        self._plot_network_growth(spider.link_counter, spider.link_counter_list)
        self._plot_duration(spider.end_times)

    def _load_cumulative_data(self):
        """Load cumulative data from a file."""
        if os.path.exists(self.cumulative_file):
            with open(self.cumulative_file, 'r') as f:
                self.cumulative_sizes = json.load(f).get("cumulative_network_growth", [])
        else:
            self.cumulative_sizes = []

    def _update_cumulative_data(self):
        """Update cumulative data with the new network sizes."""
        self.cumulative_sizes.extend(self.network_sizes)
        with open(self.cumulative_file, 'w') as f:
            json.dump({"cumulative_network_growth": self.cumulative_sizes}, f, indent=2)
        logging.info(f"Cumulative network growth data updated in {self.cumulative_file}")

    def _write_network_growth(self):
        """Write current run's network growth to a file."""
        data = {"network_growth": self.network_sizes}
        with open(self.output_file, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Network growth data written to {self.output_file}")

    def _plot_network_growth(self, link_counter, link_counter_list):
        """Plot cumulative network growth over multiple runs."""
        logging.info("Plotting cumulative network growth")
        plt.figure(figsize=(10, 5))
        plt.plot(range(1, len(link_counter.keys()) + 1), np.cumsum(list(link_counter.values())), marker='o', color='blue', label='Links Scraped')
        # plt.plot(range(1, len(link_counter_list.keys()) + 1), link_counter_list.values(), marker='o', color='green', label='Links Scraped with Duplicates', alpha=0.3)
        # plt.plot(range(1, len(link_counter_list.keys()) + 1), [20**i for i in range(1, len(link_counter_list.keys()) + 1)], marker='o', color='red', label='Max Links Extraction', alpha=0.3)
        plt.title('Cumulative Network Growth Over Multiple Runs')
        plt.xlabel('Cumulative Number of Items Scraped')
        plt.ylabel('Network Size')
        plt.grid(True)
        plt.legend()  # Add this line to include the legend
        plot_filename = 'cumulative_network_growth_plot.png'
        plt.savefig(plot_filename)
        plt.close()
        logging.info(f"Cumulative plot saved as {plot_filename}")
        with open("cumulative_network_growth_plot_data.json", 'w') as f:
            json.dump(link_counter, f, indent=2)

    def _plot_duration(self, end_times):
        """Plot cumulative network growth over multiple runs."""
        logging.info("Plotting cumulative network growth")
        plt.figure(figsize=(10, 5))
        plt.plot(range(1, len(end_times.keys()) + 1), np.cumsum(list(end_times.values())), marker='o', color='blue', label='Duration in minutes')
        # plt.plot(range(1, len(link_counter_list.keys()) + 1), link_counter_list.values(), marker='o', color='green', label='Links Scraped with Duplicates', alpha=0.3)
        # plt.plot(range(1, len(link_counter_list.keys()) + 1), [20**i for i in range(1, len(link_counter_list.keys()) + 1)], marker='o', color='red', label='Max Links Extraction', alpha=0.3)
        plt.title('Cumulative duration of Scrape Length')
        plt.xlabel('Iterations')
        plt.ylabel('Duration (m)')
        plt.grid(True)
        plt.legend()  # Add this line to include the legend
        plot_filename = 'cumulative_time_growth_plot.png'
        plt.savefig(plot_filename)
        plt.close()
        logging.info(f"Cumulative plot saved as {plot_filename}")
        with open("cumulative_time_growth_plot_data.json", 'w') as f:
            json.dump(end_times, f, indent=2)
