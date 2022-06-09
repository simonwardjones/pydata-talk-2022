import colorsys
import math
from typing import Union

numeric = Union[int, float, complex]


def draw_heap(
    heap: list[numeric],
    draw_connectors: bool = True,
    pad: int = 2,
    use_color: bool = True,
):
    """
    Draws a heap as a string.

    Parameters
    ----------
    heap : list[numeric]
        The heap to draw.
    draw_connectors : bool, optional
        Whether to draw the connectors between elements.
    pad : int, optional
        The amount of space to leave between elements.
    use_color : bool, optional
        Whether to use colors in the output.

    Returns
    -------
    str
        The string representation of the heap.
    """
    n_rows = int(math.ceil(math.log(len(heap) + 1, 2)))
    total_width = 2**n_rows * pad

    # one row for each level and connection between levels
    rows = ["" for _ in range(2 * n_rows)]
    if use_color:
        yiq_tuples = [colorsys.yiq_to_rgb(0.5, x / n_rows, 0.3) for x in range(n_rows)]
        pallet = [tuple(int(x * 255) for x in yiq) for yiq in yiq_tuples]
        for i, (r, g, b) in enumerate(pallet):
            rows[2 * i] = rows[2 * i + 1] = f"\033[38;2;{r};{g};{b}m"

    for position, value in enumerate(heap):
        row = int(math.floor(math.log(position + 1, 2)))
        n_columns = 2**row
        column_width = total_width // n_columns
        rows[2 * row] += str(value).center(column_width)

        if draw_connectors:
            children = heap[2 * position + 1 : 2 * position + 3]
            r = (column_width - 3) // 4
            if len(children) == 2:
                drop_downs = f"┏{'━' * r}┻{'━' * r}┓".center(column_width)
            elif len(children) == 1:
                drop_downs = f"┏{'━' * r}┛{' ' * (r+1)}".center(column_width)
            else:
                drop_downs = f" " * column_width
            rows[2 * row + 1] += drop_downs

    list_str = str(heap).center(total_width) + "\n"
    if use_color:
        r, g, b = pallet[0]
        list_str = f"\033[38;2;{r};{g};{b}m{list_str}\033[0m"
    rows.insert(0, list_str)

    print("\n".join(rows))


if __name__ == "__main__":
    heap = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    draw_heap(heap)

    """
                  1                
          ┏━━━━━━━┻━━━━━━━┓        
          2               3        
      ┏━━━┻━━━┓       ┏━━━┻━━━┓    
      4       5       6       7    
    ┏━┻━┓                          
    8   9  
    """
