
import unittest
from mock import Mock

from pyramid import testing


class TestCase(unittest.TestCase):
    """
    Base class for all test suites.
    """

    def setUp(self):
        self.config = testing.setUp()
        # TODO: this probably shouldn't (need to) be here
        self.config.add_directive('add_tailbone_permission_group', 'tailbone.auth.add_permission_group')
        self.config.add_directive('add_tailbone_permission', 'tailbone.auth.add_permission')

    def tearDown(self):
        testing.tearDown()


def mock_query():
    """
    Mock object used to simulate a ``sqlalchemy.Query`` instance.
    """

    query = Mock()
    query.return_value = query
    query.outerjoin.return_value = query
    query.join.return_value = query
    query.filter.return_value = query
    query.distinct.return_value = query
    query.order_by.return_value = query
    return query
