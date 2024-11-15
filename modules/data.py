import pandas as pd

def get_dataframe(data):
    for item in data:
        if isinstance(item.get("authors"), list):
            item["authors"] = ", ".join(item["authors"])  # Junta autores em uma única string
        if isinstance(item.get("cited_by"), list):
            item["cited_by"] = "; ".join(item["cited_by"])  # Junta referências em uma única string
    df = pd.DataFrame(data)
    # print(df.head())  # Para verificar o DataFrame
    # print(df)
    return df