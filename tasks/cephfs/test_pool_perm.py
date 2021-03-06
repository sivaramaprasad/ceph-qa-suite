from textwrap import dedent
from tasks.cephfs.cephfs_test_case import CephFSTestCase
import os


class TestPoolPerm(CephFSTestCase):
    def test_pool_perm(self):
        self.mount_a.run_shell(["touch", "test_file"])

        file_path = os.path.join(self.mount_a.mountpoint, "test_file")

        remote_script = dedent("""
            import os
            import errno

            fd = os.open("{path}", os.O_RDWR)
            try:
                if {check_read}:
                    ret = os.read(fd, 1024)
                else:
                    os.write(fd, 'content')
            except OSError, e:
                if e.errno != errno.EPERM:
                    raise
            else:
                raise RuntimeError("client does not check permission of data pool")
            """)

        client_name = "client.{0}".format(self.mount_a.client_id)

        # set data pool read only
        self.fs.mon_manager.raw_cluster_cmd_result(
            'auth', 'caps', client_name, 'mds', 'allow', 'mon', 'allow r', 'osd',
            'allow r pool={0}'.format(self.fs.get_data_pool_name()))

        self.mount_a.umount_wait()
        self.mount_a.mount()
        self.mount_a.wait_until_mounted()

        # write should fail
        self.mount_a.run_python(remote_script.format(path=file_path, check_read=str(False)))

        # set data pool write only
        self.fs.mon_manager.raw_cluster_cmd_result(
            'auth', 'caps', client_name, 'mds', 'allow', 'mon', 'allow r', 'osd',
            'allow w pool={0}'.format(self.fs.get_data_pool_name()))

        self.mount_a.umount_wait()
        self.mount_a.mount()
        self.mount_a.wait_until_mounted()

        # read should fail
        self.mount_a.run_python(remote_script.format(path=file_path, check_read=str(True)))

    def tearDown(self):
        self.fs.mon_manager.raw_cluster_cmd_result(
            'auth', 'caps', "client.{0}".format(self.mount_a.client_id),
            'mds', 'allow', 'mon', 'allow r', 'osd',
            'allow rw pool={0}'.format(self.fs.get_data_pool_name()))

        super(TestPoolPerm, self).tearDown()
