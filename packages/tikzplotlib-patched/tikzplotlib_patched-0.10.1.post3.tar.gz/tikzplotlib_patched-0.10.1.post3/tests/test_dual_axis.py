import matplotlib.pyplot as plt
import numpy as np


def plot():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    dat = np.linspace(0, 10, 20)
    ax.plot(dat, dat**2)
    ax2 = ax.twinx()
    ax2.plot(20 * dat, 20 * dat**2)
    ax.xaxis.tick_top()
    return fig


def test():
    from .helpers import assert_equality

    assert_equality(plot, "test_dual_axis_reference.tex")
