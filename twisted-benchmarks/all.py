from __future__ import print_function


from twisted.python.reflect import namedAny

from benchlib import multidriver

allBenchmarkNames = [
    "iteration", "names", "threads", "web", "web_template", "pb", "amp",
    "deferred_callback_chains", "deferred_await", "deferred_yieldfrom",
    "linereceiver", "lineonlyreceiver", "int16receiver",

    "tcp_connect", "ssh_connect", "ssl_connect", "sslbio_connect",
    "tcp_throughput", "ssh_throughput", "ssl_throughput", "sslbio_throughput",
    ]

allBenchmarks = []

for name in allBenchmarkNames:
    try:
        main = namedAny(name).main
    except Exception as e:
        print('Skipping', name, ':', e)
    else:
        allBenchmarks.append(main)

if __name__ == '__main__':
    multidriver(allBenchmarks)
