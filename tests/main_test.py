# Tests using pytest
from __future__ import absolute_import
from __future__ import unicode_literals

import os
from multiprocessing import Process

from pyentrypoint.entrypoint import main


class ProxyMain(object):

    def __init__(self, args, env):

        self.args = args
        self.env = env

    def run(self):
        for key, val in self.env.items():
            os.environ[key] = val
        main(self.args)


def test_main():
    run = [
        #  ((Process instance), (file to check), (uid), (gid))
        (
            Process(target=ProxyMain(
                args=['pyentrypoint', '-c', 'echo OK > /tmp/CMD6'],
                env={'ENTRYPOINT_CONFIG': 'configs/base.yml'}
            ).run),
            '/tmp/CMD6',
            1000,
            1000,
        ), (
            Process(target=ProxyMain(
                args=['pyentrypoint',
                      'bash',
                      '-c',
                      'echo ${SECRET}OK > /tmp/CMD7'],
                env={'ENTRYPOINT_CONFIG': 'configs/base.yml'}
            ).run),
            '/tmp/CMD7',
            1000,
            1000,
        ), (
            Process(target=ProxyMain(
                args=['pyentrypoint', 'bash', '-c', 'echo OK > /tmp/CMD8'],
                env={'ENTRYPOINT_CONFIG': 'configs/usernames.yml'}
            ).run),
            '/tmp/CMD8',
            33,
            33,
        ), (
            Process(target=ProxyMain(
                args=['pyentrypoint', 'bash', '-c', 'echo OK > /tmp/CMD9'],
                env={'ENTRYPOINT_CONFIG': 'configs/unhandled.yml'}
            ).run),
            '/tmp/CMD9',
            0,
            0,
        ), (
            Process(target=ProxyMain(
                args=['pyentrypoint', 'bash', '-c', 'echo OK > /tmp/CMD10'],
                env={'ENTRYPOINT_CONFIG': 'configs/unhandled_force.yml',
                     'ENTRYPOINT_FORCE': 'true'}
            ).run),
            '/tmp/CMD_FORCE',
            0,
            0,
        ), (
            Process(target=ProxyMain(
                args=['pyentrypoint', 'bash', '-c', 'echo OK > /tmp/CMD11'],
                env={'ENTRYPOINT_CONFIG': '/dontexist'}
            ).run),
            '/tmp/CMD11',
            0,
            0,
        )
    ]

    for proc, test, uid, gid in run:
        proc.start()
        proc.join()
        with open(test) as f:
            assert f.readline().startswith('OK')
        assert os.stat(test).st_uid == uid
        assert os.stat(test).st_gid == gid