""" Plot Graph in terminal


   from src.utils.utilmy_graph import (histogram, bar, scatter )



"""
import fire 

########################################################################################################
def histogram(x, bins=5, height=10, mark='▇'):
    '''A simple histogram chart that prints to the console

    :param x: list, array or series of numeric values
    :param bins: integer for the number of bins
    :param height: integer for the output height
    :param mark: unicode symbol to mark data values

    x = [1, 2, 4, 3, 3, 1, 7, 9, 9, 1, 3, 2, 1, 2]
    histogram(x)
    ▇ ▇     ▇
    ▇ ▇   ▇ ▇

    import scipy.stats as stats
    import numpy as np
    np.random.seed(14)
    n = stats.norm(loc=0, scale=10)
    histogram(n.rvs(100), bins=14, height=7, mark='🍑')
    '''
    binned_x = NumberBinarizer(bins).fit_transform(x)
    counter = {x: 0 for x in range(bins)}
    for x in binned_x:
        counter[x] += 1
    x, y = list(counter.keys()), list(counter.values())
    y = RangeScaler((0, height), floor=0).fit_transform(y)
    matrix = [[' '] * bins for _ in range(height)]
    for xi, yi in zip(x, y):
        if yi == 0:
            continue
        for yii in range(yi):
            matrix[yii][xi] = mark
    matrix = matrix[::-1]
    string_chart = ''
    for row in matrix:
        string_row = ' '.join(row)
        string_chart += string_row
        string_chart += '\n'
    print(string_chart)
    


def bar(x, y, width=30, label_width=None, mark='▇'):
    '''A simple bar chart that prints to the console

    :param x: list, array or series of numeric values
    :param y: list, array or series of labels for the numeric values
    :param width: integer for the character length of the x values
    :param label_width: integer for the label character length
    :param mark: unicode symbol to mark data values


    x = [500, 200, 900, 400]
    y = ['marc', 'mummify', 'chart', 'sausagelink']
    bar(x, y)
           marc: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇
        mummify: ▇▇▇▇▇▇▇
          chart: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇
    sausagelink: ▇▇▇▇▇▇▇▇▇▇▇▇▇

    import pandas as pd
    df = pd.DataFrame({
        'artist': ['Tame Impala', 'Childish Gambino', 'The Knocks'],
        'listens': [8_456_831, 18_185_245, 2_556_448]
    })
    bar(df.listens, df.artist, width=20, label_width=11, mark='🔊')
    Tame Impala: 🔊🔊🔊🔊🔊🔊🔊🔊🔊
    Childish Ga: 🔊🔊🔊🔊🔊🔊🔊🔊🔊🔊🔊🔊🔊🔊🔊🔊🔊🔊🔊🔊
     The Knocks: 🔊🔊🔊                 
    '''
    if not label_width:
        label_width = max([len(l) for l in y])
    labels = [create_label(l, label_width) for l in y]
    values = RangeScaler((0, width), 0).fit_transform(x)
    string_chart = ''
    for value, label in zip(values, labels):
        string_row = build_row(value, label, width, mark)
        string_chart += string_row
        string_chart += '\n'
    print(string_chart)




def scatter(x, y, width=40, height=None, mark='•'):
    '''A simple scatter plot that prints to the console

    :param x: list, array or series of numeric values
    :param y: list, array or series of numeric values
    :param width: integer for the character length of the x values
    :param height: integer for the character length of the y values
    :param mark: unicode symbol to mark data values

    from chart import scatter
    x = range(0, 20)
    y = range(0, 20)
    scatter(x, y)
                                           •
                                       • •
                                     •
                                 • •
                             • •
                           •

    import numpy as np
    np.random.seed(1)
    N = 100
    x = np.random.normal(100, 50, size=N)
    y = x * -2 + 25 + np.random.normal(0, 25, size=N)
    scatter(x, y, width=20, height=9, mark='^')

    ^^
     ^
        ^^^
        ^^^^^^^
           ^^^^^^
    '''
    if not height:
        height = int(width / 3 // 1)
    matrix = [[' '] * width for _ in range(height)]
    x = RangeScaler((0, width-1)).fit_transform(x)
    y = RangeScaler((0, height-1)).fit_transform(y)
    for (xi, yi) in zip(x, y):
        matrix[yi][xi] = mark
    matrix = matrix[::-1]
    string_chart = ''
    for row in matrix:
        string_row = ''.join(row)
        string_chart += string_row
        string_chart += '\n'
    print(string_chart)




######################################################################################################
def scale(x, o=(0, 100), i=(0, 1)):
    return (x - i[0]) / (i[1] - i[0]) * (o[1] - o[0]) + o[0]


class RangeScaler:
    '''A scaler to coerce values to a target output range

    rs = RangeScaler(out_range=(0, 50), floor=0, round=False)
    rs.fit(x)
    rs.transform([18, 24, 75])
    [7.5, 10.0, 31.25]
    '''
    def __init__(self, out_range=(0, 100), floor=None, round=True):
        self.out_range = out_range
        self.floor = floor
        self.round = round

    def fit(self, y):
        if not self.floor and self.floor != 0:
            min_ = min(y)
        else:
            min_ = self.floor
        max_ = max(y)
        self.in_range_ = (min_, max_)
        return self

    def transform(self, y):
        y = [scale(yi, self.out_range, self.in_range_) for yi in y]
        if self.round:
            y = [int(round(yi)) for yi in y]
        return y

    def fit_transform(self, y):
        self.fit(y)
        return self.transform(y)


def bin(x, b, o=(0, 100)):
    return int(b * ((x - o[0]) / (o[1] - o[0])))



class NumberBinarizer:
    '''A binarizer that cuts values into equal-width bins

    x = range(10)
    NumberBinarizer(4).fit_transform(x)
    [0, 0, 0, 1, 1, 2, 2, 3, 3, 3]
    '''
    def __init__(self, bins=5):
        self.bins = bins

    def fit(self, y):
        self.min_ = min(y)
        self.max_ = max(y)
        return self

    def transform(self, y):
        y = [bin(yi, self.bins, (self.min_, self.max_)) for yi in y]
        y = [yi - 1 if yi == self.bins else yi for yi in y]
        return y

    def fit_transform(self, y):
        self.fit(y)
        return self.transform(y)
    


def create_label(label, label_width):
    '''Add right padding to a text label'''
    label = label[:label_width]
    label = label.rjust(label_width)
    label += ': '
    return label


def build_row(value, label, width, mark):
    '''Build a complete row of data'''
    marks = value * mark
    row = marks.ljust(width)
    row = label + row
    return row







###################################################################################################
###################################################################################################
import numpy as np, decimal
from numpy.typing import ArrayLike
import re, subprocess, sys
from typing import List, Tuple, Union,Optional




def barh(
    vals: List[int],
    labels: Optional[List[str]] = None,
    max_width: int = 40,
    bar_width: int = 1,
    show_vals: bool = True,
    val_format: Optional[str] = None,
    force_ascii: bool = False,
):
    """
    Generate a horizontal bar chart with labels and values.

    Args:
        vals (List[int]): The list of values to be plotted.
        labels (Optional[List[str]], optional): The list of labels for each value. Defaults to None.
        max_width (int, optional): The maximum width of the chart. Defaults to 40.
        bar_width (int, optional): The width of each bar. Defaults to 1.
        show_vals (bool, optional): Whether to show the values on the chart. Defaults to True.
        val_format (Optional[str], optional): The format string for the values. Defaults to None.
        force_ascii (bool, optional): Whether to force ASCII characters for the chart. Defaults to False.

    Returns:
        List[str]: The list of strings representing the horizontal bar chart.
    """    
    partition = _get_partition(vals, max_width)
    partition = np.repeat(partition, bar_width, axis=1)

    if is_unicode_standard_output() and not force_ascii:
        chars = [" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
    else:
        chars = [" ", "*", "*", "*", "*", "*", "*", "*", "*"]

    fmt = []
    if labels is not None:
        max_len = max(len(str(label)) for label in labels)
        cfmt = f"{{:{max_len}s}}"
        fmt.append(cfmt)

    if show_vals:
        if val_format is not None:
            cfmt = val_format
        elif np.issubdtype(np.asarray(vals).dtype, float):
            # find max decimal length
            # https://stackoverflow.com/a/6190291/353337
            num_digits = max(
                -decimal.Decimal(str(val)).as_tuple().exponent for val in vals
            )
            cfmt = f"{{:.{num_digits}f}}"
        elif np.issubdtype(np.asarray(vals).dtype, np.integer):
            max_len = max(len(str(val)) for val in vals)
            cfmt = f"{{:{max_len}d}}"
        else:
            cfmt = "{}"
        fmt.append("[" + cfmt + "]")

    fmt.append("{}")
    fmt = "  ".join(fmt)

    out = []
    for k, (val, num_full, remainder) in enumerate(
        zip(vals, partition[0], partition[1])
    ):
        data = []
        if labels is not None:
            data.append(str(labels[k]))
        if show_vals:
            data.append(val)

        # Cut off trailing zeros
        data.append("".join([chars[-1]] * num_full + [chars[remainder]]))
        out.append(fmt.format(*data))

    return out



def hist(
    samples: List[float]=None, n_bins:int=10, counts:  List[int]=None, 
    bin_edges: List[float]=None, mode: str = "horizontal", max_width: int = 40, 
    grid=None, bar_width: int = 1, strip: bool = False, force_ascii: bool = False,
):
    """
    Generate a histogram plot.
    
    
    samples = np.random.randint(0,5, 50)
    hist(samples, n_bins=10, mode='horizontal')

    Parameters:
        counts (List[int]): A list of integers representing the counts or frequencies of each bin.
        bin_edges (List[float]): A list of floats representing the edges of each bin.
        orientation (str, optional): The orientation of the histogram plot. Default is "vertical".
        max_width (int, optional): The maximum width of the histogram plot. Default is 40.
        grid (object, optional): An object representing the grid lines of the plot. Default is None.
        bar_width (int, optional): The width of each bar in the histogram plot. Default is 1.
        strip (bool, optional): Whether to strip leading/trailing whitespace from each bar. Default is False.
        force_ascii (bool, optional): Whether to force ASCII characters for bar rendering. Default is False.

    Returns:
        The generated histogram plot.

    Raises:
        AssertionError: If the orientation is not "vertical" or "horizontal".

    """    
    if samples is not None:
        counts, bin_edges = np.histogram(samples, bins=n_bins)
    

    if mode in ["vertical", 'v', 'vert',]:
        return hist_vertical(
            counts, xgrid=grid, bar_width=bar_width, strip=strip, force_ascii=force_ascii,
        )

    # assert mode  "horizontal", f"Unknown orientation '{mode}'"
    ll = hist_horizontal(
        counts, bin_edges, max_width=max_width, bar_width=bar_width, force_ascii=force_ascii,
    )
    ss = "\n".join(ll)
    return ss


def hist_horizontal(
    counts: List[int],
    bin_edges: List[float],
    max_width: int = 40,
    bar_width: int = 1,
    show_bin_edges: bool = True,
    show_counts: bool = True,
    force_ascii: bool = False,
):
    """
    Generate a horizontal histogram given the counts and bin edges.

    Parameters:
        counts (List[int]): The counts for each bin.
        bin_edges (List[float]): The edges of each bin.
        max_width (int, optional): The maximum width of the histogram. Defaults to 40.
        bar_width (int, optional): The width of each bar. Defaults to 1.
        show_bin_edges (bool, optional): Whether to show the bin edges as labels. Defaults to True.
        show_counts (bool, optional): Whether to show the count values as labels. Defaults to True.
        force_ascii (bool, optional): Whether to use ASCII characters for the bars. Defaults to False.

    Returns:
        None
    """    
    if show_bin_edges:
        labels = [
            f"{bin_edges[k]:+.2e} - {bin_edges[k+1]:+.2e}"
            for k in range(len(bin_edges) - 1)
        ]
    else:
        labels = None

    return barh(
        counts,
        labels=labels,
        max_width=max_width,
        bar_width=bar_width,
        show_vals=show_counts,
        force_ascii=force_ascii,
    )


def hist_vertical(
    counts: List[int],
    max_height: int = 10,
    bar_width: int = 2,
    strip: bool = False,
    xgrid: Optional[List[int]] = None,
    force_ascii: bool = False,
):
    """
    Generate a vertical histogram representation of the given counts.

    Args:
        counts (List[int]): The list of counts for each bar in the histogram.
        max_height (int, optional): The maximum height of the histogram bars. Defaults to 10.
        bar_width (int, optional): The width of each bar in the histogram. Defaults to 2.
        strip (bool, optional): Whether to strip leading and trailing rows of 0. Defaults to False.
        xgrid (Optional[List[int]], optional): The positions at which to add grid lines. Defaults to None.
        force_ascii (bool, optional): Whether to force ASCII characters for the histogram. Defaults to False.

    Returns:
        List[str]: The vertical histogram representation as a list of strings.
    """    
    if xgrid is None:
        xgrid = []

    partition = _get_partition(counts, max_height)

    if strip:
        # Cut off leading and trailing rows of 0
        num_head_rows_delete = np.argmax(np.any(partition != 0, axis=0))
        num_tail_rows_delete = np.argmax(np.any(partition != 0, axis=0)[::-1])

        n = partition.shape[1]
        partition = partition[:, num_head_rows_delete : n - num_tail_rows_delete]
    else:
        num_head_rows_delete = 0

    matrix = _get_matrix_of_eighths(partition[0], partition[1], max_height, bar_width)

    if is_unicode_standard_output() and not force_ascii:
        block_chars = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        left_seven_eighths = "▉"
    else:
        block_chars = [" ", "*", "*", "*", "*", "*", "*", "*", "*"]
        left_seven_eighths = "*"

    block_chars = np.array(block_chars)

    out = []
    for row in np.flipud(matrix.T):
        # converts row into block chars
        c = block_chars[row]

        # add grid lines
        for i in xgrid:
            pos = (i - num_head_rows_delete) * bar_width - 1
            if row[pos] == 8 and (pos + 1 == len(row) or row[pos + 1] > 0):
                c[pos] = left_seven_eighths

        out.append("".join(c))

    return out


def _get_matrix_of_eighths(
    nums_full_blocks, remainders, max_size, bar_width: int
) -> np.ndarray:
    """
    Returns a matrix of integers between 0-8 encoding bar lengths in histogram.

    For instance, if one of the sublists is [8, 8, 8, 3, 0, 0, 0, 0, 0, 0], it means
    that the first 3 segments should be graphed with full blocks, the 4th block should
    be 3/8ths full, and that the rest of the bar should be empty.
    """
    matrix = np.zeros((len(nums_full_blocks), max_size), dtype=int)

    for row, num_full_blocks, remainder in zip(matrix, nums_full_blocks, remainders):
        row[:num_full_blocks] = 8
        if num_full_blocks < matrix.shape[1]:
            row[num_full_blocks] = remainder

    return np.repeat(matrix, bar_width, axis=0)












def create_padding_tuple(padding: Union[int, List[int], Tuple[int, int]]):
    # self._padding is a 4-tuple: top, right, bottom, left (just like CSS)
    if isinstance(padding, int):
        out = (padding, padding, padding, padding)
    else:
        if len(padding) == 1:
            out = (padding[0], padding[0], padding[0], padding[0])
        elif len(padding) == 2:
            out = (padding[0], padding[1], padding[0], padding[1])
        elif len(padding) == 3:
            out = (padding[0], padding[1], padding[2], padding[1])
        else:
            assert len(padding) == 4
            out = (padding[0], padding[1], padding[2], padding[3])
    return out


def is_unicode_standard_output():
    if sys.stdout.encoding is None:
        return True

    return hasattr(sys.stdout, "encoding") and sys.stdout.encoding.lower() in (
        "utf-8",
        "utf8",
    )


def get_gnuplot_version():
    out = subprocess.check_output(["gnuplot", "--version"]).decode()
    m = re.match("gnuplot (\\d).(\\d) patchlevel (\\d)\n", out)
    if m is None:
        raise RuntimeError("Couldn't get gnuplot version")

    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def _get_partition(values: ArrayLike, max_size: int):
    values = np.asarray(values)
    assert np.all(values >= 0)
    maxval = np.max(values)
    if maxval == 0:
        maxval = 1

    eighths = np.around(values / maxval * max_size * 8).astype(int)
    return np.array([eighths // 8, eighths % 8])















###################################################################################################
if __name__ == "__main__":
    fire.Fire()



