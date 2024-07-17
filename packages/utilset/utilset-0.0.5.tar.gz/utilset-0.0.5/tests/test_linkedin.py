import unittest

from utilset import linkedin


class TestLinkedin(unittest.TestCase):

    def test_get_vanity_from_linkedin_url(self):
        url = 'https://www.linkedin.com/in/williamhgates/'
        self.assertEqual('williamhgates',
                         linkedin.get_vanity_from_linkedin_url(url))

    def test_get_vanity_from_linkedin_url(self):
        url = 'https://www.linkedin.com/comm/in/williamhgates'
        self.assertEqual('williamhgates',
                         linkedin.get_vanity_from_linkedin_url(url))

    def test_get_company_vanity_from_linkedin_url(self):
        url = 'http://www.linkedin.com/company/williamhgates/'
        self.assertEqual('williamhgates',
                         linkedin.get_company_vanity_from_linkedin_url(url))
        url = 'linkedin.com/company/williamhgates/'
        self.assertEqual('williamhgates',
                         linkedin.get_company_vanity_from_linkedin_url(url))


if __name__ == '__main__':
    unittest.main()