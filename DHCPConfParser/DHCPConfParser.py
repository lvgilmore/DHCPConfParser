#! /usr/bin/python2.7

"""
@author: Geiger
@created: 13/09/2016
"""
from ipaddr import IPv4Network
from re import split
from re import sub


class DHCPConfParser(object):
    """help class to pars the dhcpd.conf file"""

    def __init__(self, conffile=None):
        """:param conffile: either a file or a file path """
        if isinstance(conffile, file):
            self.conffile = conffile
        elif isinstance(conffile, str):
            self.conffile = open(conffile)
        elif conffile is not None:
            raise TypeError("unexpected type " + str(conffile.__class__))

        self.globals = {}
        self.subnets = {}
        self.hosts = {}
        self.groups = {}
        self.shared_nets = {}

    def parse(self):
        confs = self._preformat()
        while confs.__len__() > 0:
            conf = confs[0]
            assert isinstance(conf, str)
            if conf.startswith('shared-network'):
                k, v = DHCPConfParser._parse_shared_network(confs)
                self.shared_nets[k] = v
            elif conf.startswith('subnet'):
                k, v = DHCPConfParser._parse_subnet(confs)
                self.subnets[k] = v
            elif conf.startswith('host'):
                k, v = DHCPConfParser._parse_host(confs)
                self.hosts[k] = v
            elif conf.startswith('group'):
                k, v = DHCPConfParser._parse_group(confs)
                self.groups[k] = v
            elif conf.startswith('{') or conf.startswith('}'):
                raise ParseError(
                    "unexpected word while parsing {}: {}".format(
                        str(self.conffile), conf))
            else:
                k, v = DHCPConfParser._parse_option(confs)
                self.globals[k] = v

    def _preformat(self):
        raw_conf = split('(\n|\{|\}|;)', self.conffile.read())
        for index, content in enumerate(raw_conf):
            raw_conf[index] = sub('#.*$', '', content)
            raw_conf[index] = sub('^\s+', '', raw_conf[index])
            raw_conf[index] = sub('\s+$', '', raw_conf[index])
        # clean empty entries
        try:
            while True:
                raw_conf.pop(raw_conf.index(''))
        except ValueError:
            pass
        return raw_conf

    @staticmethod
    def _parse_shared_network(confs):
        assert isinstance(confs[0], str) \
            and confs[0].startswith('shared-network') \
            and confs[1] == '{'
        shared_name = confs.pop(0).split()[1]
        shared_net = {'subnets': {},
                      'hosts': {},
                      'groups': {},
                      'options': {},
                      }
        confs.pop(0)
        while confs[0] != '}':
            if confs[0].startswith('subnet'):
                k, v = DHCPConfParser._parse_subnet(confs)
                shared_net['subnets'][k] = v
            elif confs[0].startswith('host'):
                k, v = DHCPConfParser._parse_host(confs)
                shared_net['hosts'][k] = v
            elif confs[0].startswith('group'):
                k, v = DHCPConfParser._parse_group(confs)
                shared_net['groups'][k] = v
            else:
                k, v = DHCPConfParser._parse_option(confs)
                shared_net['options'][k] = v
        confs.pop(0)
        return shared_name, shared_net

    @staticmethod
    def _parse_subnet(confs):
        assert isinstance(confs[0], str) \
            and confs[0].startswith('subnet') \
            and confs[1] == '{'
        subnet_ip = IPv4Network("{}/{}".format(
            confs[0].split()[1], confs[0].split()[3]))
        subnet = {'hosts': {},
                  'groups': {},
                  'options': {},
                  }
        confs.pop(0)
        confs.pop(0)
        while confs[0] != '}':
            if confs[0].startswith('host'):
                k, v = DHCPConfParser._parse_host(confs)
                subnet['hosts'][k] = v
            elif confs[0].startswith('group'):
                k, v = DHCPConfParser._parse_group(confs)
                subnet['groups'][k] = v
            else:
                k, v = DHCPConfParser._parse_option(confs)
                subnet['options'][k] = v
        confs.pop(0)
        return subnet_ip, subnet

    @staticmethod
    def _parse_host(confs):
        assert isinstance(confs[0], str) \
            and confs[0].startswith('host') \
            and confs[1] == '{'
        host_name = confs.pop(0).split()[1]
        host = {'options': {}}
        confs.pop(0)
        while confs[0] != '}':
            k, v = DHCPConfParser._parse_option(confs)
            host['options'][k] = v
        confs.pop(0)
        return host_name, host

    @staticmethod
    def _parse_option(confs):
        try:
            if confs[1] != ';':
                raise ParseError(
                    "expected separator ; after conf {}".format(confs[0]))
        except IndexError:
            raise IndexError("ended unexpectedly. expected ;")

        raw_option = confs.pop(0).split()
        if raw_option[0] in ["option"]:
            option_name = "{} {}".format(raw_option.pop(0), raw_option.pop(0))
        else:
            option_name = raw_option.pop(0)
        if raw_option.__len__() == 1:
            option = raw_option.pop(0)
        else:
            option = raw_option
        confs.pop(0)
        return option_name, option

    @staticmethod
    def _parse_group(confs):
        assert isinstance(confs[0], str) \
            and confs[0].startswith('group') \
            and confs[1] == '{'
        group_name = confs.pop(0).split()[1]
        group = {'subnets': {},
                 'hosts': {},
                 'shared-networks': {},
                 'options': {},
                 'groups': {},
                 }
        confs.pop(0)
        while confs[0] != '}':
            if confs[0].startswith('subnet'):
                k, v = DHCPConfParser._parse_subnet(confs)
                group['subnets'][k] = v
            elif confs[0].startswith('host'):
                k, v = DHCPConfParser._parse_host(confs)
                group['hosts'][k] = v
            elif confs[0].startswith('shared-network'):
                k, v = DHCPConfParser._parse_shared_network(confs)
                group['shared-networks'][k] = v
            elif confs[0].startswith('group'):
                k, v = DHCPConfParser._parse_group(confs)
                group['groups'][k] = v
            else:
                k, v = DHCPConfParser._parse_option(confs)
                group['options'][k] = v
        confs.pop(0)
        return group_name, group


class ParseError(Exception):
    pass


if __name__ == "__main__":
    parser = DHCPConfParser(conffile="../../resources/dhcp-example.conf")
    parser.parse()
    print(parser.globals)
    print(parser.groups)
    print(parser.hosts)
    print(parser.shared_nets)
    print(parser.subnets)
