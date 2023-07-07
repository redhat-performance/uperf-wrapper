Automation wrapper for uperf 2005

Description:
      uperf is a network performance tool that supports modelling and replay
      of various networking patterns. uperf was initially developed by the
      Performance Applications Engineering group at Sun Microsystems. Since
      2008, it is being developed by the community. uperf is released under
      the GNU General Public License Version 3. 
  
Location of underlying workload: https://github.com/uperf/uperf

Packages required: python3,gcc,lksctp-tools-devel,bc

To run:
```
[root@hawkeye ~]# git clone https://github.com/redhat-performance/uperf-wrapper
[root@hawkeye ~]# uperf-wrapper/uperf/uperf_run
```

Options
/root/uperf-wrapper/uperf/uperf_run --usage
Usage /root/specjbb-wrapper///specjbb/specjbb_run:
```
  --client_ips: comma separated list of the client ip addresses
  --max_stddev: standard deviation of the pbench uperf runs
  --networks_to_run: how many networks are we to run.
  --numb_jobs: comma separated list of the number of jobs per network to run
  --packet_sizes: comma separated list of packet sizes, (in bytes)
  --packet_type:  comma separated list of packet types, (tcp,udp)
  --server_ips: comma separated list of the server ip addresses
  --suffix: Suffix to add to the results file
  --test_types:  stream,rr,maerts,bidirec
  --time:  number of seconds to run the test for
  --time_delay <x>: Delay x seconds before the next iteration is started.
  --tools_git: Pointer to the test_tools git.  Default is https://github.com/redhat-performance/test_tools-wrappers.  Top directory is always test_tools
  --use_pbench_version: Instead of running the wrappers version
     of uperf, use pbench-uperf when pbench is requested
General options
  --home_parent <value>: Our parent home directory.  If not set, defaults to current working directory.
  --host_config <value>: default is the current host name.
  --iterations <value>: Number of times to run the test, defaults to 1.
  --pbench: use pbench-user-benchmark and place information into pbench, defaults to do not use.
  --pbench_user <value>: user who started everything. Defaults to the current user.
  --pbench_copy: Copy the pbench data, not move it.
  --pbench_stats: What stats to gather. Defaults to all stats.
  --run_label: the label to associate with the pbench run. No default setting.
  --run_user: user that is actually running the test on the test system. Defaults to user running wrapper.
  --sys_type: Type of system working with, aws, azure, hostname.  Defaults to hostname.
  --sysname: name of the system running, used in determing config files.  Defaults to hostname.
  --tuned_setting: used in naming the tar file, default for RHEL is the current active tuned.  For non
    RHEL systems, default is none.
  --usage: this usage message.
```
