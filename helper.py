import re
from dataclasses import dataclass
VALID_AGG = {"sum", "avg", "count", "min", "max"}

@dataclass
class AggregateToken:
    gv: int
    func: str
    attr: str
    genVer: str
    raw: str
    
def positiveIntCheck(value, field_name):
    try:
        number = int(value)
    except ValueError:
        raise ValueError(f"{field_name} must be an integer")

    if number <= 0:
        raise ValueError(f"{field_name} must be greater than 0")

    return number


def parseAggregate(item):
    raw = item
    parts = item.split("_")
    
    if len(parts) != 3 or not parts[0].isdigit():
        return None
    
    gv = int(parts[0])
    func = parts[1]
    attr = "_".join(parts[2:])
    
    if func not in VALID_AGG:
        raise ValueError(f"Invalid aggregate function: {func}")
    
    genVer = f"values._{gv}_{func}_{attr}"
    
    return AggregateToken(gv, func, attr,genVer, raw)

def normalizeItems(item):
    token = parseAggregate(item)
    return token.genVer if token else item

def suchthatStruct(item):
    return re.sub(r"(\d+)\.([a-zA-Z_]\w*)",r'row["\2"]',item)

def havingStruct(item):
    return re.sub(
        r"\b\d+_[A-Za-z]+_[A-Za-z_]\w*\b",
        lambda m: normalizeItems(m.group(0)),
        item
    )