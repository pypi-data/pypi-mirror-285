

# jgtfx2console

just getting prices from fxconnect


## Installation
```sh
pip install -U jgtfx2console
```

## Example

```py

    >>> import pandas as pd
    >>> import jgtfx2console
    >>> df=jgtfx2console.getPH('EUR/USD','H4')
    >>>
    >>> # retrieve 3000 periods and generate from the DF
    >>> df=jgtfx2console.getPH('EUR/USD','H4',3000,with_index=False)
    >>> dfi=jgtfx2console.createFromDF(df)
    >>>

```

## More


### Enhancements Idea

#### -l (for --timeline)

* --@STCGoal An easy way to snap a moment in time and save it to our store.

```sh
jgtfxcli -i "SPX500" -t "H1,H4,H8,D1,W1,M1" -c 500 -l "22101313"

```

```
$JGTPY_DATA/pds  NORMAL
$JGTPY_DATA/pdl/  L Item

```