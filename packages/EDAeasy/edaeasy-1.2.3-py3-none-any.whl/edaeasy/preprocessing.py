import pandas as pd


def convertir_tipos_columnas(
    df: pd.DataFrame, cat_cols: list = None, bool_cols: list = None
) -> pd.DataFrame:
    """
    Convierte el tipo de columnas en un DataFrame a 'categorical' o 'bool' según las listas proporcionadas.

    Parameters:
    df (pd.DataFrame): El DataFrame que contiene los datos.
    cat_cols (list): Lista de nombres de columnas a convertir a 'categorical'.
    bool_cols (list): Lista de nombres de columnas a convertir a 'bool'.

    Returns:
    pd.DataFrame: DataFrame con los cambios de tipo aplicados.
    """
    if cat_cols:
        for col in cat_cols:
            if col in df.columns:
                df[col] = df[col].astype("category")
            else:
                print(f"La columna '{col}' no existe en el DataFrame.")

    if bool_cols:
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].astype("bool")
            else:
                print(f"La columna '{col}' no existe en el DataFrame.")

    return df
