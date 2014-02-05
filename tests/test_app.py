from nose.tools import raises, with_setup
import datetime
import unittest
from tornado.testing import AsyncHTTPTestCase

import application

class GISMOH_App_Test(AsyncHTTPTestCase):
    def get_app(self):
        return application.init_app()

    def test_homepage(self):
        self.http_client.fetch(self.get_url('/'), self.stop)
        response = self.wait()
        assert response.code == 200

    def test_antibiogram(self):
        self.http_client.fetch(self.get_url('/api/antibiogram'), self.stop)
        response = self.wait()
        assert response.code == 200

    def test_locations(self):
        self.http_client.fetch(self.get_url('/api/locations'), self.stop)
        response = self.wait()
        assert response.code == 200

    def test_overlaps(self):
        self.http_client.fetch(self.get_url('/api/overlaps'), self.stop)
        response = self.wait()
        assert response.code == 200

    def test_risk_and_positive(self):
        self.http_client.fetch(self.get_url('/api/risk_patients'), self.stop)
        response = self.wait()
        assert response.code == 200

    def test_isolates(self):
        self.http_client.fetch(self.get_url('/api/isolates'), self.stop)
        response = self.wait()

        assert response.code == 200

