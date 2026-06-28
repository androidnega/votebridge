from django.http.request import validate_host
from django.test import SimpleTestCase

from config.settings.allowed_hosts import parse_allowed_hosts


class ParseAllowedHostsTests(SimpleTestCase):
    def test_production_mode_excludes_cloudflare_suffixes(self):
        hosts = parse_allowed_hosts(["votebridge.example.com"], debug=False)
        self.assertEqual(hosts, ["votebridge.example.com"])
        self.assertFalse(validate_host("abc.trycloudflare.com", hosts))

    def test_debug_mode_allows_cloudflare_quick_tunnel_subdomains(self):
        hosts = parse_allowed_hosts([], debug=True, include_local_defaults=True)
        self.assertIn(".trycloudflare.com", hosts)
        self.assertTrue(validate_host("random-name.trycloudflare.com", hosts))

    def test_localhost_still_allowed_in_development(self):
        hosts = parse_allowed_hosts([], debug=True, include_local_defaults=True)
        self.assertTrue(validate_host("localhost", hosts))
        self.assertTrue(validate_host("127.0.0.1", hosts))

    def test_wildcard_env_entry_is_normalized(self):
        hosts = parse_allowed_hosts(["*.trycloudflare.com"], debug=False)
        self.assertEqual(hosts, [".trycloudflare.com"])
        self.assertTrue(validate_host("demo.trycloudflare.com", hosts))

    def test_env_hosts_are_merged_with_dev_defaults(self):
        hosts = parse_allowed_hosts(
            ["my-dev.test"],
            debug=True,
            include_local_defaults=True,
        )
        self.assertIn("my-dev.test", hosts)
        self.assertIn("localhost", hosts)
        self.assertIn(".trycloudflare.com", hosts)
