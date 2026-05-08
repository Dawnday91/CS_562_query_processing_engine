from helper import parseAggregate, positiveIntCheck, normalizeItems

ALIAS = {1:"x",2:"y",3:"z",4:"a",5:"b"}
KEYWORDS = {
        "SELECT ATTRIBUTE(S)":"select",
        "NUMBER OF GROUPING VARIABLES(n)":"n",
        "GROUPING ATTRIBUTES(V)":"groupingAttribute",
        "F-VECT([F])":"f_vect",
        "SELECT CONDITION-VECT([σ])":"suchThat",
        "HAVING_CONDITION(G)":"having",
    }

#input = {
#    'select': ['cust', 'prod', '1_avg_price', '2_sum_quant', '3_min_quant'],  
#    'n': '3', 
#   'groupingAttribute': ['cust', 'prod'], 
#  'f_vect': ['1_avg_price', '2_sum_quant', '3_min_quant'], 
# 'suchThat': ["row['year'] == 2023 and row['region'] == 'east' and row['state'] == 'CT'",
#            "row['year'] == 2023 and row['region'] == 'east' and row['state'] == 'NY'",
#           "row['year'] == 2023 and row['region'] == 'east' and row['state'] == 'NJ'"], 
#    'having': 'value._2_sum_quant > 100 or value._1_avg_price < 50 and value._3_min_quant >= 5'}
#note that this will not run because the where clause is incompatible with the sales schema, this is just example

def parseInput(item):
    queryLine = {}
    lines = [line.strip() for line in item.splitlines() if line.strip()]
    
    i=0
    while i <len(lines):
        line = lines[i].rstrip(":")
        if line in KEYWORDS:
            key = KEYWORDS[line]
            i+=1
            values = []
            while i < len(lines) and lines[i].rstrip(":") not in KEYWORDS:
                values.append(lines[i])
                i+=1
            if key in ['select','groupingAttribute','f_vect']:
                queryLine[key]= [
                    item.strip() 
                    for v in values 
                    for item in v.split(",") 
                    if item.strip()
                ]
            elif key == "n":
                queryLine[key] = values[0] if values else None
            else: 
                queryLine[key] = values
        else:
            i+=1
    return queryLine
    
    
def syntaxCheckerNorm(item):
    reqBase = {'select'}
    reqGv = {"n", "groupingAttribute", "f_vect", "suchThat", "having"}
    
    missing = [key for key in reqBase if not item.get(key)]
    if missing:
        raise KeyError(f"Missing required sections(s): {missing}")
    
    gv = bool(item.get("groupingAttribute"))

    if not gv:
        return True

    missingGv = [key for key in reqGv if not item.get(key)]
    if missingGv:
        raise KeyError(f"Missing GV section(s): {missingGv}")
    
    syntaxCheckerGv(item)
    
    return True;

def syntaxCheckerGv(item):
    n = positiveIntCheck(item['n'],'n')
    gv = item['groupingAttribute']
    
    if n > len(ALIAS):
        raise ValueError("number of provided grouping variables does not match upto n")
    
    if len(item.get("suchThat", [])) != n:
        raise ValueError(
            f"n={n}, but found {len(item.get('suchThat', []))} such-that condition(s)"
        )

    for value in item["select"]:
        token = parseAggregate(value)

        if token:
            if token.gv < 1 or token.gv > n:
                raise ValueError(
                    f"{value} uses grouping variable {token.gv}, but n={n}"
                )
        elif value not in gv:
            raise ValueError(
                f"{value} is in SELECT but not in grouping attribute section"
            )

def write_output(tokenDict):
    output = []
    syntaxCheckerNorm(tokenDict)
    """with token from parse item and syntax checker being ran handle the token output"""
    selectInput = [normalizeItems(item) for item in tokenDict["select"]]
    output.append(f"select: {', '.join(selectInput)}")
    output.append("from sales")
    output.append("where ,")
    if tokenDict.get("groupingAttribute"):
        n = int(tokenDict['n'])
        aliases = [ALIAS[i] for i in range(1,n+1)]
        output.append(f"group by {', '.join(tokenDict['groupingAttribute'])}: {', '.join(aliases)}")

    if tokenDict.get("suchThat"):
        conditions = []
        
        for i, cond in enumerate(tokenDict["suchThat"],start=1):
            alias = ALIAS[i]
            conditions.append(cond.replace(f"{i}.",f"{alias}."))
        output.append(f"such that {conditions[0]}")
        for cond in conditions[1:]:
            output.append(f"and {cond}")
            
    if tokenDict.get("having"):
        attr = tokenDict["having"][0]
        
        for aggr in tokenDict["f_vect"]:
            token = parseAggregate(aggr)
            if token:
                attr = attr.replace(aggr,token.sqlVer)
        output.append(f"having {attr};")
    
    return "\n".join(output)


def UserInput():
    print ("Choose input method:")
    print ("1) Manual Input")
    print ("2) File Input")
    choice = input("Input option (1 or 2):").strip()
    
    if choice == "1":
        print("Paste your query below.")
        print("Type END on a new line when finished:\n")

        lines = []

        while True:
            line = input()

            if line.strip().upper() == "END":
                break

            lines.append(line)

        queryText = '\n'.join(lines).strip()
        
        if not queryText:
            return tuple()

        return (parseInput(queryText),)
    
    elif choice == "2":
        path = input("Enter file path: ").strip()

        try:
            queries = []
            currentQuery = []
            with open(path, "r", encoding="utf-8") as file:
                for line in file:
                    if line.strip().upper()=='END':
                        queryText = "\n".join(currentQuery).strip()
                        
                        if queryText:
                            queries.append(parseInput(queryText))
                    
                        currentQuery = []
                    else:
                        currentQuery.append(line.rstrip("\n"))
                
            if currentQuery:
                queryText = '\n'.join(currentQuery).strip()
                if queryText:
                    queries.append(parseInput(queryText))
        
            return tuple(queries)

        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find file: {path}")

    else:
        raise ValueError("Invalid option selected")