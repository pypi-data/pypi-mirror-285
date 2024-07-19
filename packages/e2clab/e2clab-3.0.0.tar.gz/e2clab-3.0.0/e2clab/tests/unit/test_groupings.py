from enoslib import Host

import e2clab.grouping as e2cgrp
from e2clab.tests.unit import TestE2cLab


class TestGrouping(TestE2cLab):

    def test_get_grouping(self):
        with self.assertRaises(KeyError):
            e2cgrp.get_grouping_class("notagrouping")

        grp_class = e2cgrp.get_grouping_class("asarray")
        self.assertIs(grp_class, e2cgrp.Asarray)

    def test_address_match(self):
        # Testing "AddressMatch"
        prefix = "_self"
        serv_extra_info = [
            {"__address__": "1.2.3.4", "__port__": "80"},
            {"__address__": "5.6.7.8", "__port__": "81"},
        ]
        hosts = [Host("1.2.3.4"), Host("5.6.7.8", extra={prefix: {"misc": "hello"}})]
        grouping = e2cgrp.get_grouping("address_match", hosts, prefix, serv_extra_info)

        self.assertIsInstance(grouping, e2cgrp.AddressMatch)

        new_hosts = grouping.distribute()
        self.assertEqual(new_hosts[0].extra[prefix]["__port__"], "80")
        self.assertEqual(new_hosts[1].extra[prefix]["__port__"], "81")

    def test_round_robin(self):
        # Testing RoudRobin
        prefix = "server"
        hosts = [
            Host("1.2.3.4"),
            Host("5.6.7.8", extra={prefix: {"misc": "hello"}}),
            Host("9.9.9.9"),
            Host("8.8.8.8"),
        ]
        serv_extra_info = [
            {"__address__": "1.1.1.1"},
            {"__address__": "2.2.2.2"},
        ]
        grouping = e2cgrp.get_grouping("round_robin", hosts, prefix, serv_extra_info)
        self.assertIsInstance(grouping, e2cgrp.RoundRobin)

        new_hosts = grouping.distribute()
        self.assertEqual(len(new_hosts), 4)
        self.assertEqual(new_hosts[0].extra[prefix]["__address__"], "1.1.1.1")
        self.assertEqual(new_hosts[1].extra[prefix]["__address__"], "2.2.2.2")
        self.assertEqual(new_hosts[2].extra[prefix]["__address__"], "1.1.1.1")
        self.assertEqual(new_hosts[3].extra[prefix]["__address__"], "2.2.2.2")

    def test_asarray(self):
        # Testing Asarray
        prefix = "server"
        hosts = [
            Host("1.2.3.4"),
            Host("5.6.7.8", extra={prefix: {"misc": "hello"}}),
            Host("9.9.9.9"),
            Host("8.8.8.8"),
        ]
        serv_extra_info = [
            {"_id": "1_1"},
            {"_id": "1_2"},
            {"_id": "2_1"},
            {"_id": "2_2"},
        ]
        grouping = e2cgrp.get_grouping("asarray", hosts, prefix, serv_extra_info)
        self.assertIsInstance(grouping, e2cgrp.Asarray)

        new_hosts = grouping.distribute()
        self.assertEqual(len(new_hosts), 4)
        for host in new_hosts:
            self.assertEqual(host.extra[prefix][0], "11")
            self.assertEqual(host.extra[prefix][1], "12")
            self.assertEqual(host.extra[prefix][2], "21")
            self.assertEqual(host.extra[prefix][3], "22")

    def test_aggregate(self):
        # Testing Aggregate
        prefix = "server"
        hosts = [
            Host("1.2.3.4"),
            Host("5.6.7.8", extra={f"{prefix}1_1": {"misc": "hello"}}),
            Host("9.9.9.9"),
            Host("8.8.8.8"),
        ]
        service_extra_info = [
            {"_id": "1_1_1", "port": "80"},
            {"_id": "1_1_2", "port": "81"},
            {"_id": "1_2_1", "port": "82"},
            {"_id": "1_2_2", "port": "83"},
        ]
        grouping = e2cgrp.get_grouping("aggregate", hosts, prefix, service_extra_info)
        self.assertIsInstance(grouping, e2cgrp.Aggregate)

        new_hosts = grouping.distribute()
        self.assertEqual(len(new_hosts), 4)
        for host in new_hosts:
            self.assertEqual(host.extra["server1_1"]["port"], "80")
            self.assertEqual(host.extra["server1_2"]["port"], "81")
            self.assertEqual(host.extra["server2_1"]["port"], "82")
            self.assertEqual(host.extra["server2_2"]["port"], "83")
        self.assertEqual(new_hosts[1].extra["server1_1"]["misc"], "hello")

        wrong_info = [{"_id": "1_1"}]
        grouping = e2cgrp.get_grouping("aggregate", hosts, prefix, wrong_info)
        with self.assertRaises(Exception):
            grouping.distribute()
