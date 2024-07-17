# USAggregate

USAggregate is a Python package for aggregating and merging US geographic data frames.

## Installation

You can install the package using pip:

```{sh}
pip install USAggregate
```

Below is an example of package usage.

```{python}
import pandas as pd
from USAggregate.usaggregate import usaggregate

data_city = pd.DataFrame({
    'city': ['Albany', 'Albany', 'Buffalo', 'Buffalo'],
    'state': ['NY', 'NY', 'NY', 'NY'],
    'value': [1, 2, 3, 4],
    'year': [2017, 2018, 2017, 2018]
})

data_county = pd.DataFrame({
    'county': ['Albany', 'Albany', 'Erie', 'Erie'],
    'state': ['NY', 'NY', 'NY', 'NY'],
    'value': [5, 6, 7, 8],
    'year': [2017, 2018, 2017, 2018]
})

# Example usage of usaggregate function
result = usaggregate([data_city, data_county], level='state')
print(result)

```

