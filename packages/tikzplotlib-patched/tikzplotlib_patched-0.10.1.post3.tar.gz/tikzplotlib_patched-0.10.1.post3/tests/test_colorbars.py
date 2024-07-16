import matplotlib as mpl
import matplotlib.pyplot as plt


def plot():
    # Make a figure and axes with dimensions as desired.
    fig, ax = plt.subplots(4)

    # Set the colormap and norm to correspond to the data for which the colorbar will be
    # used.
    cmap = mpl.cm.cool
    norm = mpl.colors.Normalize(vmin=-5, vmax=10)

    # ColorbarBase derives from ScalarMappable and puts a colorbar in a specified axes,
    # so it has everything needed for a standalone colorbar.  There are many more
    # kwargs, but the following gives a basic continuous colorbar with ticks and labels.
    cb1 = mpl.colorbar.ColorbarBase(
        ax[0], cmap=cmap, norm=norm, orientation="horizontal"
    )
    cb1.set_label("Some Units")

    # The second example illustrates the use of a ListedColormap, a BoundaryNorm, and
    # extended ends to show the "over" and "under" value colors.
    cmap = mpl.colors.ListedColormap(["r", "g", "b", "c"])
    cmap.set_over("0.25")
    cmap.set_under("0.75")

    # If a ListedColormap is used, the length of the bounds array must be one greater
    # than the length of the color list.  The bounds must be monotonically increasing.
    bounds = [1, 2, 4, 7, 8]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    cb2 = mpl.colorbar.ColorbarBase(
        ax[1],
        cmap=cmap,
        norm=norm,
        # to use 'extend', you must
        # specify two extra boundaries:
        boundaries=[0] + bounds + [13],
        extend="both",
        ticks=bounds,  # optional
        spacing="proportional",
        orientation="horizontal",
    )
    cb2.set_label("Discrete intervals, some other units")

    # The third example illustrates the use of custom length colorbar extensions, used
    # on a colorbar with discrete intervals.
    cmap = mpl.colors.ListedColormap(
        [[0.0, 0.4, 1.0], [0.0, 0.8, 1.0], [1.0, 0.8, 0.0], [1.0, 0.4, 0.0]]
    )
    cmap.set_over((1.0, 0.0, 0.0))
    cmap.set_under((0.0, 0.0, 1.0))

    bounds = [-1.0, -0.5, 0.0, 0.5, 1.0]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    cb3 = mpl.colorbar.ColorbarBase(
        ax[2],
        cmap=cmap,
        norm=norm,
        boundaries=[-10] + bounds + [10],
        extend="both",
        # Make the length of each extension
        # the same as the length of the
        # interior colors:
        extendfrac="auto",
        ticks=bounds,
        spacing="uniform",
        orientation="horizontal",
    )
    cb3.set_label("Custom extension lengths, some other units")

    # Set the colormap and norm to correspond to the data for which the colorbar will be
    # used.  This time attach the colorbar to axes.
    cmap = mpl.cm.cool
    norm = mpl.colors.Normalize(vmin=-5, vmax=10)

    img = ax[3].imshow([[0, 1]], cmap=cmap)
    ax[3].set_visible(False)
    cax = fig.add_axes([0.1, 1, 0.8, 0.1])
    cb4 = fig.colorbar(img, cax=cax, orientation="horizontal", label="Some Units")

    return fig


def test():
    from .helpers import assert_equality

    assert_equality(plot, "test_colorbars_reference.tex", assert_compilation=False)
