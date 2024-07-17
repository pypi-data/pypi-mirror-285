from typing import Dict, List
from db_copilot.contract.api_core import APIManager
from db_copilot.contract.chat_core import InContextExample
from db_copilot.contract.db_core import SQLDialect

TSQL_EXAMPLES = [
    [
        {
            "question": "top 3 customers by total sales",
            "response": f"""
<Response>
<Cell>
To find the top 3 customers by total sales, we can calculate the total sales for each customer by summing the product of the quantity and list price for each order item, and then group by the customer_id. Here's the T-SQL query to achieve this:
</Cell>
<Cell>
```tsql code_id='1'
WITH [customer_sales] AS (
    SELECT
        o.[customer_id],
        SUM(oi.[quantity] * oi.[list_price] * (1 - oi.[discount])) AS [total_sales]
    FROM [sales].[orders] o
    JOIN [sales].[order_items] oi ON o.[order_id] = oi.[order_id]
    GROUP BY o.[customer_id]
)
SELECT TOP 3
    cs.[customer_id],
    c.[first_name],
    c.[last_name],
    cs.[total_sales]
FROM [customer_sales] cs
JOIN [sales].[customers] c ON cs.[customer_id] = c.[customer_id]
ORDER BY cs.[total_sales] DESC;
```
</Cell>
<Cell>
Now, let's create a bar chart to visualize the sales distribution among these top 3 customers.
</Cell>
<Cell>
```python code_id='2'
res = px.bar({APIManager.GET_CODE_RESULT.template.format(code_id='1')}, x='first_name', y='total_sales', title='Top 3 Customers by Total Sales').to_json()
```
</Cell>
<Cell>
The End
</Cell>
</Response>
""".strip()
        },
        {
            "question": "as pie chart",
            "response": f"""
<Response>
<Cell>
Now that we have the top 3 customers by total sales, let's create a pie chart.
</Cell>
<Cell>
```python code_id='3'
res = px.pie({APIManager.GET_CODE_RESULT.template.format(code_id='1')}, values='total_sales', names='first_name', title='Top 3 Customers by Total Sales').to_json()
```
</Cell>
<Cell>
The End
</Cell>
</Response>
""".strip()
        }
    ],
    [
        {
            "question": "sales by category, stacked bar chart",
            "response": f"""
<Response>
<Cell>
To create a stacked bar chart of sales by category, we first need to calculate the total sales for each category. We can do this by joining the `order_items`, `products`, and `categories` tables and then grouping by the category name. Here's the T-SQL query to get the sales data:
</Cell>
<Cell>
```tsql code_id='3'
SELECT
    c.[category_name],
    SUM(oi.[quantity] * oi.[list_price] * (1 - oi.[discount])) as [total_sales]
FROM [sales].[order_items] oi
JOIN [production].[products] p ON oi.[product_id] = p.[product_id]
JOIN [production].[categories] c ON p.[category_id] = c.[category_id]
GROUP BY c.[category_name]
ORDER BY [total_sales] DESC;
```
</Cell>
<Cell>
Now that we have the sales data for each category, let's create a stacked bar chart using Plotly. We will use the `category_name` as the x-axis and `total_sales` as the y-axis.
</Cell>
<Cell>
```python code_id='4'
res = px.bar({APIManager.GET_CODE_RESULT.template.format(code_id='3')}, x='category_name', y='total_sales', text='total_sales', labels={{'total_sales': 'Sales'}}, title='Sales by Category').to_json()
```
</Cell>
<Cell>
for each category. The highest sales are in the Mountain Bikes category, followed by Road Bikes and Cruisers Bicycles.
</Cell>
<Cell>
The End
</Cell>
</Response>
""".strip()
        },
        {
            "question": "pie chart",
            "response": f"""
<Response>
<Cell>
Let's create a pie chart using Plotly based on the previous question's data. We will use the category_name as the labels and total_sales as the values.
</Cell>
<Cell>
```python code_id='5'
res = px.pie({APIManager.GET_CODE_RESULT.template.format(code_id='3')}, values='total_sales', names='category_name', title='Sales by Category').to_json()
```
</Cell>
<Cell>
The End
</Cell>
</Response>
""".strip()
        }
    ],
    [
        {
            "question": "which customer buy the most",
            "response": """
<Response>
<Cell>
To find the customer who has made the most purchases, we can calculate the total quantity of products purchased by each customer. We can do this by joining the sales.orders, sales.order_items, and sales.customers tables. Here's the T-SQL query to find the customer who bought the most:
</Cell>
<Cell>
```tsql code_id='5'
SELECT TOP 1
    c.[customer_id],
    c.[first_name],
    c.[last_name],
    SUM(oi.[quantity]) as [total_quantity]
FROM
    [sales].[orders] o
JOIN [sales].[order_items] oi ON o.[order_id] = oi.[order_id]
JOIN [sales].[customers] c ON o.[customer_id] = c.[customer_id]
GROUP BY c.[customer_id], c.[first_name], c.[last_name]
ORDER BY [total_quantity] DESC;
```
</Cell>
<Cell>
The customer who bought the most is Tameka Fisher with a customer ID of 3. She purchased a total of 19 items.
</Cell>
<Cell>
The End
</Cell>
</Response>
""".strip()
        }
    ],
    [
        {
            "question": "why Marcelene Boyer sold most",
            "response": f"""
<Response>
<Cell>
To analyze why Marcelene Boyer sold the most, we can collect information about all salesmen's sales, including the products, categories, brands, and customers involved in their sales. Here's a T-SQL query to gather this information for all salesmen:
</Cell>
<Cell>
```tsql code_id='1'
SELECT
    s.[staff_id],
    s.[first_name],
    s.[last_name],
    c.[customer_id],
    c.[first_name] as [customer_first_name],
    c.[last_name] as [customer_last_name],
    p.[product_id],
    p.[product_name],
    p.[brand_id],
    b.[brand_name],
    p.[category_id],
    cat.[category_name],
    o.[order_id],
    oi.[item_id],
    oi.[quantity],
    oi.[list_price],
    oi.[discount],
    oi.[quantity] * oi.[list_price] * (1 - oi.[discount]) as [sales_amount]
FROM [sales].[orders] o
JOIN [sales].[order_items] oi ON o.[order_id] = oi.[order_id]
JOIN [sales].[staffs] s ON o.[staff_id] = s.[staff_id]
JOIN [sales].[customers] c ON o.[customer_id] = c.[customer_id]
JOIN [production].[products] p ON oi.[product_id] = p.[product_id]
JOIN [production].[brands] b ON p.[brand_id] = b.[brand_id]
JOIN [production].[categories] cat ON p.[category_id] = cat.[category_id];
```
</Cell>
<Cell>
The query above collects all the available information related to all salesmen's sales, including the products, categories, brands, and customers involved in their sales. Now we use this data to analyze why Marcelene Boyer sold the most and compare her performance with other salesmen. Here's the Python code to analyze the data and find out why she sold the most:
</Cell>
<Cell>
```python code_id='2'
import pandas as pd
import numpy as np
from scipy import stats

def analyze_sales(df):
    # Filter data for Marcelene Boyer
    marcelene_df = df[df['first_name'] == 'Marcelene']

    # Calculate total sales for each staff member
    staff_sales = df.groupby(['staff_id', 'first_name', 'last_name'])['sales_amount'].sum().reset_index()

    # Sort staff members by total sales
    staff_sales_sorted = staff_sales.sort_values(by='sales_amount', ascending=False)

    # Calculate the average sales amount for each product category
    category_sales = df.groupby(['category_name'])['sales_amount'].mean().reset_index()

    # Calculate the average sales amount for each brand
    brand_sales = df.groupby(['brand_name'])['sales_amount'].mean().reset_index()

    # Calculate the average sales amount for each product
    product_sales = df.groupby(['product_name'])['sales_amount'].mean().reset_index()

    # Calculate the average discount for each staff member
    staff_discount = df.groupby(['staff_id', 'first_name', 'last_name'])['discount'].mean().reset_index()

    # Calculate the average quantity sold for each staff member
    staff_quantity = df.groupby(['staff_id', 'first_name', 'last_name'])['quantity'].mean().reset_index()

    # Calculate the average sales amount for each customer
    customer_sales = df.groupby(['customer_id', 'customer_first_name', 'customer_last_name'])['sales_amount'].mean().reset_index()

    # Print the results
    print("Top Sales Staff:")
    print(staff_sales_sorted.head())
    print() # Print a blank line

    print("Average Sales Amount by Category:")
    print(category_sales)
    print() 

    print("Average Sales Amount by Brand:")
    print(brand_sales)
    print()

    print("Average Sales Amount by Product:")
    print(product_sales)
    print()

    print("Average Discount by Staff:")
    print(staff_discount)
    print()

    print("Average Quantity Sold by Staff:")
    print(staff_quantity)
    print()

    print("Average Sales Amount by Customer:")
    print(customer_sales)

df={APIManager.GET_CODE_RESULT.template.format(code_id='1')}
df = preprocess_dataframe(df)
# Call the analyze_sales function with the input DataFrame
analyze_sales(df)
```
</Cell>
<Cell>
Marcelene Boyer sold the most compared to other sales staff for several reasons. Here are some key factors that contributed to her high sales performance:

1. Higher average discount: Marcelene offered a slightly higher average discount (10.8%) on her sales compared to other sales staff. This could have attracted more customers and encouraged them to make purchases.

2. Product selection: The products Marcelene sold had a higher average sales amount compared to other staff members. This means that the items she sold were generally more expensive, which could have contributed to her higher total sales amount.

3. Quantity sold: Marcelene sold an average of 1.5 items per sale, which is slightly higher than some of her colleagues. This indicates that she was able to sell more items per transaction, leading to a higher overall sales amount.

4. Customer base: Marcelene's customers had a higher average sales amount compared to other staff members' customers. This suggests that she was able to attract customers who were willing to spend more on their purchases.

In summary, Marcelene Boyer's high sales performance can be attributed to her ability to offer higher discounts, sell more expensive products, sell more items per transaction, and attract customers who were willing to spend more on their purchases.
</Cell>
<Cell>
The End
</Cell>
</Response>
""".strip()
        }
    ]
]


SQLITE_EXAMPLES = [
    [
        {
            "question": "top 3 customers by total sales",
            "response": f"""
<Response>
<Cell>
To find the top 3 customers by total sales, we can calculate the total sales for each customer by summing the product of the quantity and list price for each order item, and then group by the customer_id. Here's the SQL query to achieve this:
</Cell>
<Cell>
```sqlite code_id='1'
WITH [customer_sales] AS (
    SELECT
        o.[customer_id],
        SUM(oi.[quantity] * oi.[list_price] * (1 - oi.[discount])) AS [total_sales]
    FROM [orders] o
    JOIN [order_items] oi ON o.[order_id] = oi.[order_id]
    GROUP BY o.[customer_id]
)
SELECT
    cs.[customer_id],
    c.[first_name],
    c.[last_name],
    cs.[total_sales]
FROM [customer_sales] cs
JOIN [customers] c ON cs.[customer_id] = c.[customer_id]
ORDER BY cs.[total_sales] DESC
LIMIT 3;
```
</Cell>
<Cell>
Now, let's create a bar chart to visualize the sales distribution among these top 3 customers.
</Cell>
<Cell>
```python code_id='2'
res = px.bar({APIManager.GET_CODE_RESULT.template.format(code_id='1')}, x='first_name', y='total_sales', title='Top 3 Customers by Total Sales').to_json()
```
</Cell>
<Cell>
The End
</Cell>
</Response>
""".strip()
        },
        {
            "question": "as pie chart",
            "response": f"""
<Response>
<Cell>
Now that we have the top 3 customers by total sales, let's create a pie chart.
</Cell>
<Cell>
```python code_id='3'
res = px.pie({APIManager.GET_CODE_RESULT.template.format(code_id='1')}, values='total_sales', names='first_name', title='Top 3 Customers by Total Sales').to_json()
```
</Cell>
<Cell>
The End
</Cell>
</Response>
""".strip()
        }
    ],
    [
        {
            "question": "sales by category, stacked bar chart",
            "response": f"""
<Response>
<Cell>
To create a stacked bar chart of sales by category, we first need to calculate the total sales for each category. We can do this by joining the `order_items`, `products`, and `categories` tables and then grouping by the category name. Here's the SQL query to get the sales data:
</Cell>
<Cell>
```sqlite code_id='3'
SELECT
    c.[category_name],
    SUM(oi.[quantity] * oi.[list_price] * (1 - oi.[discount])) as [total_sales]
FROM [order_items] oi
JOIN [products] p ON oi.[product_id] = p.[product_id]
JOIN [categories] c ON p.[category_id] = c.[category_id]
GROUP BY c.[category_name]
ORDER BY [total_sales] DESC;
```
</Cell>
<Cell>
Now that we have the sales data for each category, let's create a stacked bar chart using Plotly. We will use the `category_name` as the x-axis and `total_sales` as the y-axis.
</Cell>
<Cell>
```python code_id='4'
res = px.bar({APIManager.GET_CODE_RESULT.template.format(code_id='3')}, x='category_name', y='total_sales', text='total_sales', labels={{'total_sales': 'Sales'}}, title='Sales by Category').to_json()
```
</Cell>
<Cell>
for each category. The highest sales are in the Mountain Bikes category, followed by Road Bikes and Cruisers Bicycles.
</Cell>
<Cell>
The End
</Cell>
</Response>
""".strip()
        },
        {
            "question": "pie chart",
            "response": f"""
<Response>
<Cell>
Let's create a pie chart using Plotly based on the previous question's data. We will use the category_name as the labels and total_sales as the values.
</Cell>
<Cell>
```python code_id='5'
res = px.pie({APIManager.GET_CODE_RESULT.template.format(code_id='3')}, values='total_sales', names='category_name', title='Sales by Category').to_json()
```
</Cell>
<Cell>
The End
</Cell>
</Response>
""".strip()
        }
    ],
    [
        {
            "question": "which customer buy the most",
            "response": """
<Response>
<Cell>
To find the customer who has made the most purchases, we can calculate the total quantity of products purchased by each customer. We can do this by joining the sales.orders, sales.order_items, and sales.customers tables. Here's the SQL query to find the customer who bought the most:
</Cell>
<Cell>
```sqlite code_id='5'
SELECT
    c.[customer_id],
    c.[first_name],
    c.[last_name],
    SUM(oi.[quantity]) as [total_quantity]
FROM
    [orders] o
JOIN [order_items] oi ON o.[order_id] = oi.[order_id]
JOIN [customers] c ON o.[customer_id] = c.[customer_id]
GROUP BY c.[customer_id], c.[first_name], c.[last_name]
ORDER BY [total_quantity] DESC
LIMIT 1;
```
</Cell>
<Cell>
The customer who bought the most is Tameka Fisher with a customer ID of 3. She purchased a total of 19 items.
</Cell>
<Cell>
The End
</Cell>
</Response>
""".strip()
        }
    ]
]


KQL_EXAMPLES = [
    [
        {
            "question": "top 3 customers by total sales from 2020-01-01 to 2020-01-31",
            "response": f"""
<Response>
<Cell>
To find the top 3 customers by total sales between January 1, 2020, and January 31, 2020, you can use the following KQL query:
</Cell>
<Cell>
```kql code_id='1'
CustomersSales
| where timestamp between(datetime("2020-01-01") .. datetime("2020-01-31"))
| sort by sales desc
| take 3
| project name, sales
```
</Cell>
<Cell>
The top 3 customers by total sales are: Sharyn Hopkins, Pamelia Newman, and Abby Gamble. Let's create a bar chart using Plotly:
</Cell>
<Cell>
```python code_id='2'
res = px.bar({APIManager.GET_CODE_RESULT.template.format(code_id='1')}, x='name', y='sales', title='Top 3 Customers by Total Sales in January 2020').to_json()
```
</Cell>
<Cell>
The End
</Cell>
</Response>
""".strip()
        }
    ],
    [
        {
            "question": "How many tables are there in this database?",
            "response": """
<Response>
<Cell>
To find the total number of tables in this database, you can use the following KQL query:
</Cell>
<Cell>
```kql code_id='1'
.show tables
| count
```
</Cell>
<Cell>
There are 2 tables in this database: Staffs and Stores.
</Cell>
<Cell>
The End
</Cell>
</Response>
""".strip()
        }
    ]
]


ONLY_SQL_EXAMPLES = [
    {
        "question": "What is the highest eligible free rate for K-12 students in the schools in Alameda County?",
        SQLDialect.TSQL.value: """
SELECT TOP 1 [Eligible_Free_Rate]  
FROM [Schools]  
WHERE [County] = 'Alameda' AND [Grade_Level] = 'K-12'  
ORDER BY [Eligible_Free_Rate] DESC;
""".strip(),
        SQLDialect.SQLITE.value: """
SELECT [Eligible_Free_Rate]  
FROM [Schools]  
WHERE [County] = 'Alameda' AND [Grade_Level] = 'K-12'  
ORDER BY [Eligible_Free_Rate] DESC  
LIMIT 1;
""".strip(),
        SQLDialect.KQL.value: """
Schools  
| where County == 'Alameda' and Grade_Level == 'K-12'  
| top 1 by Eligible_Free_Rate desc  
| project Eligible_Free_Rate;
"""
    },
    {  
        "question": "Give phishing attempts over email that did not use identity imitation between 20:54:33 and 21:05:12 on 2022-10-05.",  
        SQLDialect.TSQL.value: """  
SELECT *  
FROM [EmailEvents]  
WHERE [Timestamp] BETWEEN '2022-10-05T20:54:33' AND '2022-10-05T21:05:12'  
AND CHARINDEX('Phish', [ThreatTypes]) > 0  
AND [EmailActionPolicy] != 'Anti-phishing user impersonation';  
""".strip(),  
        SQLDialect.SQLITE.value: """  
SELECT *  
FROM [EmailEvents]  
WHERE strftime('%Y-%m-%dT%H:%M:%S', [Timestamp]) BETWEEN '2022-10-05T20:54:33' AND '2022-10-05T21:05:12'  
AND instr([ThreatTypes], 'Phish') > 0  
AND [EmailActionPolicy] != 'Anti-phishing user impersonation';  
""".strip(),  
        SQLDialect.KQL.value: """  
EmailEvents  
| where Timestamp between(datetime("2022-10-05T20:54:33Z") .. datetime("2022-10-05T21:05:12Z"))  
| where ThreatTypes has "Phish"  
| where EmailActionPolicy != "Anti-phishing user impersonation"  
""".strip()
    },
    {
        "question": "How many schools with an average score in Math under 400 in the SAT test are exclusively virtual?",  
        SQLDialect.TSQL.value: """  
SELECT COUNT(DISTINCT T2.[School])    
FROM [satscores] AS T1    
INNER JOIN [schools] AS T2 ON T1.[cds] = T2.[CDSCode]    
WHERE T2.[Virtual] = 'F' AND T1.[AvgScrMath] < 400;  
""".strip(),  
        SQLDialect.SQLITE.value: """  
SELECT COUNT(DISTINCT T2.[School])    
FROM [satscores] AS T1    
INNER JOIN [schools] AS T2 ON T1.[cds] = T2.[CDSCode]    
WHERE T2.[Virtual] = 'F' AND T1.[AvgScrMath] < 400;  
""".strip(),  
        SQLDialect.KQL.value: """  
satscores    
| join kind=inner schools on cds == CDSCode    
| where Virtual == 'F' and AvgScrMath < 400    
| summarize count(distinct(School))
""".strip()
    },
    {  
        "question": "Which molecule consisted of Sulphur atom with double bond?",  
        SQLDialect.TSQL.value: """  
SELECT DISTINCT T1.[molecule_id]  
FROM [atom] AS T1  
INNER JOIN [bond] AS T2 ON T1.[molecule_id] = T2.[molecule_id]  
WHERE T1.[element] = 'S' AND T2.[bond_type] = '=';  
""".strip(),  
        SQLDialect.SQLITE.value: """  
SELECT DISTINCT T1.[molecule_id]  
FROM [atom] AS T1  
INNER JOIN [bond] AS T2 ON T1.[molecule_id] = T2.[molecule_id]  
WHERE T1.[element] = 'S' AND T2.[bond_type] = '=';  
""".strip(),  
        SQLDialect.KQL.value: """  
atom  
| join kind=inner bond on molecule_id  
| where element == 'S' and bond_type == '='  
| summarize by molecule_id;  
""".strip()  
    },
    {  
        "question": "Describe the inspection types and violation descriptions under moderate risk category for ART's CAFÉ.",  
        SQLDialect.TSQL.value: """  
SELECT DISTINCT T2.[type], T1.[description]  
FROM [violations] AS T1  
INNER JOIN [inspections] AS T2 ON T1.[business_id] = T2.[business_id]  
INNER JOIN [businesses] AS T3 ON T2.[business_id] = T3.[business_id]  
WHERE T3.[name] = 'ART''S CAFÉ' AND T1.[risk_category] = 'Moderate Risk';  
    """.strip(),  
        SQLDialect.SQLITE.value: """  
SELECT DISTINCT T2.[type], T1.[description]  
FROM [violations] AS T1  
INNER JOIN [inspections] AS T2 ON T1.[business_id] = T2.[business_id]  
INNER JOIN [businesses] AS T3 ON T2.[business_id] = T3.[business_id]  
WHERE T3.[name] = 'ART''S CAFÉ' AND T1.[risk_category] = 'Moderate Risk';  
    """.strip(),  
        SQLDialect.KQL.value: """  
violations  
| join kind=inner inspections on business_id  
| join kind=inner businesses on business_id  
| where name == "ART's CAFÉ" and risk_category == 'Moderate Risk'  
| summarize by type, description;  
    """.strip()  
    },
    {  
        "question": "Among the cards that doesn't have multiple faces on the same card, who is the illustrator of the card art that has the highest cost of converted mana?",  
        SQLDialect.TSQL.value: """  
SELECT [artist]  
FROM [cards]  
WHERE [side] IS NULL AND [convertedmanacost] = (  
    SELECT MAX([convertedmanacost])  
    FROM [cards]  
    WHERE [side] IS NULL  
);  
""".strip(),  
        SQLDialect.SQLITE.value: """  
SELECT [artist]  
FROM [cards]  
WHERE [side] IS NULL AND [convertedmanacost] = (  
    SELECT MAX([convertedmanacost])  
    FROM [cards]  
    WHERE [side] IS NULL  
);  
""".strip(),  
        SQLDialect.KQL.value: """  
cards  
| where isnull(side)  
| extend max_converted_mana_cost = toscalar(cards | where isnull(side) | summarize max(convertedmanacost))  
| where convertedmanacost == max_converted_mana_cost  
| project artist;  
""".strip()  
    },
    {  
        "question": "What is the average number of complaints on credit cards filed by clients from New York in the 3 consecutive years starting from 2015?",  
        SQLDialect.TSQL.value: """  
SELECT CAST(COUNT(T2.[Complaint ID]) AS FLOAT) / 3 AS [average]  
FROM [client] AS T1  
INNER JOIN [events] AS T2 ON T1.[client_id] = T2.[Client_ID]  
WHERE YEAR(T2.[Date received]) BETWEEN 2015 AND 2017 AND T1.[city] = 'New York City' AND T2.[Product] = 'Credit card';  
    """.strip(),  
        SQLDialect.SQLITE.value: """  
SELECT CAST(COUNT(T2.[Complaint ID]) AS REAL) / 3 AS [average]  
FROM [client] AS T1  
INNER JOIN [events] AS T2 ON T1.[client_id] = T2.[Client_ID]  
WHERE strftime('%Y', T2.[Date received]) BETWEEN '2015' AND '2017' AND T1.[city] = 'New York City' AND T2.[Product] = 'Credit card';  
    """.strip(),  
        SQLDialect.KQL.value: """  
client  
| join kind=inner events on client_id  
| where format_datetime(['Date received'], 'yyyy') between "2015" and "2017" and city == "New York City" and Product == "Credit card"  
| summarize count(['Complaint ID']) / 3 as average;  
    """.strip()  
    }  
]

def convert_sessions(sessions: List[List]) -> List[InContextExample]:
    examples = []
    for session in sessions:
        examples.append(InContextExample(
            embed_text=session[0]['question'],
            prompt_text="\n\n".join(f"<Question>\n{item['question']}\n</Question>\n{item['response'].strip()}" for item in session)
        ))
    return examples


def convert_sql_examples(sql_examples: List[Dict], dialect: SQLDialect) -> List[InContextExample]:
    examples = []
    for example in sql_examples:
        examples.append(InContextExample(
            embed_text=example['question'],
            prompt_text=f"<Question>\n{example['question']}\n</Question>\n<Response>\n<Cell>\n```{dialect.value}\n{example[dialect.value]}\n```\n</Cell>\n<Cell>\nThe End\n</Cell></Response>"
        ))
    return examples


def get_examples(dialect: SQLDialect, with_extensions: bool=True) -> List[InContextExample]:
    if with_extensions:
        if dialect == SQLDialect.TSQL:
            return convert_sessions(TSQL_EXAMPLES[:-1])
        elif dialect == SQLDialect.SQLITE:
            return convert_sessions(SQLITE_EXAMPLES)
        elif dialect == SQLDialect.KQL:
            return convert_sessions(KQL_EXAMPLES)
        else:
            raise NotImplementedError(f'In-context examples for {dialect} (with extensions) has not been implemented')
    else:
        if dialect == SQLDialect.TSQL:
            return convert_sql_examples(ONLY_SQL_EXAMPLES, dialect)
        elif dialect == SQLDialect.SQLITE:
            return convert_sql_examples(ONLY_SQL_EXAMPLES, dialect)
        elif dialect == SQLDialect.KQL:
            return convert_sql_examples(ONLY_SQL_EXAMPLES, dialect)
        else:
            raise NotImplementedError(f'In-context examples for {dialect} (without extensions) has not been implemented')