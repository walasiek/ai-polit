def df_to_list_of_lists(df, column_names):
    return df[column_names].values.tolist()
