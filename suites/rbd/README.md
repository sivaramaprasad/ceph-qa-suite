
================================
Comments On RBD Suite Submodules
================================

rbd/basic
---------

* Runs all basic block level tests of Rados Block Device (RBD).

* Basic block level tests are:

    - Create rbd images

    - Clone rbd images

    - Map block devices to rbd images

    - Create snaps

    - Clone snaps

    - Resize snaps

    - Lock rbd images

    - Check for exclusive locks on images

    - Perform IO on rbd image

    - Perform DiffIterate tests

* Perform Some rbd CLI tests like:

    - rbd create test_img

    - pool test,size 1024

    - rbd create new_img_mv

    - pool test,size 1024

    - rbd create new_img_mv

    - pool test,size 0,order 22

* Perform some nosetests on rbd like:

    - test_copy

    - test_create_snap

    - test_diff_create

    - test_large_read

    - test_large_write



rbd/cli
-------
* Uses CLI Utility to perform rbd actions like: 
 
    - Create Pools

    - Import/Export rbd images

    - Copy rbd images among Pools



rbd/librbd
----------
* Uses librados APIs to perform rbd actions like:  

    - Create rbd images

    - Clone rbd images

    - Map block devices to rbd images

    - Create snaps

    - Clone snaps

    - Resize snaps

    - Lock rbd images

    - Check for exclusive locks on images

    - Perform IO on rbd image

    - Perform DiffIterate tests

    - Perform Test Object mapping tests

* Runs fsx on an rbd image.  Fsx will be used to perform read, write, truncate, punch, and clone operations on different regions of an rbd image. 

* Runs fio tests on rbd block devices to measure the IO performance.




rbd/qemu
--------
* Download and runs xfstests on rbd.

* Perform Qemu IO tests against rbd mapped devices.

* QEMU can access an image as a virtual block device directly via librbd. This avoids an additional context switch, and can take advantage of RBD caching.

* You can use qemu-img to convert existing virtual machine images to Ceph block device images.




rbd/singleton
-------------     

* Runs specific individual block level tests of RBD on Single node CEPH cluster.

* Block level tests of rbd are:

    - Runs 15 qemu IO tests against rbd(with no-cache and with rbd caching techniques like:  write-back cache and  write-through cache).

    - Create rbd images and its Snaps then it will set and test read flags with different combinations.

    - Perform Image diff operations like: Import diff, Export diff and Merge diff.

    - Create rbd Images, Resize Images, Create Snaps, Clone Snaps, Lock Snaps and then do test formatting.




rbd/thrash
----------
* Runs the librbd tests along with thrash which is used to simulate random OSD failures.

* "Thrash" the OSDs by randomly marking them out/down (and then back in) until the task is ended. This loops, and every op_delay seconds it randomly chooses to add or remove an OSD (even odds) unless there are fewer than min_out OSDs out of the cluster, or more than min_in OSDs in the cluster.

    - min_in: (default 3) the minimum number of OSDs to keep in the cluster.

    - min_out: (default 0) the minimum number of OSDs to keep out of the cluster.

    - op_delay: (5) the length of time to sleep b/w changing an OSD’s status.

    - min_dead: (0) the minimum number of OSDs to leave down/dead.

    - max_dead: (0) maximum number of OSDs to leave down/dead before waiting for clean.


* While running the task, If some OSDs listed in the dead_OSDs[ ]. Then thrasher may kill that OSD from live_OSDs[ ] and next remove that OSD from in_OSDs[ ]. Next it will automatically revive that OSD.




rbd/valgrind
------------
* Runs the librbd tests under Valgrind which will use memcheck tool to   detect/analyze memory errors like:

    - memory corruption

    - memory leaks





