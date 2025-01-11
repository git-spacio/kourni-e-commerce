import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.seasonal import seasonal_decompose
import ast
import sys

sys.path.append('/home/snparada/Spacionatural/Libraries')
from sheets_lib.main_sheets import GoogleSheets
from sklearn.metrics.pairwise import cosine_similarity
from pprint import pprint

def load_embeddings(file_path):
    try:
        embeddings = pd.read_csv(file_path, low_memory=False)
    except UnicodeDecodeError:
        try:
            embeddings = pd.read_csv(file_path, low_memory=False)
        except Exception as e:
            print(f'Failed to read the file with UTF-16 encoding: {e}')
            return None

    try:
        embeddings['ada_embedding'] = embeddings['ada_embedding'].apply(ast.literal_eval)
    except Exception as e:
        print(f'Error converting embeddings with ast.literal_eval: {e}')
        return None

    return embeddings

def calculate_similarity_matrix(embeddings):
    embeddings_matrix = np.array(embeddings['ada_embedding'].tolist())
    return cosine_similarity(embeddings_matrix)

def group_queries(embeddings, threshold, group_name):
    similarity_matrix = calculate_similarity_matrix(embeddings)
    grouped_queries = pd.DataFrame(columns=[group_name])
    grouped = set()

    for i in range(len(embeddings)):
        if i not in grouped:
            grouped_queries = pd.concat([grouped_queries, pd.DataFrame({group_name: [embeddings['Top queries'][i]]})], ignore_index=True)
            grouped.add(i)
            for j in range(i + 1, len(embeddings)):
                if similarity_matrix[i][j] > threshold and j not in grouped:
                    grouped_queries = pd.concat([grouped_queries, pd.DataFrame({group_name: [embeddings['Top queries'][j]]})], ignore_index=True)
                    grouped.add(j)
            grouped_queries = pd.concat([grouped_queries, pd.DataFrame({group_name: ['-']})], ignore_index=True)

    if grouped_queries.iloc[-1][group_name] == '-':
        grouped_queries = grouped_queries[:-1]

    return grouped_queries

def separate_groups(grouped_queries, group_name):
    una_palabra = []
    mas_una_palabra = []
    grupo_actual = []

    for item in grouped_queries[group_name]:
        if pd.isna(item):
            continue
        if item == '-':
            if len(grupo_actual) == 1:
                una_palabra.extend(grupo_actual)
                una_palabra.append('-')
            else:
                mas_una_palabra.extend(grupo_actual)
                mas_una_palabra.append('-')
            grupo_actual = []
        else:
            grupo_actual.append(item)

    return pd.DataFrame({'Solas': una_palabra}), pd.DataFrame({group_name: mas_una_palabra})

def create_grouped_lists_with_volume(final_groupings, group_names):
    all_group_lists = []

    for group_name in group_names:
        group_column = final_groupings[group_name]
        volume_column = f'avg_monthly_{group_name}_volume'
        
        current_group = []
        total_volume = 0

        for i, keyword in enumerate(group_column):
            if pd.isna(keyword):
                continue
            if keyword == '-':
                if current_group:
                    current_group_sorted = [kw for kw in current_group if not any(pd.isna(v) for v in kw)]
                    all_group_lists.append([total_volume] + sorted(current_group_sorted, key=lambda x: x[1], reverse=True))
                current_group = []
                total_volume = 0
            else:
                keyword_volume = final_groupings.at[i, volume_column]
                if not pd.isna(keyword_volume):
                    total_volume += keyword_volume
                    current_group.append((keyword, keyword_volume))

        if current_group:
            current_group_sorted = [kw for kw in current_group if not any(pd.isna(v) for v in kw)]
            all_group_lists.append([total_volume] + sorted(current_group_sorted, key=lambda x: x[1], reverse=True))

    return all_group_lists

def create_grouped_lists(final_groupings, group_names):
    all_group_lists = []

    for group_name in group_names:
        group_column = final_groupings[group_name]
        volume_column = f'avg_monthly_{group_name}_volume'
        
        current_group = []
        total_volume = 0

        for i, keyword in enumerate(group_column):
            if pd.isna(keyword):
                continue
            if keyword == '-':
                if current_group:
                    keywords_sorted = [kw[0] for kw in sorted(current_group, key=lambda x: x[1], reverse=True)]
                    all_group_lists.append([total_volume] + keywords_sorted)
                current_group = []
                total_volume = 0
            else:
                keyword_volume = final_groupings.at[i, volume_column]
                if not pd.isna(keyword_volume):
                    total_volume += keyword_volume
                    current_group.append((keyword, keyword_volume))

        if current_group:
            keywords_sorted = [kw[0] for kw in sorted(current_group, key=lambda x: x[1], reverse=True)]
            all_group_lists.append([total_volume] + keywords_sorted)

    return all_group_lists

def calculate_trend(values):
    if len(values) < 2:
        return 0
    x = np.arange(len(values)).reshape(-1, 1)
    y = values.values.reshape(-1, 1)
    model = LinearRegression()
    model.fit(x, y)
    return model.coef_[0][0]

def calculate_seasonality(values, period=12):
    if len(values) < period:
        return np.nan
    result = seasonal_decompose(values, model='additive', period=period)
    return result.seasonal.mean()

def analyze_trends_and_quarters(df):
    year_columns = [col for col in df.columns if col.startswith('Searches')]
    years = sorted(set(col.split()[-1] for col in year_columns))

    for year in years:
        columns_of_year = [col for col in year_columns if year in col]
        quarterly_averages = []
        for quarter in range(0, len(columns_of_year), 3):
            quarter_columns = columns_of_year[quarter:quarter+3]
            if df[quarter_columns].isna().all().all():
                quarterly_averages.append(pd.Series([np.nan] * len(df)))
            else:
                quarterly_averages.append(df[quarter_columns].mean(axis=1, skipna=True))

        if not all(average_series.isna().all() for average_series in quarterly_averages):
            best_quarter = pd.concat(quarterly_averages, axis=1).idxmax(axis=1, skipna=True)
            best_quarter[best_quarter.notna()] += 1  # Solo incrementar donde no es NA
            df['best_quarter_' + year] = best_quarter
        else:
            df['best_quarter_' + year] = pd.NA

    best_quarter_columns = [df['best_quarter_' + year] for year in years if 'best_quarter_' + year in df.columns]
    if best_quarter_columns:
        mode_result = pd.concat(best_quarter_columns, axis=1).mode(axis=1)
        if not mode_result.empty:
            df['best_quarter'] = mode_result[0]
        else:
            df['best_quarter'] = pd.NA
    else:
        df['best_quarter'] = pd.NA

    df['trend'] = df[year_columns].apply(lambda row: calculate_trend(row.dropna()), axis=1)
    df['seasonality'] = df[year_columns].apply(lambda row: calculate_seasonality(row.dropna()), axis=1)

    df['trend_analyze'] = 'stable'
    for i, row in df.iterrows():
        slope = row['trend']
        if slope > 0.05:
            df.at[i, 'trend_analyze'] = 'uptrend'
        elif slope < -0.05:
            df.at[i, 'trend_analyze'] = 'downtrend'

    return df

def create_grouped_lists_json(final_groupings, group_names):
    all_group_lists_json = []

    for group_name in group_names:
        group_column = final_groupings[group_name]
        volume_column = f'avg_monthly_{group_name}_volume'

        current_group_json = []
        for i, keyword in enumerate(group_column):
            if pd.isna(keyword):
                continue
            if keyword == '-':
                if current_group_json:
                    all_group_lists_json.append(current_group_json)
                current_group_json = []
            else:
                keyword_volume = final_groupings.at[i, volume_column]
                if not pd.isna(keyword_volume):
                    current_group_json.append({keyword: keyword_volume})

        if current_group_json:
            all_group_lists_json.append(current_group_json)

    return all_group_lists_json

def create_final_dataframe_for_sheets(grouped_lists_with_volume):
    final_df = pd.DataFrame(columns=['Group', 'Volume', 'Tendencia', 'Estacionalidad', 'Competition (indexed value)', 'Bid Range'])

    for group in grouped_lists_with_volume:
        group_total_volume = group[0]
        keywords_with_volumes = group[1:]

        final_df = pd.concat([final_df, pd.DataFrame({'Group': [f"Grupo {grouped_lists_with_volume.index(group) + 1}"], 'Volume': [group_total_volume]})], ignore_index=True)

        for keyword, volume in keywords_with_volumes:
            tendencia = final_df.loc[final_df['Group'] == keyword, 'Tendencia'].values[0] if keyword in final_df['Group'].values else None
            estacionalidad = final_df.loc[final_df['Group'] == keyword, 'Estacionalidad'].values[0] if keyword in final_df['Group'].values else None
            competition_value = final_df.loc[final_df['Group'] == keyword, 'Competition (indexed value)'].values[0] if keyword in final_df['Group'].values else None
            bid_range = final_df.loc[final_df['Group'] == keyword, 'Bid Range'].values[0] if keyword in final_df['Group'].values else None
            final_df = pd.concat([final_df, pd.DataFrame({
                'Group': [keyword], 
                'Volume': [volume], 
                'Tendencia': [tendencia], 
                'Estacionalidad': [estacionalidad], 
                'Competition (indexed value)': [competition_value],
                'Bid Range': [bid_range]
            })], ignore_index=True)

    return final_df

def main(thresholds, embedded_path, keywords_stats_file, id_sheets, page_name):
    group_names = ['first_group', 'second_group', 'third_group', 'fourth_group']
    gs = GoogleSheets(id_sheets)

    embeddings = load_embeddings(embedded_path)
    
    try:
        keywords_with_volume = pd.read_csv(keywords_stats_file, low_memory=False, encoding='utf-16', sep='\t')
    except:
        try:
            keywords_with_volume = pd.read_csv(keywords_stats_file, low_memory=False, encoding='utf-16')
        except:
            keywords_with_volume = pd.read_csv(keywords_stats_file, low_memory=False, encoding='utf-8')
    
    # Eliminar columnas no necesarias y reemplazar NaN por 0
    columns_to_drop = ['Currency', 'Segmentation', 'Three month change', 'YoY change', 'Competition']
    keywords_with_volume.drop(columns=columns_to_drop, inplace=True, errors='ignore')
    keywords_with_volume.fillna(0, inplace=True)
    
    # Calcular las columnas adicionales
    keywords_with_volume['Bid Range'] = keywords_with_volume['Top of page bid (low range)'].astype(str) + '-' + keywords_with_volume['Top of page bid (high range)'].astype(str)
    
    keywords_with_volume = analyze_trends_and_quarters(keywords_with_volume)
    pd.set_option('display.max_rows', None) 
    volume_columns = ['Keyword', 'Avg. monthly searches', 'Competition (indexed value)', 'Bid Range']

    all_groupings = pd.DataFrame()

    for i, (threshold, group_name) in enumerate(zip(thresholds, group_names)):
        if i == 0:
            current_group = group_queries(embeddings, threshold, group_name)
        else:
            lonely_words = all_groupings[all_groupings[f'lonely_words_{i-1}'] != '-'][f'lonely_words_{i-1}']
            filtered_embeddings = embeddings[embeddings['Top queries'].isin(lonely_words)].reset_index(drop=True)
            current_group = group_queries(filtered_embeddings, threshold, group_name)

        df_una_palabra, df_mas_una_palabra = separate_groups(current_group, group_name)
        df_una_palabra.rename(columns={'Solas': f'lonely_words_{i}'}, inplace=True)

        if i == 0:
            all_groupings = pd.concat([df_mas_una_palabra, df_una_palabra], axis=1)
        else:
            all_groupings = pd.concat([all_groupings, df_mas_una_palabra, df_una_palabra], axis=1)

        merged_data = pd.merge(all_groupings, keywords_with_volume[volume_columns], left_on=group_name, right_on='Keyword', how='left', sort=False)
        all_groupings = merged_data.drop(columns=['Keyword'])
        all_groupings.rename(columns={'Avg. monthly searches': f'avg_monthly_{group_name}_volume'}, inplace=True)

    final_columns = [col for group_name in group_names for col in [group_name, f'avg_monthly_{group_name}_volume']]
    final_groupings = all_groupings[final_columns]

    grouped_lists_with_volume = create_grouped_lists_with_volume(final_groupings, group_names)
    grouped_lists_with_volume.sort(key=lambda x: x[0], reverse=True)

    final_df = create_final_dataframe_for_sheets(grouped_lists_with_volume)
    gs.update_all_data_by_dataframe(final_df, page_name)

    return final_df

if __name__=="__main__":
    nich = 'envases'
    id_sheets = '1osSCP1UABHZIhZp7NVXvSAobXYD8KvHuwpx9lnkUBFc'
    page_name = 'Sheet1'
    thresholds = [0.85, 0.8, 0.75, 0.7]
    embedded_path = f'/home/snparada/Spacionatural/Data/Embeddings/Keywords/{nich}_embedded_keywords.csv'
    row_keywords_stats_file = f'/home/snparada/Spacionatural/Data/Historical/Keywords_Planner/{nich}.csv'
    final_df = main(thresholds, embedded_path, row_keywords_stats_file, id_sheets, page_name)

    pprint(final_df)
