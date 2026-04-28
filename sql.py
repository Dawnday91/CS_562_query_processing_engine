import os
import psycopg2
import psycopg2.extras
import tabulate
from parser import parseInput, write_output
from dotenv import load_dotenv


def query():
    """
    Used for testing standard queries in SQL.
    """
    load_dotenv()

    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')

    conn = psycopg2.connect("dbname="+dbname+" user="+user+" password="+password,
                            cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales WHERE quant > 10")

    return tabulate.tabulate(cur.fetchall(), headers="keys", tablefmt="psql")


def main():
    test_input = """
    SELECT ATTRIBUTE(S):
    cust, 1_avg_price, 2_sum_quant, 3_min_quant
    FROM:
    sales
    WHERE:
    year = 2023 and region = 'east'
    NUMBER OF GROUPING VARIABLES(n):
    3
    GROUPING ATTRIBUTES(V):
    cust
    F-VECT([F]):
    1_avg_price, 2_sum_quant, 3_min_quant
    SELECT CONDITION-VECT([σ]):
    1.state='CA'
    2.state='TX'
    3.state='FL'
    HAVING_CONDITION(G):
    2_sum_quant > 100 or 1_avg_price < 50 and 3_min_quant >= 5
    """

    tokenDict = parseInput(test_input)

    print("Parsed dict:")
    print(tokenDict)

    print("\nGenerated query:")
    print(write_output(tokenDict))
    "print(query())"


if "__main__" == __name__:
    main()
