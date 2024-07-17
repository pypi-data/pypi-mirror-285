# Interactive Terminal Utilities

```python
import itrm
```

This library offers several functions for visualizing data within the terminal.
This project does not exist just because it is cool. It exists because it fills
some needs which few other tools do. For many developers, engineers, and
scientists, the terminal is where much of their time is spent. Having to switch
contexts every time a plot is generated can be time consuming and annoying.
Furthermore, most plotting tools have fairly limited analysis capabilities. They
are great for generating final, beautiful figures, but not great at quickly
inspecting and understanding the data. Also, if you are working with a remote
server through SSH, visualizing the data with conventional tools can be very
tedious: save data to file, transfer data to local machine, write script just to
read and plot data, plot data, repeat. This library lets you directly visualize
and interact with the data, skipping all the tedium.

## Configuration

This library will generate a `config.ini` file in the same directory as the
library's installation. You can either manually modify the settings in that
file, or you can call the `itrm.config()` function. This function will take the
following parameters:

| Setting   | Default       | Description                       |
| --------- | :-----------: | --------------------------------- |
| `uni`     | `True`        | flag to use Unicode characters    |
| `cols`    | `60`          | default column width              |
| `rows`    | `20`          | default row height                |
| `ar`      | `0.48`        | aspect ratio of characters        |
| `cmap`    | `spectrum`    | color map                         |

### Unicode

Much of the plotting in the terminal performed by `itrm` relies on Unicode
characters. However, properly displaying those characters requires having a
monospace font with those specific glyphs defined. In fact, the default plotting
mode relies on braille characters, and relatively few fonts define those. If you
are looking for a good terminal font which supports all the Unicode used by this
library, try out [JuliaMono][julia]. However, you might not be interested in
downloading fonts, so this library can also forego all Unicode characters and
only rely on ASCII characters.

### Columns and Rows

Many terminals provide a means for a Python script to query the current size of
the terminal window in terms of the number of columns and rows of text. However,
not all terminals do. In those cases, it is good to have a fallback setting.
These are defined by the `cols` and `rows` configuration parameters.

### Aspect Ratio

Because all the plotting by this library uses text, the aspect ratio (ratio of
width to height) of the characters affects the apparent aspect ratio of curves.
So, a circle might look perfectly round or squashed depending on the font
chosen. This does not mean you need a new font, you just need to adjust the
aspect ratio setting, `ar`.

### Color Map

By default, the color map used is `spectrum`, a rainbow of colors. Using the
`cmap` parameter, you can pick any of the following color maps: `spectrum`,
`viridis`, `grays`, `reds`, `greens`, `blues`, or `4bit`. All but the last color
map use platform-independent, 8-bit colors. The last color map, `4bit`, lets use
control the colors with your terminal settings, instead.

## Interactive Plots

```python
itrm.iplot(x, y=None, label=None, rows=1, cols=1,
        lg=None, overlay=False):
```

### Parameters

The `iplot` function will render all the data points defined by `x` and `y` to
the terminal. The inputs `x` and `y` can be vectors, matrices, or lists of such
arrays. Each **row** of a matrix is treated as a separate curve. Note, this is
different from MatPlotLib, in which each *column* is treated as a separate row.
(This difference is intentional, as in the author's opinion varying time along
columns means each column in a matrix can be treated as a vector. This
arrangement works very well with in linear algebra, especially matrix
multiplication with a "set" of vectors over time.)

The shapes of `x` and `y` do not have to be the same, but they must be
compatible. So, `x` could be a vector and `y` could be a matrix as long as the
length of `x` equals the number of columns of `y`.

If only `x` is given, it will be interpreted as the `y` values, and the `x`
values will be the array of indices.

When the plot is printed, the graph is rendered within a box and the ranges of
`x` and `y` are listed in the bottom left corner. So,

```
(0:99, -1.5:1.5)
```

means that `x` ranges from `0` to `99` and `y` ranges from `-1.5` to `1.5`.

If a `label` is given, this will be printed in the bottom right of the plot box.
It can also be a list of strings. If the length of the list is the same as the
number of data sets (each row of a matrix is a different data set), then each
string in the list will be displayed with the respective data set. If the length
of the list is one greater, the first string will be displayed for the whole
plot.

The `rows` and `cols` parameters let you specify the number of terminal text
rows and columns to use for the plot, respectively. For each of these, if the
value is less than or equal to 1, it represents a portion of the available space
to use. For example, if `rows` is `0.5`, then half the number of rows of the
current terminal window will be used for the plot. If the value is greater than
1, it represents the absolute number of rows or columns to use. Also, if the
size of the current terminal cannot be obtained, the available space will
default to `20` rows and `60` columns.

You can set the x or y axes to logarithmic scaling by setting the `lg` parameter
to one of `"x"`, `"y"`, or `"xy"`. Note that the values reported for the view
and the cursor will be in the original scaling, not logarithmic.

To prevent your terminal history from extending each time a new plot is
rendered, you can print a new plot over a previous plot by setting the `overlay`
parameter to `True`. This can be especially useful when there are multiple plots
to render (like for an animation) but you do not want your terminal history to
fill up quickly.

### Keybindings

The `iplot` function provides interactivity through a vertical cursor. You can
move the cursor left and right, at normal speed or fast speed. You can zoom in
and out. And, you can cycle through which rows of the `x` and `y` data to focus
on. Note, `iplot` is designed for monotonically-increasing `x` values, and,
consequently, does not support equal axis scaling.

![](https://gitlab.com/davidwoodburn/itrm/-/raw/main/figures/fig_iplot.png)

The following table details the shortcut keys:

| Keys           | Function               |   | Keys           | Function                 |
| :------------: | ---------------------- | - | :------------: | ------------------------ |
| `q`, `⌫`, `↵`  | exit interactive plot  |   | `j`, `s`, `↓`  | zoom in                  |
| `h`, `a`, `←`  | move cursor left       |   | `k`, `w`, `↑`  | zoom out                 |
| `l`, `d`, `→`  | move cursor right      |   | `J`, `S`, `⇧↓` | zoom in fast             |
| `H`, `A`, `⇧←` | move cursor left fast  |   | `K`, `W`, `⇧↑` | zoom out fast            |
| `L`, `D`, `⇧→` | move cursor right fast |   | `n`            | select next data set     |
| `g`            | move cursor to start   |   | `N`            | select previous data set |
| `G`            | move cursor to end     |   | `i`            | toggle individual view   |
| `c`, `z`       | center view on cursor  |   | `v`            | toggle ghost cursor      |
| `x`            | toggle x log scaling   |   | `f`            | start function           |
| `y`            | toggle y log scaling   |   | `F`            | restore original data    |

Note that in Windows terminal emulators, there is no support for shift-arrow
keys. Instead, use alt-arrow keys.

### Individual Data Sets

When many data sets are being plotted simultaneously, it can be helpful to hide
all other data sets with the `i` key in order to just see the selected data
set.

### Ghost Cursor

If you want to make a comparison between two points, you can use the ghost
cursor. First, position the cursor at the start position. Then, press the `v`
key. Immediately, you should see in the bottom left corner, several metrics:
the difference in x positions (`dx`), the difference in y positions (`dy`), the
mean y value (`u`), and the standard deviation of y (`s`). Moving the cursor
will leave behind a ghost. As the cursor moves, the metrics will update to
reflect the range of values from the ghost cursor to the current cursor.

### Functions

Without writing any code, you can run a number of functions on the data and see
the results. First, press the `f` key. Then, follow that with other keys to get
the specific function applied to the data. The following table shows the full
key sequences:

| Keys  | Description                               |
| :---: | ----------------------------------------- |
| `fd`  | Derivative of `y` with respect to `x`     |
| `fi`  | Integral of `y` with respect to `x`       |
| `ff`  | Magnitude of Fourier transform of `y`     |
| `ftl` | Trim (remove) data left of cursor         |
| `ftr` | Trim (remove) data right of cursor        |
| `f#a` | Weighted moving average of half width #   |
| `f#d` | De-trend data with polynomial of degree # |

(Other functions are planned for the future.) When one of the functions have
been applied, the sides of the plotting box will be rendered gray. You can
restore the original data by pressing the `F` key.

## Plots

```python
itrm.plot(x, y=None, label=None, rows=1, cols=1,
        ea=0, lg=None, overlay=False):
```

The `plot` function is a non-interactive version of the `iplot` function. All
of the same parameters are provided, with the addition of the equal-axes (`ea`)
parameter. This function does not require monotonicity of the x-axis data.

| Single curve    | Multiple curves |
| --------------- | --------------- |
| ![](https://gitlab.com/davidwoodburn/itrm/-/raw/main/figures/fig_plot_1.png) | ![](https://gitlab.com/davidwoodburn/itrm/-/raw/main/figures/fig_plot_6.png) |

## Bars

```python
itrm.bars(x, labels=None, cols=1, fat=False)
```

It can be convenient to plot a simple bar graph. The `x` input is the vector of
values. The `labels` input is a list of strings corresponding to the labels to
print before the bar of each value in `x`. If the `cols` input is greater than
1, it is the total width of characters including the labels. If it is less than
or equal to 1, it is the portion of the terminal window width which will be used
for the graph. If the `fat` input is set to `True`, the bars will be thick.

```
 apples |=========                                         |
oranges |=========================================         |
bananas |==================================================|
  pears |====================                              |
 grapes |============================                      |
```

## Heat maps

```python
itrm.heat(matrix)
```

The `heat` function will generate a heat map of the `matrix` input using 24
shades of gray. Black is used for the lowest value and white for the highest
value. If `itrm.config.uni` is `True`, half-block characters from the Unicode
table will be used. If it is `False`, two spaces per element of the matrix will
be used.

| With Unicode      | Without Unicode     |
| ----------------- | ------------------- |
| ![](https://gitlab.com/davidwoodburn/itrm/-/raw/main/figures/fig_heat_uni.png) | ![](https://gitlab.com/davidwoodburn/itrm/-/raw/main/figures/fig_heat_ascii.png) |

## Tables

```python
itrm.table(matrix, head=None, left=None, width=10, sep='  ')
```

You can print a nicely spaced table of the `matrix` data. The `head` and `left`
inputs are lists of header and left-most column labels, respectively, to print
around the `matrix`.

```
           |      Set 1       Set 2       Set 3
---------- | ----------  ----------  ----------
    apples | 0.65802165  0.20015677  0.51074794
   bananas | 0.42184098  0.46774988  0.39589918
     pears | 0.79159879  0.89324181  0.57347394
   oranges | 0.25932644  0.29973433  0.90646047
    grapes |  0.2751687  0.40117769  0.58233234
```

## Sparsity

```python
itrm.spy(matrix)
```

If all you want to see is the sparsity of a matrix, use this function.

| With Unicode          | Without Unicode         |
| --------------------- | ----------------------- |
| ![](https://gitlab.com/davidwoodburn/itrm/-/raw/main/figures/fig_sparsity_uni.png) | ![](https://gitlab.com/davidwoodburn/itrm/-/raw/main/figures/fig_sparsity_ascii.png) |

## Progress bars

```python
bar = itrm.Progress(K, cols=1)
bar.update(k)
```

There are many progress bar libraries available for Python. But, many of them
seem to be extremely over-complicated. TQDM, for example, includes over 20
source files. This library's implementation of a progress bar is a single,
one-page function. The `k` input is the counter of whatever for loop the
progress bar is reporting on. The `K` input is one greater than the largest
possible value of `k`, as in `for k in range(K):`. When the process is
completed, the total elapsed time will be displayed. If `cols` is not provided,
the full width of the current terminal window will be used.

```
 44% ======================----------------------------- -00:00:02.1
```

[julia]: https://juliamono.netlify.app/
