import unittest
from unittest.mock import patch, MagicMock
from figshare_driver import FigshareMetrics, fetch_report


class TestFigshareMetrics(unittest.TestCase):
    def setUp(self):
        self.settings = {
            'username': 'user',
            'password': 'pass',
            'base_url': 'url',
            'start_date': '2011-07-01',
            'end_date': '2011-07-30',
        }
    @patch('requests.get')
    def test_retrieve_doi(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'resource_doi': 'example_doi'}
        mock_get.return_value = mock_response

        figshare = FigshareMetrics(
            self.settings,
            ['1', '2', '3']
        )
        doi = figshare.retrieve_doi('1')

        self.assertEqual(doi, 'example_doi')

    @patch('requests.get')
    def test_retrieve_doi_fails(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {'resource_doi': 'example_doi'}
        mock_get.return_value = mock_response

        with self.assertRaises(Exception):
            figshare = FigshareMetrics(
                self.settings,
                ['1', '2', '3']
            )
            figshare.retrieve_doi('1')

    @patch('requests.get')
    def test_retrieve_doi_article_id_not_found(self, mock_get):
        article_id = '123456'
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'resource_doi': 'example_doi'}
        mock_get.return_value = mock_response

        figshare = FigshareMetrics(
            self.settings,
            ['1', '2', '3']
        )

        with self.assertRaises(Exception) as context:
            figshare.retrieve_doi(article_id)

            self.assertEqual(str(context.exception), 'Article ID not found')

    @patch('requests.get')
    def test_get_articles_metrics(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'breakdown': True, 'resource_doi': 'example_doi'}
        mock_get.return_value = mock_response

        figshare = FigshareMetrics(
            self.settings,
            ['1', '2', '3']
        )
        metrics = figshare.get_articles_metrics('views', 'url')

        self.assertIsInstance(metrics, list)
        self.assertEqual(len(metrics), 3)

    @patch('figshare_driver.FigshareMetrics.get_articles_views')
    @patch('figshare_driver.FigshareMetrics.get_article_downloads')
    @patch('figshare_driver.FigshareMetrics.get_article_shares')
    def test_fetch_report(self, mock_get_views, mock_get_downloads, mock_get_shares):
        mock_get_views.return_value = [{'views': 10}, {'views': 20}]
        mock_get_downloads.return_value = [{'downloads': 5}, {'downloads': 8}]
        mock_get_shares.return_value = [{'shares': 2}, {'shares': 4}]

        results = FigshareMetrics(
            self.settings,
            ['1', '2', '3']
        )

        self.assertEqual(results.get_articles_views(), [{'shares': 2}, {'shares': 4}])
        self.assertEqual(len(results.get_articles_views()), 2)
        self.assertEqual(len(results.get_article_shares()), 2)


if __name__ == '__main__':
    unittest.main()
