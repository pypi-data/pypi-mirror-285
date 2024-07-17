import logging
from typing import List

from db_copilot.contract.llm_core import LLM

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class SuggestionGenerationSkill:
    def __init__(self, llm: LLM, num_suggestions: int = 3) -> None:
        self.llm = llm
        self.num_suggestions = num_suggestions

    def generate(self, schema: str, queryHistory: List[str], num: int, creative = False) -> List[str]:
        if not num:
            num = self.num_suggestions

        prev_queries = '\n'.join(queryHistory)

        suggestion_examples = [
'''
<Previous Query>
total sales
</Previous Query>

<Suggestion>
total sales by category as a bar chart
top 2 year by total sales
sales trend
</Suggestion>
''',
'''
<Previous Query>
total sales
top 2 year by total sales
</Previous Query>

<Suggestion>
top 2 year by average rating
total sales for each year as line chart
average sales over time
</Suggestion>
''',
'''
<Previous Query>
total sales
top 2 year by total sales
total sales by category
</Previous Query>

<Suggestion>
distribution of category as a pie chart
how many different category are there?
sort brand by total sales in ascending order
</Suggestion>
'''
        ]

        mode_templates = {
            True: {
                "examples": "Please try to generate challenging and complex questions that are hard to answer.",
                "query_constraints": ""
            },
            False: {
                "examples": f'''
Here is an example database:
<DatabaseInfo>
Table name is "mytable_sample",
Row count is "3",
+----+----------+---------------------+------------+------------+---------+----------+
|    |   row_id | Year                | Category   | Product    |   Sales |   Rating |
|----+----------+---------------------+------------+------------+---------+----------|
|  0 |        0 | 2017-01-01 00:00:00 | Components | Chains     |   20000 |     0.75 |
|  1 |        1 | 2015-01-01 00:00:00 | Clothing   | Socks      |    3700 |     0.22 |
|  2 |        2 | 2017-01-01 00:00:00 | Clothing   | Bib-Shorts |    4000 |     0.22 |
+----+----------+---------------------+------------+------------+---------+----------+
</DatabaseInfo>

{suggestion_examples[max(0, min(len(queryHistory), len(suggestion_examples)) - 1)]}
''',
                "query_constraints": '''- Each suggested query should be natural, not verbose, and with less than 10 words.
- Each suggested query should contain 1 or 2 columns in the given database.
'''
            }
        }

        prompt = f'''
Task:
Given the database schema, generate some useful data analysis queries.

Here are some rules that the output should follow:
- In the <Suggestion>...</Suggestion> block, there should be {num} diverse data analysis queries.
- Each line has only one suggested query.
- Each line should start with a English letter.
- Only need text query and do not contain any SQL in the suggestions.
- It's better to generate questions related with the last previous query.
- These {num} data analysis queries should have different prefixes, i.e., the first word of each suggestions are different.
- It's better that one of these query suggests chart, for example, as a bar chart.
{mode_templates[creative]["query_constraints"]}

Please remember very important things below:
- Don't generate duplicate suggestions.
- Don't generate any suggestion which is included in previous queries.
- Don't generate the same pattern suggestions.
- Don't add "." at the end of each line.
- Don't use some subjective words like "best", "worst", "most popular".
- Don't use any offensive term.

{mode_templates[creative]["examples"]}

Now let's start.

<DatabaseInfo>
{schema}
</DatabaseInfo>

<Previous Query>
{prev_queries}
</Previous Query>

<Suggestion>
'''
        try:
            oaiReply : str = list(self.llm.chat(messages=None, prompt=prompt, stop=['</Suggestion>'], stream=False))[0]
        except StopIteration:
            return []
        query_lst = [x.strip() for x in oaiReply.split("\n")]
        query_lst = [x for x in query_lst if x != ""]

        logger.info('Sample Query Generated in {}: {}'.format("Free style" if creative else "Normal style", query_lst))

        if len(query_lst) >= num:
            return [{"name": x, 'isHighlight':True} for x in query_lst[:num]]

        return []