import pandas as pd
import numpy as np
import ast
import sys
from urllib.parse import urlparse

sys.path.append('/home/snparada/Spacionatural/Libraries')
from sheets_lib.main_sheets import GoogleSheets
from sklearn.metrics.pairwise import cosine_similarity
from pprint import pprint

def extract_domain(url):
    try:
        domain = urlparse(url).netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return ''

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
                    if current_group_sorted:
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
            if current_group_sorted:
                all_group_lists.append([total_volume] + sorted(current_group_sorted, key=lambda x: x[1], reverse=True))

    return all_group_lists

def create_final_dataframe_for_sheets(grouped_lists_with_volume, final_groupings, group_names):
    final_data = []

    for group in grouped_lists_with_volume:
        group_total_volume = group[0]
        keywords_with_volumes = group[1:]

        if group_total_volume > 0:
            final_data.append({'Group': f"Grupo {grouped_lists_with_volume.index(group) + 1}", 'Volume': group_total_volume})

        for keyword, volume in keywords_with_volumes:
            keyword_difficulty = None
            competitive_density = None
            trend = None
            click_potential = None
            top_10_competitors = [''] * 10
            for group_name in group_names:
                if keyword in final_groupings[group_name].values:
                    row = final_groupings[final_groupings[group_name] == keyword].iloc[0]
                    keyword_difficulty = row.get(f'keyword_difficulty_{group_name}', None)
                    competitive_density = row.get(f'competitive_density_{group_name}', None)
                    trend = row.get(f'trend_{group_name}', None)
                    click_potential = row.get(f'click_potential_{group_name}', None)
                    for i in range(1, 11):
                        competitor_column = f'competitor_{i}_{group_name}'
                        competitor_value = row.get(competitor_column, '')
                        if competitor_value == 'b\'\'':
                            competitor_value = np.nan
                        top_10_competitors[i-1] = competitor_value
                    break
            
            if volume > 0:
                final_data.append({
                    'Group': keyword, 
                    'Volume': volume, 
                    'Keyword Difficulty': keyword_difficulty,
                    'Competitive Density': competitive_density,
                    'Trend': trend,
                    'Click potential': click_potential,
                    **{str(i): top_10_competitors[i-1] for i in range(1, 11)}
                })

    final_df = pd.DataFrame(final_data, columns=['Group', 'Volume', 'Keyword Difficulty', 'Competitive Density', 'Trend', 'Click potential'] + [str(i) for i in range(1, 11)])

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
    
    # Mantener solo las columnas necesarias y reemplazar NaN por 0
    keywords_with_volume = keywords_with_volume[['Keyword', 'Volume', 'Keyword Difficulty', 'Competitive Density', 'Trend', 'Click potential'] + [f'Competitor on TOP 10 #{i}' for i in range(1, 11)]]
    keywords_with_volume.replace("b''", np.nan, inplace=True)
    keywords_with_volume.fillna(0, inplace=True)
    
    # Extraer dominios de las URLs de competidores
    for i in range(1, 11):
        column_name = f'Competitor on TOP 10 #{i}'
        keywords_with_volume[column_name] = keywords_with_volume[column_name].apply(extract_domain)
    
    volume_columns = ['Keyword', 'Volume', 'Keyword Difficulty', 'Competitive Density', 'Trend', 'Click potential'] + [f'Competitor on TOP 10 #{i}' for i in range(1, 11)]

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
        all_groupings.rename(columns={
            'Volume': f'avg_monthly_{group_name}_volume',
            'Keyword Difficulty': f'keyword_difficulty_{group_name}',
            'Competitive Density': f'competitive_density_{group_name}',
            'Trend': f'trend_{group_name}',
            'Click potential': f'click_potential_{group_name}',
            **{f'Competitor on TOP 10 #{i}': f'competitor_{i}_{group_name}' for i in range(1, 11)}
        }, inplace=True)

    final_columns = [col for group_name in group_names for col in [group_name, f'avg_monthly_{group_name}_volume', f'keyword_difficulty_{group_name}', f'competitive_density_{group_name}', f'trend_{group_name}', f'click_potential_{group_name}'] + [f'competitor_{i}_{group_name}' for i in range(1, 11)]]
    final_groupings = all_groupings[final_columns]

    grouped_lists_with_volume = create_grouped_lists_with_volume(final_groupings, group_names)
    grouped_lists_with_volume.sort(key=lambda x: x[0], reverse=True)

    final_df = create_final_dataframe_for_sheets(grouped_lists_with_volume, final_groupings, group_names)
    gs.update_all_data_by_dataframe(final_df, page_name)

    return final_df

if __name__=="__main__":
    nich = 'kawaii'
    id_sheets = '1Y9NrzVzxdsbqKV-8FzrrGwTT5nG6ZCYvZRWcxLZ9nxY'
    page_name = 'Sheet1'
    thresholds = [0.85, 0.8, 0.75, 0.7]
    embedded_path = f'/home/snparada/Spacionatural/Data/Embeddings/Keywords_Semrush/{nich}_embedded_keywords.csv'
    row_keywords_stats_file = f'/home/snparada/Spacionatural/Data/Historical/Keywords_Planner_Semrush/{nich}.csv'
    final_df = main(thresholds, embedded_path, row_keywords_stats_file, id_sheets, page_name)

    pprint(final_df)
