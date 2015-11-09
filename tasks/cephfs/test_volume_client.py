

import json
import logging
import tempfile
import os
from textwrap import dedent
from tasks.cephfs.cephfs_test_case import CephFSTestCase

log = logging.getLogger(__name__)


class TestVolumeClient(CephFSTestCase):
    # One for looking at the global filesystem, one for being
    # the VolumeClient, one for mounting the created shares
    CLIENTS_REQUIRED = 3

    def _volume_client_python(self, client, script):
        return client.run_python("""
from ceph_volume_client import CephFSVolumeClient, VolumePath

vc = CephFSVolumeClient("manila", "{conf_path}", "ceph")
vc.connect()
{payload}
vc.disconnect()
        """.format(payload=script, conf_path=client.config_path))

    def test_lifecycle(self):
        """
        General smoke test for create, extend, destroy
        """

        # I'm going to use mount_c later as a guest for mounting the created
        # shares
        self.mounts[2].umount()

        # I'm going to leave mount_b unmounted and just use it as a handle for
        # driving volumeclient.  It's a little hacky but we don't have a more
        # general concept for librados/libcephfs clients as opposed to full
        # blown mounting clients.
        self.mount_b.umount_wait()

        out = self.fs.mon_manager.raw_cluster_cmd(
            "auth", "get-or-create", "client.manila",
            "mds", "allow *",
            "osd", "allow rw",
            "mon", "allow *"
        )
        keyring_local = tempfile.NamedTemporaryFile()
        keyring_local.write(out)
        keyring_local.flush()
        self.mount_b.client_id = "manila"
        self.mount_b.client_remote.put_file(keyring_local.name, self.mount_b.get_keyring_path())
        self.set_conf("client.manila", "keyring", self.mount_b.get_keyring_path())

        guest_entity = "guest"
        group_id = "grpid"
        volume_id = "volid"
        key = self._volume_client_python(self.mount_b, dedent("""
            vp = VolumePath("{group_id}", "{volume_id}")
            vc.create_volume(vp, 10)
            print vc.authorize(vp, "{guest_entity}")
        """.format(
            group_id=group_id,
            volume_id=volume_id,
            guest_entity=guest_entity
        )))

        # The dir should be created
        self.mount_a.stat(os.path.join("volumes", group_id, volume_id))

        # The auth identity should exist
        existing_ids = [a['entity'] for a in self.auth_list()]
        self.assertIn("client.{0}".format(guest_entity), existing_ids)

        keyring_local = tempfile.NamedTemporaryFile()
        keyring_local.write(dedent("""
        [client.{guest_entity}]
            key = {key}

        """.format(
            guest_entity=guest_entity,
            key=key
        )))
        keyring_local.flush()

        # We should be able to mount the volume
        self.mounts[2].client_id = guest_entity
        self.mounts[2].client_remote.put_file(keyring_local.name, self.mounts[2].get_keyring_path())
        self.set_conf("client.{0}".format(guest_entity), "debug client", "20")
        self.set_conf("client.{0}".format(guest_entity), "debug objecter", "20")
        self.set_conf("client.{0}".format(guest_entity), "keyring", self.mounts[2].get_keyring_path())
        # TODO get the mount_path out of volumeclient instead of rely on our knowledge of it
        self.mounts[2].mount(mount_path=os.path.join("/volumes", group_id, volume_id))



        # Client keys are initially written to /etc/ceph/ceph.client.0.keyring
        # using authtool in ceph_client.py.
        # We need to take an arbitrary key, insert it there, and then be ready to remove
        # it again in test teardown
        # Or... we need to set a ceph config for client.guest, send that keyring file out