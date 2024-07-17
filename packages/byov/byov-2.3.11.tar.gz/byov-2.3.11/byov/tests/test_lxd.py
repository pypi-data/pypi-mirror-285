# This file is part of Build Your Own Virtual machine.
#
# Copyright 2018 Vincent Ladeuil.
# Copyright 2015, 2016, 2017 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3, as published by the
# Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals

import errno
import io
import os
import unittest

from byot import scenarii
from byov import (
    commands,
    config,
    errors,
    subprocesses,
)
from byov.tests import (
    features,
    fixtures,
)
from byov.vms import lxd

load_tests = scenarii.load_tests_with_scenarios


def lxd_config_get(vm_name, option):
    config_command = ['lxc', 'config', 'get', vm_name, option]
    return subprocesses.run(config_command)


@features.requires(features.lxd_client_feature)
class TestConfig(unittest.TestCase):

    def setUp(self):
        super(TestConfig, self).setUp()
        fixtures.setup_tests_config(self)
        fixtures.set_uniq_vm_name(self)
        # Create a shared config
        conf = config.VmStack(None)
        conf.set('vm.class', 'lxd')
        conf.store.save()
        conf.store.unload()

    def test_autostart(self):
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        # A real test requires rebooting the host, we just check the default
        # value is the same as lxd itself.
        self.assertEqual(False, vm.conf.get('lxd.config.boot.autostart'))


@features.requires(features.lxd_client_feature)
class TestInit(unittest.TestCase):

    def setUp(self):
        super(TestInit, self).setUp()
        fixtures.setup_tests_config(self)
        fixtures.set_uniq_vm_name(self)
        # Create a shared config
        conf = config.VmStack(self.vm_name)
        conf.set('vm.class', 'lxd')
        conf.store.save()
        conf.store.unload()

    def test_unknown_image(self):
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        vm.conf.set('vm.release', 'Idontexist')
        vm.conf.set('vm.architecture', 'amd64')
        with self.assertRaises(errors.CommandError) as cm:
            vm.init()
        # The error message has changed:
        # 2.0: The requested image couldn't be found.
        # 2.5: Couldn't find the requested image
        self.assertIn('he requested image', cm.exception.err)

    def test_memory(self):
        fixtures.override_logging(self)
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        vm.conf.set('vm.architecture', 'amd64')
        vm.conf.set('vm.ram_size', '12')
        self.addCleanup(vm.teardown)
        ret, out, err = vm.init()
        self.assertEqual(0, ret)
        self.assertTrue(out.startswith(('Creating {}\n'.format(
            vm.conf.get('vm.name')))))
        log = self.log_stream.getvalue()
        self.assertTrue('--config limits.memory=12MB' in log, log)
        self.assertEqual('', err)

    def test_known_image(self):
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        vm.conf.set('vm.architecture', 'amd64')
        self.addCleanup(vm.teardown)
        ret, out, err = vm.init()
        self.assertEqual(0, ret)
        self.assertTrue(out.startswith(('Creating {}\n'.format(
            vm.conf.get('vm.name')))))
        self.assertEqual('', err)

    @features.requires(features.lxd_client_feature)
    def test_bad_nesting_config(self):
        lxc_version = features.lxd_client_feature.version
        if lxc_version[0] == '3':
            self.skipTest('Lxd {} needs to support nesting'.format(
                '.'.join(lxc_version)))
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        # Short of installing testing /etc/sub[ug]id files, using an insane
        # level of nesting.
        vm.conf.set('lxd.nesting', '1024')
        vm.conf.set('vm.architecture', 'amd64')
        with self.assertRaises(errors.ByovError) as cm:
            vm.init()
        self.assertEqual('Lxd needs more ids for 1024 levels of nesting',
                         str(cm.exception))


# FIXME: parametrized by distribution ? -- vila 2017-12-06
@features.requires(features.lxd_client_feature)
class TestSetup(unittest.TestCase):

    def setUp(self):
        super(TestSetup, self).setUp()
        fixtures.setup_tests_config(self)
        fixtures.set_uniq_vm_name(self)
        # Create a shared config
        conf = config.VmStack(self.vm_name)
        conf.set('vm.name', self.vm_name)
        conf.set('vm.class', 'lxd')
        conf.set('vm.architecture', 'amd64')
        conf.store.save()
        conf.store.unload()
        fixtures.override_logging(self)

    def test_usable(self):
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        self.addCleanup(vm.teardown)
        self.addCleanup(vm.stop)
        vm.setup()
        # We should be able to ssh with the right user
        ret, out, err = vm.shell_captured('whoami')
        self.assertEqual(0, ret)
        self.assertEqual(vm.conf.get('vm.user') + '\n', out)
        # By default, nesting is not set
        ret, out, err = lxd_config_get(self.vm_name, 'security.nesting')
        self.assertEqual(0, ret)
        self.assertEqual('\n', out)
        self.assertEqual('', err)
        # Nor is lxd.remote
        self.assertIs(None, vm.econf.get('lxd.remote'))

    def test_normal_user(self):
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        vm.conf.set('vm.user', 'tester')
        self.addCleanup(vm.teardown)
        self.addCleanup(vm.stop)
        vm.setup()
        # We should be able to ssh with the right user
        ret, out, err = vm.shell_captured('whoami')
        self.assertEqual(0, ret)
        self.assertEqual(vm.conf.get('vm.user') + '\n', out)
        # And sudo
        ret, out, err = vm.shell_captured('sudo whoami')
        self.assertEqual(0, ret)
        self.assertEqual('root\n', out)

    def test_user_homedir(self):
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        vm.conf.set('vm.user', 'systester')
        vm.conf.set('vm.user.home', '/systester')
        self.addCleanup(vm.teardown)
        self.addCleanup(vm.stop)
        vm.setup()
        # We should be able to ssh with the right user
        ret, out, err = vm.shell_captured('whoami')
        self.assertEqual(0, ret)
        self.assertEqual(vm.conf.get('vm.user') + '\n', out)
        # In the right place
        ret, out, err = vm.shell_captured('pwd')
        self.assertEqual(0, ret)
        self.assertEqual('/systester\n', out)

    def test_nesting(self):
        lxc_version = features.lxd_client_feature.version
        # FIXME: Revisit the test below once we get a better view of the
        # supported distribution/releases -- vila 2024-07-15
        if lxc_version[0] == '3':
            self.skipTest('Lxd {} needs to support nesting'.format(
                '.'.join(lxc_version)))
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        vm.conf.set('lxd.nesting', '1')
        self.addCleanup(vm.teardown)
        self.addCleanup(vm.stop)
        vm.setup()
        ret, out, err = lxd_config_get(self.vm_name, 'security.nesting')
        self.assertEqual(0, ret)
        self.assertEqual('True\n', out)
        self.assertEqual('', err)

    # MISSINGTEST: What happens if two vms use the same hwaddr at the same time
    # (or not) ? -- vila 2018-04-23
    def test_hwaddr(self):
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        vm.setup()
        # FIXME: Can we do better than eth0 ? -- vila 2018-04-24
        ret, out, err = lxd_config_get(self.vm_name, 'volatile.eth0.hwaddr')
        self.assertEqual(0, ret)
        self.assertEqual('', err)
        hwaddr = out.strip()
        ip = vm.conf.get('vm.ip')
        vm.teardown(True)
        # Arguably this can fail if the mac address is assigned by lxd to a
        # different container.
        vm.conf.set('lxd.mac.address', hwaddr)
        self.addCleanup(vm.teardown, True)
        vm.setup()
        # FIXME: The test has failed with: AssertionError: '10.242.247.98' !=
        # '10.242.247.99'. I.e. at least thrice, lxd failed to delivered the
        # same IP twice (root cause not understood yet) -- vila 2019-11-15
        self.assertEqual(ip, vm.conf.get('vm.ip'))


# FIXME: parametrized by distribution ? -- vila 2017-12-06
@features.requires(features.lxd_client_feature)
class TestMounts(unittest.TestCase):

    scenarios = [(k, dict(mount_name=k, out_dir=out_dir)) for k, out_dir in
                 (('absolute', 'testing'),
                  ('relative', 'testing'),
                  ('homedir', 'home/testing'),
                  )]

    def setUp(self):
        super().setUp()
        fixtures.setup_tests_config(self)
        fixtures.set_uniq_vm_name(self)
        # Create a shared config
        conf = config.VmStack(self.vm_name)
        conf.set('vm.name', self.vm_name)
        conf.set('vm.class', 'lxd')
        conf.set('vm.architecture', 'amd64')
        conf.store.save()
        conf.store.unload()
        fixtures.override_logging(self)
        # In at least one case (using self.uniq_dir), we need the test object
        # to be created to define more attributes. Those attributes can't be
        # provided by the scenario so they have to be defined later (aka, here
        # and now).
        if (self.mount_name == 'absolute'):
            self.mnt_opt = self.uniq_dir + '/testing:/home/{vm.user}/testing'
        elif (self.mount_name == 'relative'):
            self.mnt_opt = 'testing:/home/{vm.user}/testing'
        elif (self.mount_name == 'homedir'):
            self.mnt_opt = '~/testing:/home/{vm.user}/testing'
        else:
            self.fail(self.mount_name + ' is not a known scenario')
        self.vm = lxd.Lxd(config.VmStack(self.vm_name))
        os.mkdir(self.out_dir)
        self.vm.conf.set('lxd.user_mounts', self.mnt_opt)
        self.addCleanup(self.vm.teardown)
        self.addCleanup(self.vm.stop)
        self.vm.setup()

    def test_vm_changes_seen_from_host(self):
        ret, out, err = self.vm.shell_captured('touch testing/inside')
        self.assertEqual(0, ret)
        self.assertEqual('', out)
        self.assertEqual('', err)
        # The file is seen from the host
        self.assertTrue(os.path.exists(self.out_dir + '/inside'))


# FIXME: parametrized by distribution ? -- vila 2017-12-06
@features.requires(features.lxd_client_feature)
class TestIdMap(unittest.TestCase):

    def setUp(self):
        super().setUp()
        fixtures.setup_tests_config(self)
        fixtures.set_uniq_vm_name(self)
        # Create a shared config
        conf = config.VmStack(self.vm_name)
        conf.set('vm.name', self.vm_name)
        conf.set('vm.class', 'lxd')
        conf.set('vm.architecture', 'amd64')
        conf.store.save()
        conf.store.unload()
        fixtures.override_logging(self)
        self.vm = lxd.Lxd(config.VmStack(self.vm_name))

    def test_id_map_defaults(self):
        # The defaults are a bit ubuntu/debian specific (but they may also be
        # valid for other distros (we're not there yet)).
        # FIXME: This needs vm.user.id (defaults 1000). -- vila 2024-07-14
        # FIXME: This needs os.getuid() and os.getgid() rather than 1000, 1000
        # -- vila 2024-07-15
        self.assertEqual(('uid 1000 1000', 'gid 1000 1000'),
                         self.vm.get_mount_id_map())

    def test_id_map_unknown(self):
        self.vm.conf.set('lxd.idmap.path', '/IDontExist')
        with self.assertRaises(ValueError) as cm:
            self.vm.get_idmap_from_file(self.vm.conf.get('lxd.idmap.path'))
        self.assertEqual('/IDontExist does not exist', str(cm.exception))

    def test_id_map_passed(self):
        path = 'mymap'
        content = '''
# Comments are deleted and empty lines ignored
both 0 0
both 11 12
'''
        with open(path, 'w') as f:
            f.write(content)
        conf = self.vm.conf
        conf.set('lxd.idmap.path', path)
        mount_map = self.vm.get_idmap_from_file(conf.get('lxd.idmap.path'))
        self.assertEqual(['both 0 0', 'both 11 12'], mount_map)

    def test_id_map_expanded(self):
        path = 'mymap'
        content = '''
# Comments are deleted and empty lines ignored
# FIXME: This needs vm.user.id (defaults 1000). -- vila 2024-07-14
both 1000 1000 # {vm.user}
both 0 0 # root
'''
        with open(path, 'w') as f:
            f.write(content)
        conf = self.vm.conf
        conf.set('lxd.idmap.path', '@' + path)
        mount_map = self.vm.get_idmap_from_file(conf.get('lxd.idmap.path'))
        # FIXME: This needs vm.user.id (defaults 1000). -- vila 2024-07-14
        self.assertEqual(['both 1000 1000', 'both 0 0'], mount_map)
        os.mkdir('home/testing')
        conf.set('lxd.user_mounts', '~/testing:/home/{vm.user}/testing')
        self.addCleanup(self.vm.teardown)
        self.addCleanup(self.vm.stop)
        vmexp = conf.expand_options
        shell = self.vm.shell_captured
        self.vm.setup()
        cap = shell(vmexp('touch testing/{vm.user}'))
        self.assertEqual((0, '', ''), cap)
        cap = shell(vmexp('sudo touch ~{vm.user}/testing/root'))
        self.assertEqual((0, '', ''), cap)
        user_st = os.stat(vmexp('home/testing/{vm.user}'))
        root_st = os.stat(vmexp('home/testing/root'))
        # We've assumed uid 1000 in the idmap for the current user
        # FIXME: Dont assume, use os.getuid() ;-) -- vila 2024-07-15
        self.assertEqual(os.getuid(), user_st.st_uid)
        self.assertEqual(0, root_st.st_uid)


@features.requires(features.lxd_client_feature)
class TestCheckSubidsForMountsErrors(unittest.TestCase):
    """Test errors related to sub ids.

    Strictly speaking this should happen in a nested vm so we can change
    /etc/subuid and /ets/subgid. Doing it in the temp directory is easier.
    """
    def setUp(self):
        super(TestCheckSubidsForMountsErrors, self).setUp()
        fixtures.setup_tests_config(self)
        fixtures.set_uniq_vm_name(self)
        # Create a shared config
        conf = config.VmStack(self.vm_name)
        conf.set('vm.class', 'lxd')
        conf.set('vm.architecture', 'amd64')
        conf.set('lxd.user_mounts', '.:/work')
        conf.store.save()
        conf.store.unload()

    def create_ids(self, uids, gids):
        with open(os.path.join(self.etc_dir, 'subuid'), 'w') as f:
            f.write(uids)
        with open(os.path.join(self.etc_dir, 'subgid'), 'w') as f:
            f.write(gids)

    def test_root_cant_map_uid(self):
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        self.create_ids('', 'root:42:1')
        with self.assertRaises(errors.SubIdError) as cm:
            vm.check_subids_for_mounts(888, 0, self.etc_dir)
        self.assertEqual('uid', cm.exception.typ)
        self.assertEqual(888, cm.exception.subid)

    def test_root_cant_map_gid(self):
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        self.create_ids('root:888:1', 'root:42:1')
        with self.assertRaises(errors.SubIdError) as cm:
            vm.check_subids_for_mounts(888, 888, self.etc_dir)
        self.assertEqual('gid', cm.exception.typ)
        self.assertEqual(888, cm.exception.subid)

    def test_root_can_map(self):
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        self.create_ids('root:888:1', 'root:999:1')
        vm.check_subids_for_mounts(888, 999, self.etc_dir)


# FIXME: parametrized by distribution -- vila 2017-12-06
class TestEphemeralLXD(unittest.TestCase):

    def setUp(self):
        super(TestEphemeralLXD, self).setUp()
        fixtures.setup_tests_config(self)
        features.requires_existing_vm(self, 'byov-tests-lxd-debian')
        fixtures.set_uniq_vm_name(self)
        # Create a shared config
        conf = config.VmStack(self.vm_name)
        conf.set('vm.name', self.vm_name)
        conf.set('vm.class', 'ephemeral-lxd')
        conf.set('vm.backing', 'byov-tests-lxd-debian')
        conf.store.save()
        conf.store.unload()

    def test_start(self):
        vm = lxd.EphemeralLxd(config.VmStack(self.vm_name))
        self.addCleanup(vm.stop)
        vm.start()
        self.assertEqual('RUNNING', vm.state())

    def test_stop(self):
        vm = lxd.EphemeralLxd(config.VmStack(self.vm_name))

        def cleanup():
            # vm.start() may fail if no IP can't be acquired (for example). In
            # that case, the container runs and needs to be stopped. If the
            # test succeeds, the vm has already been stopped. This awkward
            # cleanup avoid leaks.
            if vm.state() == 'RUNNING':
                vm.stop()

        self.addCleanup(cleanup)
        vm.start()
        vm.stop()
        # There is a tiny window during which the container can be seen STOPPED
        # before being deleted
        self.assertIn(vm.state(), ('UNKNOWN', 'STOPPED'))

    def test_forbid_lxd_user_mounts_in_both(self):
        conf = config.VmStack('byov-tests-lxd-debian')
        conf.set('lxd.user_mounts', 'home:/work')
        conf.store.save()
        vm = lxd.EphemeralLxd(config.VmStack(self.vm_name))
        vm.conf.set('lxd.user_mounts', '.:/ephemeral')
        # If the backing container has specified lxd.user_mounts, the ephemeral
        # cannot.
        with self.assertRaises(errors.ByovError) as cm:
            vm.start()
        self.assertEqual(
            'Backing vm byov-tests-lxd-debian already has mounts',
            str(cm.exception))

    def test_ephemeral_mounts(self):
        vm = lxd.EphemeralLxd(config.VmStack(self.vm_name))
        os.mkdir('testing')
        vm.conf.set('lxd.user_mounts',
                    self.uniq_dir + '/testing:/home/{vm.user}/testing')
        self.addCleanup(vm.stop)
        vm.start()
        ret, out, err = vm.shell_captured('touch testing/inside')
        self.assertEqual(0, ret)
        self.assertEqual('', out)
        self.assertEqual('', err)
        # The file is seen from the host
        self.assertTrue(os.path.exists('testing/inside'))


class TestNextSubuids(unittest.TestCase):

    def setUp(self):
        super(TestNextSubuids, self).setUp()
        fixtures.isolate_from_disk(self)

    def assertIdRanges(self, expected, content):
        with open(os.path.join(self.etc_dir, 'subuid'), 'w') as f:
            f.write(content)
        self.assertEqual(expected, list(lxd.next_subids('uid', self.etc_dir)))

    def test_unknown(self):
        with self.assertRaises(IOError) as cm:
            list(lxd.next_subids('uid', self.etc_dir))
        # aka FileNotFound (python2 specific)
        self.assertEqual(2, cm.exception.args[0])
        self.assertEqual(errno.ENOENT, cm.exception.errno)

    def test_empty(self):
        self.assertIdRanges([], '')
        self.assertIdRanges([], '\n\n')

    def test_garbage(self):
        self.assertIdRanges([], 'root:foo:2')
        self.assertIdRanges([], 'root:2:foo')

    def test_no_newline(self):
        self.assertIdRanges([('root', 1000, 1)], 'root:1000:1')

    def test_ignore_comments(self):
        self.assertIdRanges([('root', 1000, 1), ('foo', 12, 42)],
                            'root:1000:1\n# foo\nfoo:12:42')


class TestCheckIdFor(unittest.TestCase):

    def setUp(self):
        super(TestCheckIdFor, self).setUp()
        fixtures.isolate_from_disk(self)

    def create_ids(self, typ, ids):
        with open(os.path.join(self.etc_dir, 'sub{}'.format(typ)), 'w') as f:
            f.write(ids)

    def test_present(self):
        self.create_ids('uid', 'root:1000:1')
        self.assertTrue(lxd.check_id_for('root', 1000, 'uid', self.etc_dir))

    def test_absent_from_subgid(self):
        self.create_ids('gid', '')
        self.assertFalse(lxd.check_id_for('root', 1000, 'gid', self.etc_dir))

    def test_absent_from_subuid(self):
        self.create_ids('uid', '')
        self.assertFalse(lxd.check_id_for('root', 1000, 'uid', self.etc_dir))


@features.requires(features.lxd_client_feature)
class TestCheckNesting(unittest.TestCase):

    def setUp(self):
        super(TestCheckNesting, self).setUp()
        fixtures.isolate_from_disk(self)

    def create_ids(self, uids, gids):
        with open(os.path.join(self.etc_dir, 'subuid'), 'w') as f:
            f.write(uids)
        with open(os.path.join(self.etc_dir, 'subgid'), 'w') as f:
            f.write(gids)

    def test_no_nesting(self):
        self.create_ids('root:100000:65536\n_lxd:100000:65536\n',
                        'root:100000:65536\n_lxd:100000:65536\n')
        self.assertTrue(lxd.check_nesting(0, self.etc_dir))

    def test_nesting_one(self):
        self.create_ids('root:100000:131072\n_lxd:100000:131072\n',
                        'root:100000:131072\n_lxd:100000:131072\n')
        self.assertTrue(lxd.check_nesting(1, self.etc_dir))

    def test_nesting_two(self):
        self.create_ids('root:100000:196608\n_lxd:100000:196608\n',
                        'root:100000:196608\n_lxd:100000:196608\n')
        self.assertTrue(lxd.check_nesting(2, self.etc_dir))

    @features.requires(features.lxd_client_feature)
    def test_not_enough(self):
        lxc_version = features.lxd_client_feature.version
        if lxc_version[0] == '3':
            self.skipTest('Lxd {} needs to support nesting'.format(
                '.'.join(lxc_version)))
        self.create_ids('root:100000:131072\n_lxd:100000:131072\n',
                        'root:100000:131072\n_lxd:100000:131072\n')
        self.assertFalse(lxd.check_nesting(2, self.etc_dir))


class TestRemoteAdd(unittest.TestCase):

    def setUp(self):
        super(TestRemoteAdd, self).setUp()
        fixtures.setup_tests_config(self)
        features.requires_existing_vm(self, 'byov-lxd-client')
        features.requires_existing_vm(self, 'byov-lxd-server')
        fixtures.set_uniq_vm_name(self)
        self.client_name = 'client-' + self.vm_name
        self.server_name = 'server-' + self.vm_name
        # Create a shared config
        conf = config.VmStack(self.client_name)
        conf.store._load_from_string('''
[{client}]
vm.name = {client}
vm.class = ephemeral-lxd
vm.backing = byov-lxd-server
[{server}]
vm.name = {server}
vm.class = ephemeral-lxd
vm.backing = byov-lxd-server
'''.format(client=self.client_name, server=self.server_name))
        conf.store.save()
        conf.store.unload()
        self.client = self.start_ephemeral(self.client_name)
        self.server = self.start_ephemeral(self.server_name)
        self.out = io.StringIO()
        self.err = io.StringIO()
        fixtures.override_logging(self)

    def start_ephemeral(self, vm_name):
        vm = lxd.EphemeralLxd(config.VmStack(vm_name))
        self.addCleanup(vm.stop)
        vm.start()
        return vm

    def shell_on_vm(self, vm_name, args, out=None, err=None):
        if out is None:
            out = self.out
        if err is None:
            err = self.err
        full_cmd = ['shell', vm_name] + args
        ret = commands.run(full_cmd, out=out, err=err)
        msg = 'Cmd {} failed with {}:\n\tstdout: {}\n\tstderr: {}'
        self.assertEqual(0, ret, msg.format(
            full_cmd, ret, out.getvalue(),
            err.getvalue()))
        return ret, out.getvalue(), err.getvalue()

    def shell_on_server(self, args, out=None, err=None):
        return self.shell_on_vm(self.server_name, args, out=out, err=err)

    def test_add_remote(self):
        self.shell_on_server(['lxc config set core.https_address :8443'])
        self.shell_on_server(['lxc config set core.trust_password s3cr3t'])
        server_ip = self.server.conf.get('vm.ip')
        cmd_args = ['remote', 'add', self.server_name,
                    '{}:8443'.format(server_ip),
                    '--password', 's3cr3t', '--accept-certificate']
        ret, out, err = self.client.shell_captured('lxc', *cmd_args)
        msg = 'remote add {} failed with {}:\n\tstdout: {}\n\tstderr: {}'
        self.assertEqual(0, ret, msg.format(cmd_args, ret, out, err))
        _, out, _ = self.client.shell_captured('lxc', 'remote', 'list')
        stem = self.server_name
        self.assertTrue(stem in out, 'Cannot find {} in {}'.format(stem, out))
        stem = 'https://' + server_ip + ':8443'
        self.assertTrue(stem in out, 'Cannot find {} in {}'.format(stem, out))


class TestRemote(unittest.TestCase):

    def setUp(self):
        super(TestRemote, self).setUp()
        fixtures.setup_tests_config(self)
        fixtures.set_uniq_vm_name(self)
        self.lxd_remote = features.requires_remote_lxd(self)
        # Create a shared config
        conf = config.VmStack(self.vm_name)
        conf.set('vm.name', self.vm_name)
        conf.set('vm.class', 'lxd')
        conf.set('vm.distribution', 'ubuntu')
        conf.set('vm.architecture', 'amd64')
        conf.set('lxd.remote', self.lxd_remote)
        conf.store.save()
        conf.store.unload()
        fixtures.override_logging(self)

    def test_setup(self):
        vm = lxd.Lxd(config.VmStack(self.vm_name))
        self.addCleanup(vm.teardown)
        self.addCleanup(vm.stop)
        vm.setup()
        # We should be able to ssh with the right user
        ret, out, err = vm.shell_captured('whoami')
        self.assertEqual(0, ret)
        self.assertEqual(vm.conf.get('vm.user') + '\n', out)
        # The lxd.remote option should be saved.
        self.assertEqual(self.lxd_remote, vm.econf.get('lxd.remote'))
