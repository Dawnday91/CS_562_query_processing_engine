import subprocess
#old test input you gave me. 
#  from is implied to the expression and so we assume it's always sales. it should be removed
#  where is supposed to be combined over every such that clause because it's implicit to every grouping attribute
#  each of the fields are in a very annoying form. I did a minor rewrite of them because it will be easier to translate in the parser than to decode here.
#input = {
#   'select': ['cust', 'prod', '1_avg_price', '2_sum_quant', '3_min_quant'], 
#   'from': ['sales'], 
#   'where': ["year = 2023 and region = 'east'"],
#   'n': '3', 'groupingAttribute': ['cust', 'prod'], 
#   'f_vect': ['1_avg_price', '2_sum_quant', '3_min_quant'], 
#   'suchThat': ["1.state='CT'", "2.state='NY'", "3.state='NJ'"], 
#   'having': ['2_sum_quant > 100 or 1_avg_price < 50 and 3_min_quant >= 5']}
"""
the most important change is that what you set suchThat and having to is correct injectable code. 
    no matter what, add the "row[blah]" stuff to every feature for suchThat
      and
    value._ to every f_vect in having

"""
#ideal input below
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

#actual working function that demonstrates how it should look
input = {
    'select': ['cust', 'prod', '1_avg_price', '2_sum_quant', '3_min_quant'],  
    'n': '3', 
    'groupingAttribute': ['cust', 'prod'], 
    'f_vect': ['1_avg_price', '2_sum_quant', '3_min_quant'], 
    'suchThat': ["row['day'] > 1 and row['month'] == 1 and row['state'] == 'CT'",
                "row['day'] > 1 and row['month'] == 1 and row['state'] == 'NY'",
                "row['day'] > 1 and row['month'] == 1 and row['state'] == 'NJ'"], 
    'having': 'value._2_sum_quant > 100 or value._1_avg_price < 50 and value._3_min_quant >= 5'}

#new test input to compare to previously calculated aggregates
input = {
    'select': ['cust', 'prod', '1_avg_price', '2_sum_quant', '3_min_quant'],
    'n': '3',
    'groupingAttribute': ['cust', 'prod'],
    'f_vect': ['1_avg_price', '2_sum_quant', '3_min_quant'],
    'suchThat': [
        "row['state'] == 'CT'",
        "row['quant'] > value._1_avg_price",
        "row['state'] == 'NJ'"
    ],
    'having': 'value._2_sum_quant > 0'
}

#sample query 1
#for each customer, 
#   get the customer, average quant where state is NY, and average quant where state is NJ
input = {'select': ['cust', '1_avg_quant', '2_avg_quant'], 'n': '2', 'groupingAttribute': ['cust'], 'f_vect': ['1_avg_quant', '2_avg_quant'], 'suchThat': ['row["state"] == \'NY\'', 'row["state"] == \'NJ\''], 'having': ['TRUE']}

#sample query 2
#for each product, compute the sum of sales when the day is after the 10th, the count of sales when the month is the 7th, and the minimum of sales when the year is before 2018
input = {'select': ['prod', '1_sum_sales', '2_count_sales', '3_min_sales'], 'n': '3', 'groupingAttribute': ['prod'], 'f_vect': ['1_sum_sales', '2_count_sales', '3_min_sales'], 'suchThat': ['row["day"] > 10', 'row["month"] == 7', 'row["year"] < 2018'], 'having': ['TRUE']}

#sample query 3
#for each product bought by the customer "Dan", compute the average quant of sales in new york, the average quant of sales in the first half of the year, and the product
input = {'select': ['prod', '1_avg_quant', '2_avg_quant'], 'n': '2', 'groupingAttribute': ['prod'], 'f_vect': ['1_avg_quant', '2_avg_quant'], 'suchThat': ['row["cust"] == \'Dan\' and row["state"] == \'NY\'', 'row["cust"] == \'Dan\' and row["month"] <= 6'], 'having': ['TRUE']}

#sample query 4
#for each customer, product pair, compute the average quant of sales in new york, and the average quant for sales in january
input = {'select': ['cust', 'prod', '1_avg_quant', '2_avg_quant'], 'n': '2', 'groupingAttribute': ['cust', 'prod'], 'f_vect': ['1_avg_quant', '2_avg_quant'], 'suchThat': ['row["state"]==\'NY\'', 'row["month"]==1'], 'having': ['TRUE']}

#sample query 5
#for each product and customer in new york, compute the count of sales and the average quant of sales for pairs that have an average price of at least 100
input = {'select': ['prod', 'cust', '1_count_sales', '2_avg_quant'], 'n': '2', 'groupingAttribute': ['prod', 'cust'], 'f_vect': ['1_count_sales', '2_avg_quant'], 'suchThat': ['row["state"]==\'NY\'', 'row["state"]==\'NY\''], 'having': ['values._2_avg_quant >= 100']}

#sample query 6
#for each customer product combination in new york, compute the average quant of sales and then the minimum quant of sales that are higher than that computed average, then output the rows that have that average quant of at least 200
#THIS IS WRONG. THE OUTPUT IS NOT ADDING THE 'value._' TO EVERYTHING
#incorrect output from program
input = {'select': ['cust', 'prod', '1_avg_quant', '2_min_quant'], 
         'n': '2', 'groupingAttribute': ['cust', 'prod'], 
         'f_vect': ['1_avg_quant', '2_min_quant'], 
         'suchThat': ['row["state"]==\'NY\'', 
                      'row["state"]==\'NY\' and row["quant"] > 1_avg_quant'], 
        'having': ['1_avg_quant_ny >= 200']}
#what it should be
input = {'select': ['cust', 'prod', '1_avg_quant', '2_min_quant'], 
         'n': '2', 'groupingAttribute': ['cust', 'prod'], 
         'f_vect': ['1_avg_quant', '2_min_quant'], 
         'suchThat': ['row["state"]==\'NY\'', 
                      'row["state"]==\'NY\' and row["quant"] > value._1_avg_quant'], 
        'having': ['1_avg_quant_ny >= 200']}

#this function computes a single loop for one grouping variable. aggType = "avg","sum","etc." iVal is the grouping variable index. vectVal is the name of the field itself
def generate(aggType, iVal, vectVal):
    output = f"""
            
    for key, value in mfTable.items():
        value.sum = 0
        value.count = 0
        value.min = float('inf')
        value.max = float('-inf')
    """
    match aggType:
        case "avg":
            conds = " and ".join( #make sure that the row matches the mf table key
                f"key.{attr} == row['{attr}']"
                for attr in input["groupingAttribute"]
            )
            input["suchThat"][iVal]
            output += f"""
    #avg
    for row in rows:
        for key, value in mfTable.items():
            if {conds}: #if row matches key
                if {input["suchThat"][iVal]}: #if we satisfy suchThat
                    value.sum += row["quant"] #compute aggregate
                    value.count += 1
                    value._{vectVal} = value.sum / value.count
                    #return
            """
        case "sum":
            conds = " and ".join(
                f"key.{attr} == row['{attr}']"
                for attr in input["groupingAttribute"]
            )
            output += f"""
    #sum
    for row in rows:
        for key, value in mfTable.items():
            if {conds}:
                if {input["suchThat"][iVal]}:
                    value.sum += row["quant"]
                    value._{vectVal} = value.sum
                    #return
            """
        case "count":
            conds = " and ".join(
                f"key.{attr} == row['{attr}']"
                for attr in input["groupingAttribute"]
            )
            output += f"""
    #count
    for row in rows:
        for key, value in mfTable.items():
            if {conds}:
                if {input["suchThat"][iVal]}:
                    value.count = value.count + 1
                    value._{vectVal} = value.count
                    #return
            """

        case "max":
            conds = " and ".join(
                f"key.{attr} == row['{attr}']"
                for attr in input["groupingAttribute"]
            )
            output += f"""
    #max
    for row in rows:
        for key, value in mfTable.items():
            if {conds}:
                if {input["suchThat"][iVal]}:
                    value.max = max(value.max, row["quant"])
                    value._{vectVal} = value.max
                    #return
            """
        
        case "min":
            conds = " and ".join(
                f"key.{attr} == row['{attr}']"
                for attr in input["groupingAttribute"]
            )
            output += f"""
    #min
    for row in rows:
        for key, value in mfTable.items():
            if {conds}:
                if {input["suchThat"][iVal]}:
                    value.min = min(value.min, row["quant"])
                    value._{vectVal} = value.min
                    #return
            """

    return output

    


def main(theInput):
    global input
    input = theInput
    """
    This is the generator code. It should take in the MF structure and generate the code
    needed to run the query. That generated code should be saved to a 
    file (e.g. _generated.py) and then run.
    """
    #input = {'select': ['cust', '1_avg_quant', '2_avg_quant'], 'n': '2', 'groupingAttribute': ['cust'], 'f_vect': ['1_avg_quant', '2_avg_quant'], 'suchThat': ['row["state"] == \'NY\'', 'row["state"] == \'NJ\''], 'having': ['TRUE']}
    
    #hardcoded in sample 6
    #input = {'select': ['cust', 'prod', '1_avg_quant', '2_min_quant'], 'n': '2', 'groupingAttribute': ['cust', 'prod'], 'f_vect': ['1_avg_quant', '2_min_quant'], 'suchThat': ['row["state"]==\'NY\'', 'row["state"]==\'NY\' and row["quant"] > value._1_avg_quant'], 'having': ['1_avg_quant_ny >= 200']}

    #print(input)
    
    mfValue = "[";
    for i in range (int(input["n"])):
        mfValue += "0, "
    mfValue = mfValue[:-2] + "]";

    #key for our mf table. contains grouping attributes
    keyDef = f"""
    class Key:
        def __init__(self, """
    params = ", ".join(input["groupingAttribute"])
    keyDef += params + "):\n"
    for attr in input["groupingAttribute"]:
        keyDef += f"            self.{attr} = {attr}\n"
    
    keyDef += """
        def __repr__(self):
            attrs = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
            return f"Key({attrs})"

        def __eq__(self, other):
            return isinstance(other, Key) and self.__dict__ == other.__dict__

        def __hash__(self):
            return hash(tuple(self.__dict__.values()))
    """
    #value for mf table. contains grouping variables
    rowDef = f"""
    class Row:
        def __init__(self,"""
    for agg in input["f_vect"]:
        aggType = agg.split("_", 1)[1].split("_")[0]
        match aggType:
            case "avg":
                me = "0"
            case "sum":
                me = "0"
            case "count":
                me = "0"
            case "min":
                me = "float('inf')"
            case "max":
                me = "float('-inf')"
        safe_name = "_" + agg   # prefix with underscore so it's a valid Python identifier
        rowDef += f"{safe_name}={me},"
    rowDef = rowDef[:-1] + "):\n"

    for agg in input["f_vect"]:
        safe_name = "_" + agg
        rowDef += f"            self.{safe_name} = {safe_name}\n"

    rowDef += "\n            self.sum = 0\n"
    rowDef += "            self.count = 0\n"
    rowDef += "            self.min = float('inf')\n"
    rowDef += "            self.max = float('-inf')\n"

    rowDef += """
        def __repr__(self):
            attrs = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
            return f"Row({attrs})"
"""


    body = f"""
    
    mfTable = {{}}
    groupingAttributes = {input["groupingAttribute"]}

    {keyDef}

    {rowDef}

    mfValue = {mfValue} 
    #int n = {input["n"]}

    #generate mf table

    for row in rows:
        #key = tuple(generateKey(groupingAttributes, row))
        key = Key(*[row[attr] for attr in {input["groupingAttribute"]}])
        if key not in mfTable:
            mfTable[key] = Row()
            #print(key)
    #print(mfTable)


    """
    #loop through and generate our scans for each grouping variable.
    for vect in input["f_vect"]:
        parts = vect.split("_", 1)   # ["1", "avg_price"]
        iVal = int(parts[0]) - 1    # grouping variable index (0-based)
        aggType = parts[1].split("_")[0]   # "avg", "sum", "min"
        #parsed.append((aggType, gv, vectVal))
        body += generate(aggType, iVal, vect)


    
    #body += generate("max", 0, "1_avg_price")
    
    #body += generate("min", 1, "2_sum_quant")

    #final part for the having clause and output
    body += f"""
    #having
    theOutput = []
    for key, value in mfTable.items():
        if {input["having"]}:
            theOutput.append((key, value))

    outputFR = []
    for key, value in theOutput:
        theRow = []
        for attr in {input["select"]}:
            if attr in {input["groupingAttribute"]}:
                theRow.append(getattr(key, attr))
            else:
                the = "_" + attr
                theRow.append(getattr(value, the))
        outputFR.append(theRow);
    """

    

    # Note: The f allows formatting with variables.
    #       Also, note the indentation is preserved.
    tmp = f"""
#test test hello
{input["select"]}
import os
import psycopg2
import psycopg2.extras
import tabulate
from dotenv import load_dotenv

# DO NOT EDIT THIS FILE, IT IS GENERATED BY generator.py

def generateKey(groupingAttributes, row):
    output = []
    for thing in groupingAttributes:
        output.append(row[thing])
    return output

def query():
    load_dotenv()

    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')

    conn = psycopg2.connect("dbname="+dbname+" user="+user+" password="+password,
                            cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales")
    
    rows = cur.fetchall()
    
    _global = []
    {body}
    
    return tabulate.tabulate(outputFR,
                        headers={input["select"]}, tablefmt="psql")


def main():
    print(query())

    
if "__main__" == __name__:
    main()
    """

    # Write the generated code to a file
    open("_generated.py", "w").write(tmp)
    # Execute the generated code
    #subprocess.run(["python", "_generated.py"])


if "__main__" == __name__:
    main(None)

def runMain(theInput):
    main(theInput)

"""
    def howIdDoIt():
    select 
        from
        where
        groupy by x, y  :  x.a, y.b
        having          


    mfTable = {}

    int numGroupByVars
    list groupByVars = ...
    
    generate groupyby table:
        for each row in realTable:
            if row not in mfTable:
                add to mfTable

    tableScannin:
        for each groupingVariable in groupByVars:
            for each row in table:
                if row satisfies WHERE clause:
                    if row satisfies SUCH THAT clause:
                        key = ...
                        if key in mfTable:
                            update mfTable
        
    output = []
    HAVING:
        for each in mfTable:
            if HAVING is satisfied:
                result.append whatever I need

    
"""
