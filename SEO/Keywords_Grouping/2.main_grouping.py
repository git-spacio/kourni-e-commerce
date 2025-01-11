import pandas as pd
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LinearRegression
import ast
import sys
sys.path.append('/home/snparada/Spacionatural/Libraries')
from sheets_lib.main_sheets import GoogleSheets
from pprint import pprint

def load_embeddings(file_path):
    try:
        embeddings = pd.read_csv(file_path, low_memory=False)
    except UnicodeDecodeError:
        try:
            embeddings = pd.read_csv(file_path, low_memory=False)
        except Exception as e:
            print(f'Failed to read the file with UTF-16 encoding: {e}')
            return None  # Explicitly return None to indicate failure

    try:
        embeddings['ada_embedding'] = embeddings['ada_embedding'].apply(ast.literal_eval)
    except Exception as e:
        print(f'Error converting embeddings with ast.literal_eval: {e}')
        # Decide whether to return None or the unprocessed DataFrame
        return None

    return embeddings

def calculate_similarity_matrix(embeddings):
    """
    Calcula y devuelve la matriz de similitud de coseno a partir de los embeddings.
    """
    embeddings_matrix = np.array(embeddings['ada_embedding'].tolist())
    return cosine_similarity(embeddings_matrix)

def group_queries(embeddings, threshold, group_name):
    """
    Agrupa consultas basadas en la similitud de coseno y devuelve un DataFrame con los grupos.
    Agrega un nombre personalizado a la columna de grupos.
    """
    similarity_matrix = calculate_similarity_matrix(embeddings)
    grouped_queries = pd.DataFrame(columns=[group_name])  # Usar group_name como nombre de columna
    grouped = set()

    for i in range(len(embeddings)):
        if i not in grouped:
            grouped_queries = pd.concat([grouped_queries, pd.DataFrame({group_name: [embeddings['Top queries'][i]]})], ignore_index=True)
            grouped.add(i)
            for j in range(i+1, len(embeddings)):
                if similarity_matrix[i][j] > threshold and j not in grouped:
                    grouped_queries = pd.concat([grouped_queries, pd.DataFrame({group_name: [embeddings['Top queries'][j]]})], ignore_index=True)
                    grouped.add(j)
            grouped_queries = pd.concat([grouped_queries, pd.DataFrame({group_name: ['-']})], ignore_index=True)

    if grouped_queries.iloc[-1][group_name] == '-':
        grouped_queries = grouped_queries[:-1]

    return grouped_queries

def separate_groups(grouped_queries, group_name):
    """
    Separa los grupos en dos categorías: de una palabra y de más de una palabra.
    Acepta un nombre de columna dinámico.
    """
    una_palabra = []
    mas_una_palabra = []
    grupo_actual = []

    for item in grouped_queries[group_name]:
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
        
        # Inicializa variables para mantener el seguimiento del grupo actual y su volumen total
        current_group = []
        total_volume = 0

        for i, keyword in enumerate(group_column):
            if pd.isna(keyword):  # Si la keyword es NaN, ignórala
                continue
            if keyword == '-':
                # Al llegar a un separador, añadir el grupo actual a la lista principal
                if current_group:
                    # Ordenar el grupo actual por volumen y eliminar las tuplas con NaN
                    current_group_sorted = [kw for kw in current_group if not any(pd.isna(v) for v in kw)]
                    all_group_lists.append([total_volume] + sorted(current_group_sorted, key=lambda x: x[1], reverse=True))
                
                # Reiniciar para el siguiente grupo
                current_group = []
                total_volume = 0
            else:
                # Agregar la palabra clave y su volumen al grupo actual si no son NaN
                keyword_volume = final_groupings.at[i, volume_column]
                if not pd.isna(keyword_volume):  # Comprobar si el volumen no es NaN
                    total_volume += keyword_volume
                    current_group.append((keyword, keyword_volume))

        # Añadir el último grupo si existe y no está vacío
        if current_group:
            current_group_sorted = [kw for kw in current_group if not any(pd.isna(v) for v in kw)]
            all_group_lists.append([total_volume] + sorted(current_group_sorted, key=lambda x: x[1], reverse=True))

    return all_group_lists

def create_grouped_lists(final_groupings, group_names):
    all_group_lists = []

    for group_name in group_names:
        group_column = final_groupings[group_name]
        volume_column = f'avg_monthly_{group_name}_volume'
        
        # Inicializa variables para mantener el seguimiento del grupo actual y su volumen total
        current_group = []
        total_volume = 0

        for i, keyword in enumerate(group_column):
            if pd.isna(keyword):  # Si la keyword es NaN, ignórala
                continue
            if keyword == '-':
                # Al llegar a un separador, añadir el grupo actual a la lista principal
                if current_group:
                    # Ordenar el grupo actual por volumen y obtener solo las keywords
                    keywords_sorted = [kw[0] for kw in sorted(current_group, key=lambda x: x[1], reverse=True)]
                    all_group_lists.append([total_volume] + keywords_sorted)
                
                # Reiniciar para el siguiente grupo
                current_group = []
                total_volume = 0
            else:
                # Agregar la palabra clave y su volumen al grupo actual si no son NaN
                keyword_volume = final_groupings.at[i, volume_column]
                if not pd.isna(keyword_volume):  # Comprobar si el volumen no es NaN
                    total_volume += keyword_volume
                    current_group.append((keyword, keyword_volume))

        # Añadir el último grupo si existe y no está vacío
        if current_group:
            keywords_sorted = [kw[0] for kw in sorted(current_group, key=lambda x: x[1], reverse=True)]
            all_group_lists.append([total_volume] + keywords_sorted)

    return all_group_lists

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
            best_quarter = pd.concat(quarterly_averages, axis=1).idxmax(axis=1) + 1
            df['best_quarter_' + year] = best_quarter
        else:
            df['best_quarter_' + year] = pd.NA


    # Determinar el trimestre más frecuente como el mejor
    best_quarter_columns = [df['best_quarter_' + year] for year in years if 'best_quarter_' + year in df.columns]
    if best_quarter_columns:
        mode_result = pd.concat(best_quarter_columns, axis=1).mode(axis=1)
        if not mode_result.empty:
            df['best_quarter'] = mode_result[0]
        else:
            df['best_quarter'] = pd.NA
    else:
        df['best_quarter'] = pd.NA


    # Análisis de la tendencia basado en el mejor trimestre general
    df['trend_analyze'] = 'stable'  # Default classification
    for i, row in df.iterrows():
        # Extraer los valores mensuales y sus índices temporales
        monthly_values = row[year_columns].dropna()
        if len(monthly_values) < 2:
            continue  # Necesitamos al menos dos puntos para calcular una regresión lineal

        # Crear un arreglo de índices temporales (0, 1, 2, ...)
        x = np.arange(len(monthly_values)).reshape(-1, 1)
        y = monthly_values.values.reshape(-1, 1)

        # Calcular la regresión lineal
        model = LinearRegression()
        model.fit(x, y)
        slope = model.coef_[0][0]
        df.at[i, 'trend'] = slope

        # Asignar la tendencia basada en la pendiente
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
            if pd.isna(keyword):  # Si la keyword es NaN, ignórala
                continue
            if keyword == '-':
                # Al llegar a un separador, añadir el grupo actual al JSON
                if current_group_json:
                    all_group_lists_json.append(current_group_json)
                current_group_json = []
            else:
                # Agregar la palabra clave y su volumen al grupo actual si no son NaN
                keyword_volume = final_groupings.at[i, volume_column]
                if not pd.isna(keyword_volume):  # Comprobar si el volumen no es NaN
                    current_group_json.append({keyword: keyword_volume})

        # Añadir el último grupo si existe y no está vacío
        if current_group_json:
            all_group_lists_json.append(current_group_json)

    return all_group_lists_json

def main(thresholds,embedded_path,keywords_stats_file,id_sheets):
    # Configuración inicial
    group_names = ['first_group', 'second_group', 'third_group', 'fourth_group']
    gs = GoogleSheets(id_sheets)

    # Cargar los embeddings
    embeddings = load_embeddings(embedded_path)
    
    # Cargar las estadísticas de volumen de búsqueda
    keywords_with_volume = pd.read_csv(keywords_stats_file, low_memory=False, encoding = 'utf-8')
    keywords_with_volume = analyze_trends_and_quarters(keywords_with_volume)
    pd.set_option('display.max_rows', None) 
    volume_columns = ['Keyword', 'Avg. monthly searches']  # Agrega más columnas si son necesarias

    all_groupings = pd.DataFrame()

    # Realizar los agrupamientos sucesivos
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

        # Añadir estadísticas de volumen de búsqueda para cada grupo
        merged_data = pd.merge(all_groupings, keywords_with_volume[volume_columns], left_on=group_name, right_on='Keyword', how='left', sort=False)
        all_groupings = merged_data.drop(columns=['Keyword'])  # Eliminar la columna 'Keyword' duplicada
        all_groupings.rename(columns={'Avg. monthly searches': f'avg_monthly_{group_name}_volume'}, inplace=True)

    # Conservar solo las columnas de grupo y sus volúmenes
    final_columns = [col for group_name in group_names for col in [group_name, f'avg_monthly_{group_name}_volume']]
    final_groupings = all_groupings[final_columns]

    # Actualizar Google Sheets con los datos finales
    gs.update_all_data_by_dataframe(final_groupings, page_name)

    grouped_lists_with_volume = create_grouped_lists_with_volume(final_groupings, group_names)
    grouped_lists = create_grouped_lists(final_groupings, group_names)
    
    json = create_grouped_lists_json(final_groupings, group_names)

    return keywords_with_volume, grouped_lists, embeddings, json

if __name__ == "__main__":
    id_sheets = '1osSCP1UABHZIhZp7NVXvSAobXYD8KvHuwpx9lnkUBFc'
    page_name = 'Sheet1'
    thresholds = [0.9, 0.85, 0.8, 0.75]
    embedded_path = '/home/snparada/Spacionatural/E-Commerce/SEO/Keywords_Grouping/embedded_keywords.csv'
    row_keywords_stats_file = '/home/snparada/Spacionatural/Data/Historical/Keywords_Planner/envases.csv'
    keywords_with_statistics, grouped_lists, embeddings, json = main(thresholds,embedded_path,row_keywords_stats_file,id_sheets)

    pprint(json)