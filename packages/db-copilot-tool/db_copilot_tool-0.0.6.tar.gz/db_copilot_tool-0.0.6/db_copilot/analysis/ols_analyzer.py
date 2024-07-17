import json
from typing import List, Tuple

import pandas as pd

from db_copilot.analysis.analysis_com import Analyzer


class OrdinaryLeastSquaresAnalyzer(Analyzer):
    '''Ordinary Least Squares'''

    def get_analysis_info(self, df: pd.DataFrame, evidences: List[Tuple[str, str]], **kwargs) -> str:
        select_columns_response = next(self.llm.complete(prompt=self.prompt_text_inner(
            df), stop=["```"], temperature=0, stream=False))
        select_columns_result = json.loads(select_columns_response)

        selected_columns = select_columns_result['selected_columns']
        target_column_name = select_columns_result['target_column_name']

        # TODO: what if the target_column_name contains ~ or +
        formula = f'{target_column_name} ~ {" + ".join([col for col in selected_columns if col != target_column_name])}'
        import statsmodels.formula.api as smf
        model = smf.ols(formula, data=df).fit()

        description = f'Here is the Ordinary Least Square analysis on the relation between {target_column_name} and {" ".join(selected_columns)}'
        result = str(model.summary())
        evidences.append((description, result))

        return f"""{description}
The formula is {formula} and the ols model from the statsmodels.api package.
{result}""".strip()

    def prompt_text_inner(self, df: pd.DataFrame) -> str:
        return f"""{self.get_base_prompt(df)}
please select one column that user cares and columns that you want to use for data analysis using the ordinary least squares model from the statsmodels.api package. The results should be a json string with the following format:
```json
{{
    "target_column_name": "column_name",
    "selected_columns": ["column_name1", "column_name2"]
}}
```
-------------
Here are some instructions for you to select columns:
    - please keep as much as columns as possible, particularly the columns that are date or number type. 
    - Make sure the selected columns are relevant to the target column. 
    - Do not select columns that are ids or primary keys, e.g., user_id, order_id should not be selected.
The current user query is 
{self.query}.
The corresponding json is:
```json
""".strip()
