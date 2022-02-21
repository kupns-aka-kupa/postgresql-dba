import os
import glob
import subprocess
import ipaddress
import numpy as np
from datetime import datetime, timedelta

import matplotlib.pyplot as plt

host = ipaddress.ip_address('172.23.169.19')
sec = timedelta(hours=10)
d = datetime.now().strftime("%d-%m-%Y-%H:%M:%S")


def plot_args(stderr):
    for s in stderr:
        print(s)
        yield list(map(float, filter(isfloat, s.split())))


def isfloat(s: str):
    return s.replace('.', '').isdigit()


debug_plot = False

data_file = 'pg_bench_stat_{0}.{1}'


def run():
    if debug_plot:
        files = list(filter(os.path.isfile, glob.glob("*.csv")))
        files.sort(key=os.path.getmtime)
        return np.loadtxt(files[-1], delimiter='|')
    process = subprocess.Popen(
        ['pgbench', '-c8', '-h', str(host), '-v', '-P', '5', '-T', str(sec.seconds), '-U', 'postgres', 'postgres'],
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=0)

    process.stdin.write('postgres')
    process.stdin.close()

    args = plot_args(process.stderr)
    return np.array(list(filter(None, args))).T


if __name__ == '__main__':
    t = run()

    np.savetxt(data_file.format(d, 'csv'), t, delimiter='|')

    fig, (tps, lat, stddev) = plt.subplots(3)
    tps.plot(t[0], t[1])
    tps.set_title('tps')
    lat.plot(t[0], t[2], 'tab:orange')
    lat.set_title('lat')
    lat.set(ylabel='ms')
    stddev.plot(t[0], t[3], 'tab:green')
    stddev.set_title('stddev')

    for ax in fig.get_axes():
        ax.set(xlabel='sec')
        ax.label_outer()

    plt.show()
    plt.savefig(data_file.format(d, 'png'))
