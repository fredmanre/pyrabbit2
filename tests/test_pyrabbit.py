import json

try:
    #python 2.x
    import unittest2 as unittest
except ImportError:
    #python 3.x
    import unittest

import sys
sys.path.append('..')
import pyrabbit
import mock

# used by Server init
test_overview_dict = {'node': 'bar', 
            'management_version': '2.4.1',
            'queue_totals': 'rrrr',
            'listeners': 'ssss',
            'statistics_db_node': 'tttt',
            'message_stats': 'uuuu',
            'statistics_level': 'vvvv'}

test_vhosts_dict = [{'name': '/'}]

test_q_all = json.loads('[{"memory":12248,"messages":0,"consumer_details":[],"idle_since":"2011-5-27 15:17:35","exclusive_consumer_pid":"","exclusive_consumer_tag":"","messages_ready":0,"messages_unacknowledged":0,"messages":0,"consumers":0,"backing_queue_status":{"q1":0,"q2":0,"delta":["delta","undefined",0,"undefined"],"q3":0,"q4":0,"len":0,"pending_acks":0,"outstanding_txns":0,"target_ram_count":"infinity","ram_msg_count":0,"ram_ack_count":0,"ram_index_count":0,"next_seq_id":0,"persistent_count":0,"avg_ingress_rate":0.0,"avg_egress_rate":0.0,"avg_ack_ingress_rate":0.0,"avg_ack_egress_rate":0.0},"name":"testq","vhost":"/","durable":true,"auto_delete":false,"owner_pid":"none","arguments":{},"pid":"<rabbit@newhotness.3.225.0>","node":"rabbit@newhotness"}]')

class TestHTTPClient(unittest.TestCase):
    """
    Except for the init test, these are largely functional tests that
    require a RabbitMQ management API to be available on localhost:55672

    """
    def setUp(self):
        self.c = pyrabbit.api.HTTPClient('localhost:55672', 'guest', 'guest')

    def test_client_init(self):
        c = pyrabbit.api.HTTPClient('localhost:55672', 'guest', 'guest')
        self.assertIsInstance(c, pyrabbit.api.HTTPClient)

    def test_is_alive(self):
        self.assertTrue(self.c.is_alive())

    def test_is_not_alive(self):
        """
        If your vhost isn't found, RabbitMQ throws a 404. This is mapped to
        a more readable exception message in HTTPClient saying the vhost
        doesn't exist.

        """
        with self.assertRaises(pyrabbit.api.APIError):
            self.c.is_alive('somenonexistentvhost')

    def test_overview_500(self):
        """
        Insures that if the broker is down, the pyrabbit.api.NetworkError gets
        raised.

        """
        c = pyrabbit.api.HTTPClient('webstatuscodes.appspot.com/500',
                                    'guest', 'guest')
        with self.assertRaises(pyrabbit.api.HTTPError) as ctx:
            c.get_overview()

        self.assertEqual(ctx.exception.status, 500)

    def test_get_overview(self):
        overview = self.c.get_overview()
        self.assertIsInstance(overview, dict)

    def test_get_all_vhosts(self):
        vhosts = self.c.get_all_vhosts()
        self.assertIsInstance(vhosts, list)

    def test_get_all_queues(self):
        queues = self.c.get_queues()
        self.assertIsInstance(queues, list)

    def test_get_queues_for_vhost(self):
        queues = self.c.get_queues('testvhost')
        self.assertIsInstance(queues, list)

    def test_get_all_exchanges(self):
        xchs = self.c.get_exchanges()
        self.assertIsInstance(xchs, list)

    def test_get_exchanges_by_vhost(self):
        xchs = self.c.get_exchanges('testvhost')
        self.assertIsInstance(xchs, list)


class TestServer(unittest.TestCase):
    def test_server_init_200(self):
        with mock.patch('pyrabbit.api.HTTPClient', spec=True) as httpmock:
            inst = httpmock.return_value
            inst.get_overview.return_value = test_overview_dict

            srvr = pyrabbit.api.Server('localhost:55672', 'guest', 'guest')

            self.assertIsInstance(srvr, pyrabbit.api.Server)
            self.assertTrue(all(x in srvr.__dict__.values() for x in \
                                        test_overview_dict.values()))
            self.assertEqual(srvr.host, 'localhost:55672')

    def test_server_is_alive_default_vhost(self):
        with mock.patch('pyrabbit.api.HTTPClient', spec=True) as httpmock:
            httpmock.return_value.get_overview.return_value = test_overview_dict
            httpmock.return_value.is_alive.return_value = True

            srvr = pyrabbit.api.Server('localhost:55672', 'guest', 'guest')

            self.assertTrue(srvr.is_alive())

    def test_get_vhosts_200(self):
        with mock.patch('pyrabbit.api.HTTPClient', spec=True) as httpmock:
            httpmock.return_value.get_overview.return_value = test_overview_dict
            httpmock.return_value.get_all_vhosts.return_value = test_vhosts_dict

            srvr = pyrabbit.api.Server('localhost:55672', 'guest', 'guest')
            vhosts = srvr.get_all_vhosts()

            self.assertIsInstance(vhosts, list)

    def test_get_all_queues(self):
        with mock.patch('pyrabbit.api.HTTPClient', spec=True) as httpmock:
            httpmock.return_value.get_overview.return_value = test_overview_dict
            httpmock.return_value.get_queues.return_value = test_q_all

            srvr = pyrabbit.api.Server('localhost:55672', 'guest', 'guest')
            queues = srvr.get_queues()

            self.assertIsInstance(queues, list)


class TestExchange(unittest.TestCase):
    def test_exch_init(self):
        xch = pyrabbit.exchanges.Exchange('test')
        self.assertIsInstance(xch, pyrabbit.exchanges.Exchange)
        self.assertEqual(xch.name, 'test')
    

class TestQueue(unittest.TestCase):
    def test_queue_init(self):
        qu = pyrabbit.queues.Queue('testq')
        self.assertIsInstance(qu, pyrabbit.queues.Queue)
        self.assertEqual(qu.name, 'testq')

