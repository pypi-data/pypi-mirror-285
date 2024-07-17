# rulesheet (work in progress)
> Convert Business Rules defined in a Google Sheet or CSV to Python

## usage
Define business rules in a CSV.  See an example of a csv [here](https://github.com/officeofperformancemanagement/rulesheet/blob/main/example.csv).

```python
from rulesheet import load_ruler_from_csv

ruler = load_ruler_from_csv("./example.csv")

ruler.test({ "year": 2023, "city": "Chattanooga" })
True
```
