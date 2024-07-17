from logging import getLogger
from typing import List
import requests

logger = getLogger(__name__)


class FigshareMetrics:
    """
    Class to retrieve metrics for articles from Figshare.
    """

    def __init__(
            self,
            settings,
            ids: List[int]
    ) -> None:
        self.username = settings.get('username')
        self.password = settings.get('password')
        self.url = settings.get('base_url')
        self.start_date = settings.get('start_date')
        self.end_date = settings.get('end_date')
        self.article_ids = ids
        self.article_doi_mapping = dict()

    def get_articles_views(self) -> List:
        """
        Retrieve views metrics for a list of article IDs.

        Returns:
            List : Contains article metrics views.
        """
        counter = 'views'
        full_url = f'{self.url}/month/{counter}/article'
        return self.get_articles_metrics(counter, full_url)

    def get_article_downloads(self) -> List:
        """
        Retrieve downloads metrics for a list of article IDs.

        Returns:
            List : Contains article metrics downloads.
        """
        counter = 'downloads'
        full_url = f'{self.url}/month/{counter}/article'
        return self.get_articles_metrics(counter, full_url)

    def get_article_shares(self):
        """
        Retrieve shares metrics for a list of article IDs.

        Returns:
            List : Contains article metrics shares.
        """
        counter = 'shares'
        full_url = f'{self.url}/month/{counter}/article'
        return self.get_articles_metrics(counter, full_url)

    def retrieve_doi(self, article_id: str) -> str:
        """The stats API endpoint doesn't provide a DOI for
        each article."""
        if article_id not in self.article_doi_mapping:
            url = f'https://api.figshare.com/v2/articles/{article_id}'
            headers = {'Content-Type': 'application/json'}
            response = requests.get(
                url,
                auth=(self.username, self.password),
                headers=headers
            )

            if (
                    response.status_code == 200
                    and 'resource_doi' in response.json()
            ):
                article_doi = response.json()['resource_doi']
                self.article_doi_mapping[article_id] = article_doi
            else:
                raise Exception('Article ID not found')

        return self.article_doi_mapping[article_id]

    def get_articles_metrics(self, counter: str, url: str) -> List:
        """
        Download the metrics dynamically for each counter,
        for reference, see Endpoint format:
            https://docs.figshare.com/#stats_breakdown

        Args:
            counter (str): 'views', 'downloads' or 'shares'
            url (str): Url with all the parameters

        Returns:
            List: Metrics organized by ID and counter
        """
        data = []
        headers = {'Content-Type': 'application/json'}
        dates = f'start_date={self.start_date}&end_date={self.end_date}'

        for article_id in self.article_ids:
            full_url = f'{url}/{article_id}?{dates}'
            response = requests.get(
                full_url, auth=(self.username, self.password), headers=headers
            )
            if response.status_code == 200:
                measure_url = (
                    f'https://metrics.operas-eu.org/figshare/{counter}/v1'
                )

                data.append(
                    {
                        'measure': measure_url,
                        'Article ID': article_id,
                        'Metrics': response.json(),
                        'doi': self.retrieve_doi(article_id)
                    }
                )
            else:
                logger.info(
                    f"""Failed to fetch article {article_id}.
                    Status code: {response.status_code}"""
                )
        return data


def fetch_report(
        settings,
        article_ids: List
) -> List:
    """
    Fetch the views, downloads and shares by country, artice_id
    and dois
    """
    figshare_metrics = FigshareMetrics(settings, ids=article_ids)

    # Retrieve article metrics
    results = [
        figshare_metrics.get_articles_views(),
        figshare_metrics.get_article_downloads(),
        figshare_metrics.get_article_shares()
    ]

    return results
