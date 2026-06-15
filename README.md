# uperf (Network Performance) Benchmark Wrapper

## Description

This wrapper facilitates the automated execution of the uperf network performance benchmark. uperf is a network performance tool that supports modelling and replay of various networking patterns. Originally developed by Sun Microsystems, it is released under GPLv3.

The wrapper provides:
- Automated uperf download, build, and installation on local and remote hosts.
- Support for multiple test types (stream, request/response, maerts, bidirectional).
- Support for TCP and UDP protocols.
- Multi-network and multi-client/server topology testing.
- Configurable packet sizes, thread counts, and network counts.
- Dynamic XML workload profile generation.
- Automatic remote server setup (uperf daemon, firewall, package installation).
- Result collection, processing, and verification across three metric types (throughput, latency, transactions).
- CSV and JSON output formats.
- System configuration metadata capture.
- Integration with test_tools framework.
- Optional Performance Co-Pilot (PCP) integration.

For more information see: https://github.com/uperf/uperf

## Command-Line Options

```
uperf Options:
  --client_ips <value>: Comma-separated list of client IP addresses.
      Required. If not provided, the script will prompt for input.
  --server_ips <value>: Comma-separated list of server IP addresses.
      Required. If not provided, the script will prompt for input.
  --intervals <x>: Creates x+1 evenly spaced thread-count intervals from 1 to ncpus.
      Overrides --numb_jobs with auto-generated values.
  --max_stddev <value>: Maximum standard deviation threshold for uperf runs.
  --networks_to_run <value>: Comma-separated list of network counts to test.
      Default: 1,2,3,4,6,8,12,16,20,24,28,32.
  --numb_jobs <value>: Comma-separated list of thread counts (instances) per test.
      Default: 1,8,16,32,64.
  --packet_sizes <value>: Comma-separated list of packet sizes in bytes.
      Default: 64,16384.
  --packet_type <value>: Comma-separated list of protocols to test (tcp, udp).
      Default: udp,tcp.
  --suffix <value>: Suffix to append to results file names.
  --tests <value>: Comma-separated list of test types to run.
      Options: stream, rr, maerts, bidirec. Default: stream,rr,bidirec,maerts.
  --time <seconds>: Duration of each test measurement in seconds. Default: 60.
  --time_delay <seconds>: Delay in seconds before starting the next iteration. Default: 0.

General test_tools options:
  --debug: Enable bash -x debug output for wrapper troubleshooting.
  --home_parent <value>: Parent home directory. If not set, defaults to current working directory.
  --host_config <value>: Host configuration name, defaults to current hostname.
  --iterations <value>: Number of times to run the test, defaults to 1.
  --json_skip: Skip JSON conversion of test CSV results.
  --no_pkg_install: Do not install any packages (system or pip). Useful for pre-provisioned systems.
  --no_system_packages: Do not install system packages via the package manager. Pip packages are still installed.
  --no_pip_packages: Do not install Python pip packages. System packages are still installed.
  --run_label <value>: Label to associate with the run. No default.
  --run_user: User that is actually running the test on the test system. Defaults to current user.
  --sys_type: Type of system working with (aws, azure, hostname). Defaults to hostname.
  --sysname: Name of the system running, used in determining config files. Defaults to hostname.
  --test_tools_release <tag>: Version tag of test_tools-wrappers to check out and use.
  --tuned_setting: Used in naming the results directory. For RHEL, defaults to current active tuned profile.
      For non-RHEL systems, defaults to 'none'. If set to a profile name, activates that tuned profile.
  --use_pcp: Enable Performance Co-Pilot monitoring during test execution.
  --verify_skip: Skip result verification against the Pydantic schema.
  --tools_git <value>: Git repo to retrieve the required tools from.
      Default: https://github.com/redhat-performance/test_tools-wrappers
  --usage: Display this usage message.
```

## What the Script Does

The `uperf_run` script performs the following workflow:

1. **Environment Setup**:
   - Clones the test_tools-wrappers repository if not present (default: ~/test_tools).
   - Sources error codes, general setup utilities, and helper functions.
   - Gathers hardware information via `gather_data`.

2. **Package Installation**:
   - Installs required dependencies on the local host via package_tool using `uperf.json`.
   - Copies test_tools and `uperf.json` to each client host and installs packages remotely via SSH.
   - Dependencies are defined for different OS variants (RHEL, Ubuntu, SLES, Amazon Linux).

3. **uperf Build and Installation**:
   - On the local host: runs `uperf_build` which checks for an existing uperf binary.
     - If `/bin/uperf` exists, copies it to `/usr/local/bin/uperf`.
     - Otherwise, clones uperf from source, runs `autoreconf`, `configure`, and `make install`.
   - On remote server hosts: copies `uperf_build` via SCP and executes it remotely.
   - On RHEL systems: installs `epel-release` before building.

4. **Remote Server Setup**:
   - Copies the `uperf_build` script to each server host and executes it.
   - Stops the firewall (`firewalld`) on each server to allow uperf traffic.
   - Starts the uperf daemon in server mode (`uperf -s`) on each server host.
   - Waits 30 seconds for servers to become ready.

5. **XML Profile Generation**:
   - Dynamically generates XML workload profiles for each test combination.
   - Profiles define the connection type, flow operations, thread count, packet size, and duration.
   - Supports four test patterns:
     - **stream**: connect, write data for duration, disconnect.
     - **rr** (request/response): connect, write then read for duration, disconnect.
     - **maerts** (reverse stream): accept, read data for duration, disconnect.
     - **bidirec** (bidirectional): combines stream and maerts patterns.

6. **Test Execution**:
   - Iterates over all combinations of: test types, network counts, thread counts, packet types, packet sizes, and iterations.
   - For each combination:
     - Generates an XML profile targeting the server IP.
     - Copies the XML profile and uperf binary to each client host.
     - Launches uperf on each client via SSH in parallel.
     - Waits for all client processes to complete.
     - Captures network interface statistics (via `ethtool -S`) before and after each test.
   - Optionally collects PCP data per test iteration.

7. **Data Collection**:
   - Captures raw uperf output with timing, throughput, and transaction data.
   - Records start and end timestamps for each test run.
   - Captures network interface statistics before and after each test.
   - Records test status ("Ran" or "Failed") per iteration.
   - Optionally records PCP performance data.

8. **Result Processing**:
   - Organizes raw results into a directory hierarchy: `test_type/packet_type/packet_size/network_count`.
   - Parses uperf output to extract throughput (Gb/s), transactions per second (op/s), and latency (usec).
   - Normalizes throughput values (converts Mb/s and Kb/s to Gb/s).
   - Calculates latency from transaction rate: `latency = 1 / ops_per_second`.
   - Generates separate CSV files for each metric type: `throughput.csv`, `pps.csv`, `lat.csv`.
   - Generates a combined `results_uperf.csv` with all metrics.
   - Creates JSON output for verification.

9. **Verification**:
   - Validates results against per-metric Pydantic schemas (`schemas/throughput`, `schemas/pps`, `schemas/lat`).
   - Each schema validates: instances > 0, metric value >= 0, test type, packet type, packet size > 0, and timestamps.
   - Uses `csv_to_json` and `verify_results` from test_tools.

10. **Output**:
    - Creates timestamped results directory in `/tmp/uperf_results_<suffix>_<YYYY.MM.DD-HH.MM.SS>`.
    - Saves raw uperf output, processed CSV/JSON, network statistics, and system metadata.
    - Optionally saves PCP performance data.
    - Archives results to configured storage location via `save_results`.

## Dependencies

**Location of underlying workload**: Cloned from https://github.com/uperf/uperf and built from source, or uses a pre-installed `/bin/uperf` binary if available.

**General packages required**:

- **RHEL**: autoconf, automake, gcc, lksctp-tools-devel, bc, net-tools, zip, unzip, git
- **Ubuntu**: libsctp-dev, lksctp-tools, libusrsctp-dev, autoconf, dh-autoreconf, automake, gcc, bc, git, unzip, zip
- **SLES**: autoconf, automake, gcc, lksctp-tools-devel, lksctp-tools, make, numactl, bc, git, unzip, zip
- **Amazon Linux**: autoconf, automake, git, gcc, lksctp-tools-devel, xorg-x11-xauth, bc, zip, unzip

To run:
```bash
git clone https://github.com/redhat-performance/uperf-wrapper
cd uperf-wrapper/uperf
./uperf_run --server_ips <server_ip> --client_ips <client_ip>
```

The script will build uperf on local and remote hosts, start the uperf server daemon, and execute the test matrix.

## The uperf Benchmark

uperf is a network performance measurement tool that uses a profile-based approach to define workloads. Unlike simple throughput tools, uperf can model complex networking patterns using XML profiles that describe sequences of flow operations (connect, read, write, disconnect).

### Test Types

1. **stream**: Unidirectional data transfer from client to server. Measures maximum throughput by continuously writing data for the test duration.

2. **rr** (Request/Response): Simulates request/response patterns. The client writes a request, then reads a response, repeated for the test duration. Measures transaction rate and latency.

3. **maerts** (Reverse Stream): Unidirectional data transfer from server to client (reverse of stream). The client accepts connections and reads data.

4. **bidirec** (Bidirectional): Combines stream and maerts patterns. Data flows in both directions simultaneously.

### Performance Metrics

uperf reports three key metrics:

1. **Throughput** (Gb/s): Network bandwidth measured in gigabits per second. The wrapper normalizes all values to Gb/s (converting from Mb/s or Kb/s as needed).

2. **Transactions per Second** (op/s): Number of completed operations per second. Most relevant for request/response (rr) tests.

3. **Latency** (usec): Time per operation in microseconds. Calculated as `1 / transactions_per_second`. Most relevant for request/response (rr) tests.

### Protocol Support

- **TCP**: Reliable, connection-oriented protocol. Default for most network performance testing.
- **UDP**: Unreliable, connectionless protocol. Useful for measuring raw throughput without TCP overhead.

## Output Files

The results directory contains:

- **results_uperf.csv**: Combined CSV file with all metrics (throughput, transactions, latency) across all test configurations.
- **throughput.csv**: CSV file with bandwidth measurements (Gb/s) per test configuration.
- **pps.csv**: CSV file with transaction rate measurements (op/s) per test configuration.
- **lat.csv**: CSV file with latency measurements (usec) per test configuration.
- **results_uperf.json**: JSON output validated against the Pydantic schema.
- **summary_results_\***: Raw uperf output files with per-test results and timestamps.
- **net_stats_\*_iter_\*.before/after**: Network interface statistics captured before and after each test iteration via `ethtool -S`.
- **test_results_report**: File indicating test status ("Ran" or "Failed") per iteration.
- **meta_data\*.yml**: System metadata (CPU info, memory, NUMA topology, kernel version).
- **uperf.out**: Full script execution log.
- **PCP data** (if --use_pcp option used): Performance Co-Pilot monitoring data.

### Results Schemas

Results are validated against three separate Pydantic schemas:

**Throughput schema** (`schemas/throughput`):

| Field | Type | Constraint |
|-------|------|------------|
| instances | int | > 0 |
| Bandwidth_Gb_sec | float | >= 0 |
| test | str | required |
| packet_type | str | required |
| packet_size | int | > 0 |
| Start_Date | datetime | required |
| End_Date | datetime | required |

**Latency schema** (`schemas/lat`):

| Field | Type | Constraint |
|-------|------|------------|
| instances | int | > 0 |
| Latency_usec | float | >= 0 |
| test | str | required |
| packet_type | str | required |
| packet_size | int | > 0 |
| Start_Date | datetime | required |
| End_Date | datetime | required |

**Transactions schema** (`schemas/pps`):

| Field | Type | Constraint |
|-------|------|------------|
| instances | int | > 0 |
| trans_sec | int | > 0 |
| test | str | required |
| packet_type | str | required |
| packet_size | int | > 0 |
| Start_Date | datetime | required |
| End_Date | datetime | required |

## Examples

### Basic two-host test
```bash
./uperf_run --server_ips 192.168.1.10 --client_ips 192.168.1.20
```
This runs with all defaults:
- All test types (stream, rr, bidirec, maerts)
- TCP and UDP
- Packet sizes 64 and 16384 bytes
- Thread counts 1, 8, 16, 32, 64
- 60-second test duration
- 1 iteration

### TCP-only stream test
```bash
./uperf_run --server_ips 192.168.1.10 --client_ips 192.168.1.20 \
    --tests stream --packet_type tcp
```
Runs only the stream test type over TCP.

### Custom packet sizes
```bash
./uperf_run --server_ips 192.168.1.10 --client_ips 192.168.1.20 \
    --packet_sizes 64,512,1024,4096,16384,65536
```
Tests with six different packet sizes to profile throughput across the range.

### Request/response latency test
```bash
./uperf_run --server_ips 192.168.1.10 --client_ips 192.168.1.20 \
    --tests rr --packet_type tcp --packet_sizes 64 --numb_jobs 1
```
Single-threaded TCP request/response test with 64-byte packets for baseline latency measurement.

### Auto-generated thread intervals
```bash
./uperf_run --server_ips 192.168.1.10 --client_ips 192.168.1.20 \
    --intervals 8
```
Generates 9 evenly-spaced thread counts from 1 to the number of CPUs, replacing the default `--numb_jobs` list.

### Multi-network topology
```bash
./uperf_run --server_ips 10.0.1.10,10.0.2.10,10.0.3.10,10.0.4.10 \
    --client_ips 10.0.1.20 --networks_to_run 1,2,4
```
Tests with 1, 2, and 4 network connections using the specified server IPs.

### Run multiple iterations with delay
```bash
./uperf_run --server_ips 192.168.1.10 --client_ips 192.168.1.20 \
    --iterations 3 --time_delay 30
```
Runs 3 iterations with 30 seconds between each run.

### Extended test duration
```bash
./uperf_run --server_ips 192.168.1.10 --client_ips 192.168.1.20 \
    --time 120 --tests stream --packet_type tcp
```
Runs a 120-second TCP stream test for more stable throughput measurements.

### Run with PCP monitoring
```bash
./uperf_run --server_ips 192.168.1.10 --client_ips 192.168.1.20 --use_pcp
```
Collects Performance Co-Pilot data during the run.

### Combination example
```bash
./uperf_run --server_ips 192.168.1.10 --client_ips 192.168.1.20 \
    --tests stream,rr --packet_type tcp --packet_sizes 64,16384 \
    --numb_jobs 1,16,64 --iterations 3 --time 120 --use_pcp
```
Runs stream and rr tests over TCP with two packet sizes, three thread counts, three iterations, 120-second duration, and PCP monitoring.

## How the Test Matrix Works

The wrapper iterates over all combinations of test parameters in a nested loop structure:

```
for each test_type (stream, rr, maerts, bidirec):
  for each network_count (from --networks_to_run):
    for each thread_count (from --numb_jobs):
      for each packet_type (tcp, udp):
        for each packet_size (from --packet_sizes):
          for each iteration (from --iterations):
            execute_test()
```

### Total Test Combinations

The total number of individual test executions is:
```
test_types x network_counts x thread_counts x packet_types x packet_sizes x iterations
```

With defaults, this is: `4 x 12 x 5 x 2 x 2 x 1 = 960` individual test runs. Each runs for 60 seconds by default, so a full default matrix takes approximately 16 hours. Use `--tests`, `--numb_jobs`, `--packet_sizes`, `--packet_type`, and `--networks_to_run` to reduce the matrix for faster testing.

## How Multi-Host Topology Works

The wrapper supports distributed testing across multiple client and server hosts:

### Server Hosts
- Each server IP in `--server_ips` runs a uperf daemon (`uperf -s`).
- The wrapper SSHs to each server to build uperf, stop the firewall, and start the daemon.
- Multiple server IPs enable multi-network testing (each IP represents a network path).

### Client Hosts
- Each client IP in `--client_ips` runs the uperf client workload.
- The wrapper copies the XML profile and uperf binary to each client via SCP.
- All clients run in parallel against the server(s).
- Packages and test_tools are installed on each client remotely.

### Network Count Scaling
The `--networks_to_run` parameter controls how many server IPs are used simultaneously:
- With `--networks_to_run 1,2,4` and 4 server IPs, the wrapper tests with 1 server, then 2 servers, then 4 servers.
- This measures how throughput scales with additional network paths.

### SSH Requirements
- Passwordless SSH (key-based authentication) must be configured from the test host to all client and server hosts.
- The wrapper connects as `root` to remote hosts.
- `StrictHostKeyChecking` is disabled for automated operation.

## Return Codes

The script uses standardized error codes from test_tools error_codes:
- **0**: Success
- **101**: Git clone failure (test_tools repository)
- **E_GENERAL**: General execution errors (SSH failures, build failures, XML generation failures, test execution failures).
- **E_PARSE_ARGS**: Argument parsing failure
- **E_PACKAGE_TOOL_PACKAGING**: Package installation failure
- **E_USAGE**: Invalid usage/arguments

A non-zero return code from `verify_results` indicates that the output data did not pass schema validation.

## Notes

### Network Topology Requirements
- uperf requires at least two hosts: one client and one server.
- The `--server_ips` and `--client_ips` parameters are required. If not provided on the command line, the script will prompt interactively.
- All hosts must be reachable via passwordless SSH as root.
- Firewalls on server hosts are automatically stopped (`systemctl stop firewalld`).

### Architecture Support
- **x86_64**: Fully supported.
- **aarch64**: Supported (uperf builds from source on ARM).
- The wrapper does not have architecture-specific tuning; it relies on uperf's portable codebase.

### Build Process
- The `uperf_build` helper script handles installation on both local and remote hosts.
- If `/bin/uperf` already exists (e.g., from a system package), it is copied to `/usr/local/bin/uperf` without rebuilding.
- Otherwise, uperf is cloned from GitHub and built from source (`autoreconf`, `configure`, `make install`).
- On RHEL systems, `epel-release` is installed to provide build dependencies.

### Performance Tips
- For throughput tests, use larger packet sizes (16384+ bytes) to reduce per-packet overhead.
- For latency tests, use small packet sizes (64 bytes) with `--tests rr` and `--numb_jobs 1`.
- Reduce the test matrix for initial runs — the full default matrix (960 tests) takes many hours.
- Use `--time_delay` between iterations to allow network state to settle.
- Consider the active tuned profile on RHEL systems (e.g., `network-throughput` or `network-latency`).
- Run multiple iterations to verify consistency.

### Throughput Normalization
The wrapper normalizes all throughput values to Gb/s:
- Values reported in Mb/s are divided by 1024.
- Values reported in Kb/s are divided by 1048576.
- This ensures consistent units across all result files regardless of the raw uperf output format.

### Troubleshooting
- If SSH connections fail, verify passwordless SSH is configured for root on all client and server hosts.
- If uperf fails to build, verify that `autoconf`, `automake`, and `gcc` are installed on the target host.
- If tests produce no results (test_results_report shows "Failed"), check that the uperf daemon is running on server hosts (`ps aux | grep uperf`).
- If firewall issues persist, manually verify `systemctl status firewalld` on server hosts.
- If throughput is unexpectedly low, check for network bottlenecks using the `net_stats_*` before/after files.
- Use `--use_pcp` to collect detailed performance counters for analysis.
- The full script execution log is saved to `uperf.out` in the results directory.
