def plot():
    from matplotlib import pyplot as plt

    a = [pow(10, i) for i in range(10)]
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.semilogy(a, color="blue", lw=0.25, base=2)

    plt.grid(visible=True, which="major", color="g", linestyle="-", linewidth=0.25)
    plt.grid(visible=True, which="minor", color="r", linestyle="--", linewidth=0.5)
    return fig


def test():
    from .helpers import assert_equality

    assert_equality(plot, __file__[:-3] + "_reference.tex")
