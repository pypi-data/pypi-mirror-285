import pandas as pd


# TODO: is the following code enought to convert a dataframe to known types?
def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.columns:
        for c_type in [float, str]:
            try:
                df[column] = df[column].astype(
                    c_type)
                break
            except ValueError:
                continue
            except TypeError:
                try:
                    df[column] = df[column].astype(str)
                    break
                except ValueError:
                    continue

    return df
