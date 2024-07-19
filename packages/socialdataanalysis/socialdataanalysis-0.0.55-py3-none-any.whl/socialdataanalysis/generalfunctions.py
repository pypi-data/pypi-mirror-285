import pandas as pd
import requests
import pyreadstat
import tempfile
import os
from tabulate import tabulate

from sklearn.preprocessing import StandardScaler
import scipy.stats as stats
import plotly.express as px

import numpy as np
from scipy.stats import pearsonr

import plotly.graph_objs as go
import plotly.io as pio

def download_and_load_sav_file(public_url):

    """
    Baixa um arquivo .sav do OneDrive e carrega os dados em um DataFrame.

    Args:
    public_url (str): URL pública direta do arquivo no OneDrive com o parâmetro de download.

    Returns:
    DataFrame: DataFrame carregado a partir do arquivo .sav ou None se houver um erro.
    """
    # Criar um diretório temporário
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Nome do arquivo
        file_name = 'downloaded_file.sav'
        downloaded_file_path = os.path.join(tmpdirname, file_name)

        try:
            # Baixar o arquivo do OneDrive
            response = requests.get(public_url)
            response.raise_for_status()  # Levanta um erro para códigos de status de resposta ruins

            # Salvar o arquivo no diretório temporário
            with open(downloaded_file_path, 'wb') as file:
                file.write(response.content)
            print("Arquivo baixado com sucesso.")

            # Carregar o DataFrame
            df, meta = pyreadstat.read_sav(downloaded_file_path)
            print("DataFrame carregado com sucesso.")
            return df, meta

        except requests.RequestException as req_err:
            print("Erro ao baixar o arquivo:", req_err)
        except pyreadstat.ReadstatError as read_err:
            print("Erro ao carregar o arquivo:", read_err)
        except Exception as e:
            print("Erro inesperado:", e)

    return None

def gerar_tabela_frequencias(df, meta, coluna):

    """
    Gera uma tabela de frequência para uma coluna específica de um DataFrame.

    Parâmetros:
    df (pandas.DataFrame): DataFrame contendo os dados.
    meta (pyreadstat.Meta): Metadados do arquivo SAV.
    coluna (str): Nome da coluna para a qual a tabela de frequência será gerada.

    Exibe:
    Tabela de frequência com os valores, frequências, percentuais e percentuais cumulativos.
    """

    df[coluna] = df[coluna].round(2)

    # Mapear os valores para labels usando meta.variable_value_labels
    value_labels = meta.variable_value_labels.get(coluna, {})

    # Criar a tabela de frequência
    frequency_table = df[coluna].value_counts(dropna=False).sort_index().reset_index()
    frequency_table.columns = [coluna, 'Frequency']
    frequency_table['Value Labels'] = frequency_table[coluna].map(value_labels)

    # Reordenar as colunas
    frequency_table = frequency_table[[coluna, 'Value Labels', 'Frequency']]

    # Calcular os percentuais
    total_cases = len(df)
    frequency_table['Percent'] = (frequency_table['Frequency'] / total_cases * 100).round(2)
    frequency_table['Cumulative Percent'] = frequency_table['Percent'].cumsum().round(2)

    # Adicionar linha de Total
    total_row = pd.DataFrame({
        coluna: ['Total'], 
        'Value Labels': [''], 
        'Frequency': [frequency_table['Frequency'].sum()], 
        'Percent': [''], 
        'Cumulative Percent': ['']
    })
    frequency_table = pd.concat([frequency_table, total_row], ignore_index=True)

    # Exibir a tabela
    print(tabulate(frequency_table, headers='keys', tablefmt='grid', showindex=False))

def gerar_tabela_frequencias_OLD(df, meta, coluna, weight_case=None):
    """
    Gera uma tabela de frequência para uma coluna específica de um DataFrame.

    Parâmetros:
    df (pandas.DataFrame): DataFrame contendo os dados.
    meta (pyreadstat.Meta): Metadados do arquivo SAV.
    coluna (str): Nome da coluna para a qual a tabela de frequência será gerada.
    weight_case (str): Nome da coluna a ser usada para ponderação dos casos.

    Exibe:
    Tabela de frequência com os valores, frequências, percentuais e percentuais cumulativos.
    """
    # Mapear os valores para labels usando meta.variable_value_labels
    value_labels = meta.variable_value_labels.get(coluna, {})

    # Criar a tabela de frequência
    if weight_case:
        frequency_table = df.groupby(coluna)[weight_case].sum().reset_index()
        frequency_table.columns = [coluna, 'Frequency']
        frequency_table['Frequency'] = frequency_table['Frequency'].round().astype(int)
    else:
        frequency_table = df[coluna].value_counts(dropna=True).sort_index().reset_index()
        frequency_table.columns = [coluna, 'Frequency']

    # Contabilizar NaN
    if weight_case:
        nan_weight = df[df[coluna].isna()][weight_case].sum().round().astype(int)
        nan_row = pd.DataFrame({coluna: [float('nan')], 'Frequency': [nan_weight]})
    else:
        nan_count = df[coluna].isna().sum()
        nan_row = pd.DataFrame({coluna: [float('nan')], 'Frequency': [nan_count]})

    # Concat NaN row
    frequency_table = pd.concat([frequency_table, nan_row], ignore_index=True)

    # Map value labels
    frequency_table['Value Labels'] = frequency_table[coluna].map(value_labels)

    # Reordenar as colunas
    frequency_table = frequency_table[[coluna, 'Value Labels', 'Frequency']]

    # Calcular os percentuais
    total_cases = frequency_table['Frequency'].sum()
    frequency_table['Percent'] = (frequency_table['Frequency'] / total_cases * 100).round(1)
    frequency_table['Cumulative Percent'] = frequency_table['Percent'].cumsum().round(1)

    # Adicionar linha de Total
    total_row = pd.DataFrame({
        coluna: ['Total'], 
        'Value Labels': [''], 
        'Frequency': [total_cases], 
        'Percent': [''], 
        'Cumulative Percent': ['']
    })
    frequency_table = pd.concat([frequency_table, total_row], ignore_index=True)

    # Exibir a tabela
    print(tabulate(frequency_table, headers='keys', tablefmt='grid', showindex=False))

def plot_boxplot(df, variables, x_axis_title, y_axis_title):
    """
    Gera um gráfico de caixas interativo para as variáveis especificadas e identifica outliers.

    Parâmetros:
    df (pd.DataFrame): DataFrame contendo os dados a serem analisados.
    variables (list): Lista de nomes de colunas (strings) no DataFrame a serem analisadas.
    x_axis_title (str): Título para o eixo X do gráfico.
    y_axis_title (str): Título para o eixo Y do gráfico.

    Retorna:
    None: Exibe um gráfico interativo com caixas para cada variável, incluindo pontos de outliers.
    """

    # Preparar dados para Plotly
    df_melted = df[variables].melt(var_name='Variable', value_name='Z-score')
    df_melted['ID'] = df_melted.index + 1

    # Criar gráfico de caixas interativo
    fig = px.box(df_melted, x='Variable', y='Z-score', points='all', hover_data=['ID'], color='Variable')

    # Atualizar layout para melhor apresentação
    fig.update_layout(
        title="",
        xaxis_title=x_axis_title,
        yaxis_title=y_axis_title,
        template="plotly_white",
        showlegend=False
    )

    fig.show()


def padronizar_colunas(df, colunas):
    """
    Padroniza as colunas especificadas de um DataFrame.

    Parâmetros:
    df (pd.DataFrame): DataFrame contendo os dados.
    colunas (list): Lista de colunas a serem padronizadas.

    Retorna:
    pd.DataFrame: DataFrame original com as colunas padronizadas adicionadas.
    """
    df2 = df.copy(deep=True)

    # Inicializar o StandardScaler
    scaler = StandardScaler()

    # Ajustar e transformar os dados
    colunas_padronizadas = scaler.fit_transform(df2[colunas])

    # Criar novos nomes para as colunas padronizadas
    colunas_padronizadas_nomes = [f"z_{col}" for col in colunas]

    # Adicionar colunas padronizadas ao DataFrame original
    df2[colunas_padronizadas_nomes] = colunas_padronizadas

    return df2


def gerar_tabela_estatisticas_descritivas(df, variables):
    """
    Gera uma tabela de estatísticas descritivas para as variáveis especificadas em um DataFrame.
    
    Parâmetros:
    df (pd.DataFrame): O DataFrame contendo os dados a serem analisados.
    variaveis (list): Uma lista de nomes de colunas (strings) no DataFrame a serem analisadas.
    
    Retorna:
    str: Uma tabela formatada com as estatísticas descritivas.
    """
    results = []
    for var in variables:
        n = df[var].count()
        mean = f"{df[var].mean()}"
        std_dev = f"{df[var].std()}"
        skewness = f"{df[var].skew()}"
        std_err_skew = ((6 * n * (n - 1)) / ((n - 2)*(n + 1)*(n + 3))) ** 0.5
        std_err_kurt = ((4 * (n ** 2 - 1)) * (std_err_skew ** 2) / ((n - 3) * (n + 5))) ** 0.5
        std_err_skew = f"{(std_err_skew)}"
        kurtosis = f"{df[var].kurtosis()}"
        std_err_kurt = f"{(std_err_kurt)}"
        results.append([
            var, n, mean, std_dev, skewness, std_err_skew, kurtosis, std_err_kurt
        ])
    
    headers = ["Variable", "Valid\nN", "Mean", "Std.\nDeviation",
               "Skewness", "Std. Error\nof Skewness",
               "Kurtosis", "Std. Error\nof Kurtosis"]
    floatfmt = ("", ".0f", ".3f", ".3f",
                ".3f", ".3f",
                ".3f", ".3f")

    table = tabulate(results, headers, tablefmt="grid", floatfmt=floatfmt)
    
    print(table)


def gerar_tabela_normalidade(df, variables):
    """
    Realiza testes de normalidade (Kolmogorov-Smirnov e Shapiro-Wilk) nas variáveis 
    especificadas em um DataFrame e gera uma tabela formatada com os resultados.
    
    Parâmetros:
    df (pd.DataFrame): O DataFrame contendo os dados a serem testados.
    variables (list): Uma lista de nomes de colunas (strings) no DataFrame a serem testadas.
    
    Retorna:
    str: Uma tabela formatada com os resultados dos testes de normalidade.
    """
    results = []
    for var in variables:
        # Normalize the data
        normalized_data = (df[var] - df[var].mean()) / df[var].std()
        k_stat, k_p = stats.kstest(normalized_data, 'norm')
        s_stat, s_p = stats.shapiro(normalized_data)
        results.append([var, round(k_stat, 3), 31, round(k_p, 3), round(s_stat, 3), 31, round(s_p, 3)])
    
    headers = ["Variable", "Kolmogorov-Smirnov\nStatistic", "df", "Sig.", 
               "Shapiro-Wilk\nStatistic", "df", "Sig."]
    table = tabulate(results, headers, tablefmt="grid")
    
    print(table)

def display_correlation_matrix(df, variables):
    """
    Calcula e exibe a matriz de correlação e os valores de significância (1-tailed)
    para as variáveis fornecidas.

    Parâmetros:
    df (pd.DataFrame): DataFrame contendo os dados.
    variables (list): Lista de variáveis para analisar.

    Retorna:
    None: Exibe uma tabela formatada com os resultados.
    """
    # Selecionar as variáveis a serem analisadas
    data = df[variables].dropna()

    # Calcular a matriz de correlação
    corr_matrix = data.corr()

    # Calcular os valores de significância
    p_values = np.zeros((len(variables), len(variables)))
    for i in range(len(variables)):
        for j in range(len(variables)):
            if i != j:
                _, p_value = pearsonr(data.iloc[:, i], data.iloc[:, j])
                p_values[i, j] = p_value / 2  # 1-tailed
            else:
                p_values[i, j] = 0  # Na diagonal, o valor de p é 0

    # Formatar a tabela de correlação
    headers = ["Correlation Matrix"] + variables
    rows = []

    rows.append(["Correlation"] + [""] * len(variables))
    for i, var in enumerate(variables):
        rows.append([var] + [f"{corr_matrix.iloc[i, j]:.3f}" for j in range(len(variables))])

    rows.append(["Sig. (1-tailed)"] + [""] * len(variables))
    for i, var in enumerate(variables):
        rows.append([var] + [f"{p_values[i, j]:.3f}" for j in range(len(variables))])

    # Calcular o determinante da matriz de correlação
    determinant = np.linalg.det(corr_matrix.values)

    # Exibir a tabela formatada
    print(tabulate(rows, headers, tablefmt="grid"))
    print(f"Determinant = {determinant:.3f}")


def plot_profile(df, variables, category_var='categoria', category_values=None):
    """
    Gera gráficos de perfil interativos para cada categoria especificada e exibe a tabela de comparação.
    
    Parâmetros:
    df (pd.DataFrame): DataFrame contendo os dados.
    variables (list): Lista de variáveis para análise.
    category_var (str): Nome da variável da categoria.
    category_values (list): Lista de valores específicos da categoria para geração dos gráficos.
    
    Retorna:
    None: Exibe os gráficos de perfil interativos e a tabela de comparação.
    """
    pio.renderers.default = 'notebook'  # Define o renderizador padrão para o Jupyter Notebook
    
    if category_values is None:
        category_values = df[category_var]
    
    # Verificar se as categorias especificadas existem no DataFrame
    for value in category_values:
        if value not in df[category_var].values:
            raise ValueError(f"Categoria '{value}' não encontrada na variável '{category_var}'.")
    
    # Calcular a média das variáveis para cada categoria
    means = df.groupby(category_var)[variables].mean()
    
    # Criar o gráfico interativo
    fig = go.Figure()
    
    for value in category_values:
        fig.add_trace(go.Scatter(
            x=variables,
            y=means.loc[value, variables],
            mode='lines+markers',
            name=value
        ))
    
    # Ajustar layout do gráfico
    fig.update_layout(
        title='Perfil das Categorias',
        xaxis_title='Variáveis',
        yaxis_title='Média',
        template='plotly_white',
        legend_title_text=category_var,
        width=800,
        height=600
    )
    
    fig.show()
    
    # Criar e exibir a tabela de comparação
    comparison_table = means.loc[category_values].reset_index()

    # Formatar os números para três casas decimais
    formatted_table = comparison_table.map(lambda x: f"{x:.3f}" if isinstance(x, (int, float)) else x)

    # Obter os dados da tabela e os cabeçalhos
    table_data = formatted_table.values.tolist()
    table_headers = formatted_table.columns.tolist()

    # Exibir a tabela formatada usando tabulate
    print(tabulate(table_data, headers=table_headers, tablefmt="grid"))


def plot_scatter(df, x_var, y_var, category_var, category_values=None):
    """
    Gera um gráfico de dispersão interativo para as categorias especificadas.
    
    Parâmetros:
    df (pd.DataFrame): DataFrame contendo os dados.
    x_var (str): Nome da variável para o eixo x.
    y_var (str): Nome da variável para o eixo y.
    category_var (str): Nome da variável categórica.
    category_values (list): Lista de valores específicos da categoria para geração dos gráficos. Se None, plota todas as categorias.
    
    Retorna:
    None: Exibe o gráfico de dispersão interativo.
    """
    pio.renderers.default = 'notebook'  # Define o renderizador padrão para o Jupyter Notebook

    if category_values is not None:
        df = df[df[category_var].isin(category_values)]
    
    # Criar o gráfico de dispersão interativo
    fig = px.scatter(df, x=x_var, y=y_var, text=category_var, color=category_var,
                     labels={x_var: x_var, y_var: y_var},
                     title="")
    
    # Adicionar as anotações para as categorias
    fig.update_traces(textposition='top center')
   
    # Adicionar linhas de referência nos eixos
    fig.add_shape(type='line', x0=0, x1=0, y0=min(df[y_var]), y1=max(df[y_var]),
                  line=dict(color='Black', width=0))
    fig.add_shape(type='line', x0=min(df[x_var]), x1=max(df[x_var]), y0=0, y1=0,
                  line=dict(color='Black', width=0))
    
    # Ocultar a legenda
    fig.update_layout(showlegend=False)
    
    # Mostrar o gráfico
    fig.show()

    # Criar e exibir a tabela de comparação com três casas decimais
    comparison_table = df[[category_var, x_var, y_var]].groupby(category_var).mean().reset_index()
    comparison_table = comparison_table.round(3)  # Arredondar para três casas decimais
    display(comparison_table)


def apply_case_weights_OLD(df, freq_column):
    """
    Cria um novo DataFrame ponderado repetindo as linhas de acordo com os pesos.
    
    Args:
    df (pd.DataFrame): DataFrame original.
    freq_column (str): Nome da coluna que contém as frequências (pesos).
    
    Returns:
    pd.DataFrame: Novo DataFrame com os casos ponderados.
    """
    # Verifica se a coluna de frequências está no DataFrame
    if freq_column not in df.columns:
        raise ValueError(f"A coluna de pesos '{freq_column}' não está presente no DataFrame.")
    
    # Calcula a parte inteira e a parte decimal dos pesos
    integer_parts = np.floor(df[freq_column]).astype(int)
    fractional_parts = df[freq_column] - integer_parts
    
    # Cria uma lista para armazenar as linhas ponderadas
    weighted_rows = []

    # Adiciona as linhas inteiras
    for i, row in df.iterrows():
        weighted_rows.extend([row] * integer_parts[i])

    # Lida com as partes decimais
    fractional_indices = np.argsort(fractional_parts)[::-1]
    num_extra_rows = int(np.round(fractional_parts.sum()))
    
    # Adiciona linhas adicionais com base nas partes decimais mais altas
    for i in range(num_extra_rows):
        row_index = fractional_indices[i]
        weighted_rows.append(df.iloc[row_index])
    
    # Cria um novo DataFrame com as linhas ponderadas
    df_weighted = pd.DataFrame(weighted_rows).reset_index(drop=True)
    
    return df_weighted

def apply_case_weights(df, freq_column, seed=42):
    """
    Cria um novo DataFrame ponderado repetindo as linhas de acordo com os pesos.
    
    Args:
    df (pd.DataFrame): DataFrame original.
    freq_column (str): Nome da coluna que contém as frequências (pesos).
    seed (int, optional): Semente para o gerador de números aleatórios.
    
    Returns:
    pd.DataFrame: Novo DataFrame com os casos ponderados.
    """
    # Defina a semente para garantir resultados consistentes
    np.random.seed(seed)
    
    # Verifica se a coluna de frequências está no DataFrame
    if freq_column not in df.columns:
        raise ValueError(f"A coluna de pesos '{freq_column}' não está presente no DataFrame.")
    
    # Cria uma lista para armazenar as linhas ponderadas
    weighted_rows = []
    
    for i, row in df.iterrows():
        # Adiciona a parte inteira das linhas
        integer_part = int(np.floor(row[freq_column]))
        weighted_rows.extend([row.to_dict()] * integer_part)
        
        # Adiciona a parte decimal das linhas
        decimal_part = row[freq_column] - integer_part
        if np.random.rand() < decimal_part:
            weighted_rows.append(row.to_dict())
    
    # Cria um novo DataFrame com as linhas ponderadas
    df_weighted = pd.DataFrame(weighted_rows).reset_index(drop=True)
    
    return df_weighted
