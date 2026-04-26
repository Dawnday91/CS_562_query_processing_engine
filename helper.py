from dataclasses import dataclass
VALID_AGG = {"sum", "avg", "count", "min", "max"}

@dataclass
class AggregateToken:
    gv: int
    func: str
    attr: str

def positiveIntCheck(value, field_name):
    try:
        number = int(value)
    except ValueError:
        raise ValueError(f"{field_name} must be an integer")

    if number <= 0:
        raise ValueError(f"{field_name} must be greater than 0")

    return number


def parseAggregate(item):
    parts = item.split("_")
    
    if len(parts) != 3 or not parts[0].isdigit():
        return None
    
    gv = int(parts[0])
    func = parts[1]
    attr = "_".join(parts[2:])
    
    if func not in VALID_AGG:
        raise ValueError(f"Invalid aggregate function: {func}")
    
    return AggregateToken(gv, func, attr)

def getFuncAgg(item):
    parsed = parseAggregate(item)
    return parsed.func if parsed else None