"""Actual Flask generation and PNG downloads with synthetic input only."""
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(os.environ.get('WORDCLOUD_APP_SOURCE', Path(__file__).resolve().parents[1] / 'app.py'))

class GenerationFilterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        os.environ.setdefault('MPLCONFIGDIR', str(self.root / 'mpl'))
        spec = importlib.util.spec_from_file_location('synthetic_wordcloud_app', SOURCE)
        self.module = importlib.util.module_from_spec(spec)
        # This optional regression requires a runtime without NLTK, so imports
        # cannot download corpora. Test the application's supported fallback.
        self.assertIsNone(importlib.util.find_spec('nltk'), 'Use an isolated runtime without NLTK')
        spec.loader.exec_module(self.module)
        self.assertTrue(self.module.WORDCLOUD_AVAILABLE, 'Requires real WordCloud library')
        self.module.TEMP_TOKEN_FOLDER = str(self.root / 'tokens')
        Path(self.module.TEMP_TOKEN_FOLDER).mkdir()
        self.seen = {}
        original = self.module.generate_top_words_chart
        def capture(frequencies, session):
            self.seen['frequencies'] = frequencies
            return original(frequencies, session)
        self.module.generate_top_words_chart = capture
        self.text = ('secretword ' * 12) + ('orchard garden blossom ' * 8) + ('fig ' * 5)

    def generate(self, stop='', minimum=3):
        from PIL import Image
        with self.module.app.test_client() as client, patch('socket.create_connection', side_effect=AssertionError('No network')) as network:
            response = client.post('/mcp/wordcloud/generate', data={
                'text': self.text, 'additional_stopwords': stop,
                'min_word_length': str(minimum), 'width': '500', 'height': '300'})
            self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
            body = response.get_json()
            self.assertTrue(body['success'])
            token = body['redirect'].split('/')[-1]
            sid = self.module.active_tokens[token]['uuid']
            metadata = json.loads((Path(self.module.TEMP_TOKEN_FOLDER) / sid / 'metadata.json').read_text())
            self.assertEqual(set(metadata['files']), {'wordcloud_1', 'wordcloud_2', 'wordcloud_3', 'top_25_words'})
            for name in metadata['files'].values():
                download = client.get(f'/mcp/wordcloud/download/{token}/{name}')
                self.assertEqual(download.status_code, 200)
                self.assertIn('attachment', download.headers.get('Content-Disposition', ''))
                data = download.get_data()
                self.assertTrue(data.startswith(b'\x89PNG\r\n\x1a\n'))
                with Image.open(io.BytesIO(data)) as image:
                    self.assertGreater(image.width, 0)
                    self.assertGreater(image.height, 0)
                    image.verify()
                download.close()
            network.assert_not_called()
        return dict(self.seen['frequencies'])

    def test_custom_exclusion_reaches_chart_and_real_downloads(self):
        self.assertEqual(self.generate('secretword'), {'orchard': 8, 'garden': 8, 'blossom': 8, 'fig': 5})

    def test_unfiltered_counts_preserved(self):
        self.assertEqual(self.generate(), {'secretword': 12, 'orchard': 8, 'garden': 8, 'blossom': 8, 'fig': 5})

    def test_minimum_and_normalized_custom_filters_together(self):
        self.assertEqual(self.generate(' SECRETWORD , Garden ', 7), {'orchard': 8, 'blossom': 8})

if __name__ == '__main__':
    unittest.main()
