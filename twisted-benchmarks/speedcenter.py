
"""
Evaluate one or more benchmarks and upload the results to a Speedcenter server.
"""

from __future__ import division, print_function

import subprocess
import json
import requests
import sys

from sys import argv, stdout
from os import uname, path
from sys import executable
from datetime import datetime

from twisted.python.compat import nativeString
from twisted.python.usage import UsageError

from benchlib import BenchmarkOptions, Driver

# Unfortunately, benchmark name is the primary key for speedcenter
SPEEDCENTER_NAMES = {
    'tcp_connect': 'TCP Connections',
    'tcp_throughput': 'TCP Throughput',
    'ssh_connect': 'SSH Connections',
    'ssh_throughput': 'SSH Throughput',
    'ssl_connect': 'SSL Connections',
    'ssl_throughput': 'SSL Throughput',
    'sslbio_connect': 'SSL (Memory BIO) Connections',
    'sslbio_throughput': 'SSL (Memory BIO) Throughput',
    }


class SpeedcenterOptions(BenchmarkOptions):
    optParameters = [
        ('url', None, None, 'Location of Speedcenter to which to upload results.'),
        ]

    def postOptions(self):
        if not self['url']:
            raise UsageError("The Speedcenter URL must be provided.")



class SpeedcenterDriver(Driver):
    def benchmark_report(self, acceptCount, duration, name):
        print(name, acceptCount, duration)
        stdout.flush()
        self.results.setdefault(name, []).append((acceptCount, duration))



def reportEnvironment():
    lines = subprocess.check_output(["git", "show", "-q", '--format=%H,%ai']).split(b"\n")
    revision, date = lines[0].split(b",")
    exec_trimmed = path.basename(executable)

    resp = {
        'project': 'Twisted',
        'executable': exec_trimmed,
        'environment': uname()[1].split('.')[0],
        'commitid': nativeString(revision),
        'branch': 'trunk',
        'revision_date': " ".join(nativeString(date).split(" ")[0:2]),
        'result_date': str(datetime.now())[0:-7],
    }
    print(resp)
    return resp



def main():
    options = SpeedcenterOptions()
    try:
        options.parseOptions(argv[1:])
    except UsageError as e:
        raise SystemExit(str(e))

    environment = reportEnvironment()

    from all import allBenchmarks

    driver = SpeedcenterDriver()
    driver.results = {}
    driver.run_jobs(
        allBenchmarks,
        options['duration'], options['iterations'], options['warmup'])

    allStats = []

    for (name, results) in sorted(driver.results.items()):
        rates = [count / duration for (count, duration) in results]
        totalCount = sum([count for (count, duration) in results])
        totalDuration = sum([duration for (count, duration) in results])

        name = SPEEDCENTER_NAMES.get(name, name)
        stats = environment.copy()
        stats['benchmark'] = name
        stats['result_value'] = totalCount / totalDuration
        stats['min'] = min(rates)
        stats['max'] = max(rates)
        allStats.append(stats)

    tries = 0
    r = None

    while tries < 5:
        r = requests.post(options['url'], data={"json": json.dumps(allStats)})
        if r.status_code == 202:
            print(r.content)
            return
        tries = tries + 1
        print("Try #{}".format(tries))

    print(r.content)
    sys.exit(1)

if __name__ == '__main__':
    main()
