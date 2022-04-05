import allel
import matplotlib.pyplot as plt


def plot_ld(gn, title, n=None, filename=None):
    if n is None:
        n = gn.shape[0]
    nvars = min(gn.shape[0], n)
    m = allel.stats.ld.rogers_huff_r(gn[:nvars]) ** 2
    ax = allel.stats.ld.plot_pairwise_ld(m)
    ax.set_title(title)
    if filename is not None:
        plt.savefig(filename)
        plt.cla()
        plt.clf()
