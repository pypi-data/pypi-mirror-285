## `Grid`

检查输入的 `x` 和 `y` 是否为（能构造）二维规则网格。网格形状为 `(nx, ny)`

`within_grid` 方法判断索引 `(xi, yi)` 对于该网格来说是否合法。

## `StreamMask`

构造一个形如 `30 * density` 或 `(30 * density, 30 * density)` 的网格，如果流线通过某个网格点，那么这个点的计数 +1，并且不再允许其它流线通过这个网格。

```Python
def _update_trajectory(self, xm, ym, broken_streamlines=True):
```

根据轨迹的整数坐标 `(xm, ym)` 更新 `mask` 的计数。如果坐标之前被填充过，且设定了 `broken_streamlines=True`，那么抛出 `InvalidIndexError` 异常。

## `DomainMap`

```Python
def __init__(self, grid, mask):
```

