import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import codex_model_gate as gate
from gate_execution import AuthorizedTask, prepare_task
from gate_browser_mcp import GateBrowserServer


class BrowserNavigationTests(unittest.TestCase):
    def test_direct_url_and_follow_link_need_no_search(self):
        with tempfile.TemporaryDirectory() as folder:
            server = GateBrowserServer(Path(folder))
            page = Mock()
            page.goto.return_value.status = 200
            server._ensure_page = Mock(return_value=page)
            server.snapshot = Mock(return_value={'text': 'conteúdo'})
            self.assertEqual(server.call('gate_browser_open', {'url': 'https://www.nanomape.com.br/'} )['http_status'], 200)
            server.links = [{'id': 0, 'url': 'https://www.nanomape.com.br/produtos'}]
            server.call('gate_browser_follow_link', {'id': 0})
            self.assertEqual(page.goto.call_args.args[0], 'https://www.nanomape.com.br/produtos')
            with self.assertRaises(ValueError):
                server.follow_link({'id': -1})

    def test_snapshot_reads_iframe_and_exposes_links(self):
        with tempfile.TemporaryDirectory() as folder:
            server = GateBrowserServer(Path(folder))
            page = Mock()
            page.is_closed.return_value = False
            page.url = 'https://example.org/'
            page.title.return_value = 'Página'
            frames = []
            for url, text in [('https://example.org/', 'Cabeçalho'), ('https://example.org/embed', 'NanoPasto Carbon')]:
                frame = Mock()
                frame.url = url
                frame.locator.return_value.inner_text.return_value = text
                frame.locator.return_value.evaluate_all.return_value = [{'text': 'Saiba mais', 'url': 'https://example.org/produtos'}]
                frames.append(frame)
            page.frames = frames
            server.page = page
            result = server.snapshot({})
            self.assertIn('NanoPasto Carbon', result['text'])
            self.assertEqual(len(result['frames']), 2)
            self.assertEqual(result['links'][0]['url'], 'https://example.org/produtos')

    def test_failure_is_diagnosed_without_query_secrets(self):
        with tempfile.TemporaryDirectory() as folder:
            server = GateBrowserServer(Path(folder))
            server._ensure_page = Mock(side_effect=OSError('browser executable missing'))
            with self.assertRaisesRegex(RuntimeError, 'não comprova indisponibilidade'):
                server.call('gate_browser_open', {'url': 'https://example.org/?token=secret'})
            log = (Path(folder) / '.codex-model-gate/browser-diagnostics.jsonl').read_text(encoding='utf-8')
            self.assertNotIn('secret', log)
            self.assertEqual(json.loads(log)['error_type'], 'OSError')

    def test_rejects_non_web_navigation_and_credentials(self):
        with tempfile.TemporaryDirectory() as folder:
            server = GateBrowserServer(Path(folder))
            for url in ['file:///C:/secret', 'javascript:alert(1)', 'https://user:secret@example.org/']:
                with self.assertRaises(ValueError):
                    server.open({'url': url})

    def test_site_request_enables_live_web_without_selected_skill(self):
        for task in ['Entre no site www.nanomape.com.br', 'Tente acessar o site agora.', 'Leia https://example.org/']:
            self.assertTrue(gate.needs_live_web_search(task, []))
        self.assertFalse(gate.needs_live_web_search('Some 2 e 3.', []))

    def test_preparation_exposes_browser_when_web_is_enabled(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config = AuthorizedTask('id', 'Consultar site', root, 'terra', 'medium',
                                    'equilibrada', (), False, True, '')
            with patch.object(gate, 'execution_workspace', return_value=root), \
                    patch.object(gate, 'remember_workspace'), \
                    patch.object(gate, 'stage_attachments', return_value=[]), \
                    patch.object(gate, 'skill_fingerprints', return_value=[]), \
                    patch.object(gate, 'selected_skill_instructions', return_value=''):
                prepared = prepare_task(config, [], 'codex', Mock(is_set=Mock(return_value=False)))
            self.assertIn('mcp_servers.gate_browser.required=true', '\n'.join(prepared[4]))

    def test_report_includes_browser_failure_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            server = GateBrowserServer(Path(folder))
            server._ensure_page = Mock(side_effect=OSError('net::ERR_NETWORK_ACCESS_DENIED'))
            with self.assertRaises(RuntimeError):
                server.call('gate_browser_open', {'url': 'https://example.org/'})
            rows = gate.read_browser_diagnostics(folder)
            self.assertEqual(rows[0]['error_code'], 'net::ERR_NETWORK_ACCESS_DENIED')
            rendered = gate._record_markdown({'browser_diagnostics': rows})
            self.assertIn('ERR_NETWORK_ACCESS_DENIED', rendered)


if __name__ == '__main__':
    unittest.main()
