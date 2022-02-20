import subprocess
import ipaddress
import numpy as np

import matplotlib.pyplot as plt

host = ipaddress.ip_address('172.23.169.19')
sec = 600


def plot_args(stderr):
    for s in stderr:
        yield list(map(float, filter(isfloat, s.split())))


def isfloat(s: str):
    return s.replace('.', '').isdigit()


if __name__ == '__main__':
    process = subprocess.Popen(
        ['pgbench', '-c8', '-h', str(host), '-P', '30', '-T', str(sec), '-U', 'postgres', 'postgres'],
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=0)

    process.stdin.write('postgres')
    process.stdin.close()

    args = plot_args(process.stderr)
    t = np.array(list(filter(None, args))).T

    fig, (tps, lat, stddev) = plt.subplots(3)
    tps.plot(t[0], t[1])
    tps.set_title('tps')
    lat.plot(t[0], t[2], 'tab:orange')
    lat.set_title('lat')
    stddev.plot(t[0], t[3], 'tab:green')
    stddev.set_title('stddev')

    for ax in fig.get_axes():
        ax.set(xlabel='sec')
        ax.label_outer()

    plt.show()
