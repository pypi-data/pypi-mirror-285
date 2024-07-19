import pandas as pd
import numpy as np
import pingouin as pg
import seaborn as sns
import matplotlib.pyplot as plt

from reliabilipy import reliability_analysis
from tabulate import tabulate
from factor_analyzer.factor_analyzer import calculate_kmo
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity

from factor_analyzer import FactorAnalyzer
import plotly.express as px
from itertools import combinations



def inverter_escala(df, colunas, escalas):
    """
    Inverte as escalas de colunas especificadas em um DataFrame.

    Parâmetros:
    - df (pandas.DataFrame): DataFrame contendo os dados.
    - colunas (list): Lista de colunas para as quais a escala deve ser invertida.
    - escalas (list): Lista de valores máximos das escalas correspondentes às colunas.

    Retorna:
    - DataFrame modificado, e opcionalmente, os metadados.
    """
    if not isinstance(colunas, list) or not isinstance(escalas, list) or len(colunas) != len(escalas):
        return "Erro: 'colunas' e 'escalas' devem ser listas de mesmo tamanho.", None

    for coluna, escala in zip(colunas, escalas):
        if coluna in df.columns:
            df[coluna + '_R'] = escala + 1 - df[coluna]
            print(f"Coluna '{coluna + '_R'}' criada.")
        else:
            return f"Erro: A coluna '{coluna}' não existe no DataFrame.", None
        
    return df
        
def transformar_escala(df, coluna, nova_escala_min, nova_escala_max):
    """
    Transforma os valores de uma coluna de um DataFrame de sua escala original para uma nova escala especificada.

    Parâmetros:
    - df (pandas.DataFrame): DataFrame contendo os dados.
    - coluna (str): Nome da coluna a ser transformada.
    - nova_escala_min (int): Valor mínimo da nova escala.
    - nova_escala_max (int): Valor máximo da nova escala.
    
    Retorna:
    - DataFrame com a coluna transformada.
    """
    # Extrair os valores mínimo e máximo originais da coluna
    orig_min = df[coluna].min()
    orig_max = df[coluna].max()

    # Verificar se os valores mínimos e máximos não são nulos
    if pd.isna(orig_min) or pd.isna(orig_max):
        raise ValueError("A coluna contém apenas valores nulos.")

    # Aplicar a transformação linear para a nova escala
    df[coluna + '_Nova_Escala'] = df[coluna].apply(
        lambda x: (x - orig_min) / (orig_max - orig_min) * (nova_escala_max - nova_escala_min) + nova_escala_min
        if pd.notnull(x) else None
    )

    print(f"Coluna '{coluna + '_Nova_Escala'}' criada.")

    return df
    
def analisar_consistencia_interna(df, colunas, exibir_correlacoes=False, exibir_resumo=False, exibir_heatmap=False):
    """
    Analisa o alfa de Cronbach, Ômega de MacDonald e as correlações para um conjunto específico de colunas de um DataFrame.
    
    Parâmetros:
        df (pd.DataFrame): DataFrame contendo os dados a serem analisados.
        colunas (list): Lista de colunas a serem incluídas na análise.
        exibir_correlacoes (bool): Se True, imprime a matriz de correlações.
        exibir_resumo (bool): Se True, imprime o resumo do alfa de Cronbach com e sem cada coluna.
        exibir_heatmap (bool): Se True, exibe um heatmap das correlações.

    Retorna:
        tuple: Retorna o alfa de Cronbach original, o Ômega de MacDonald, a matriz de correlações e o resumo do alfa de Cronbach se cada coluna for removida.
    """
    
    def calcular_omega(df):
        """Função auxiliar para calcular o Ômega de MacDonald."""
        correlacoes = df.corr()
        try:
            reliability_report = reliability_analysis(correlations_matrix=correlacoes)
            reliability_report.fit()
            return reliability_report.omega_total
        except Exception as e:
            print(f"Erro ao calcular o Ômega de MacDonald: {e}")
            return None
    
    df_filtrado = df[colunas]
    correlacoes = df_filtrado.corr()

    # Calcula o alfa de Cronbach original
    alfa_original = None
    if df_filtrado.shape[1] > 1:
        try:
            alfa_original = pg.cronbach_alpha(df_filtrado)[0]
        except Exception as e:
            print(f"Erro ao calcular o alfa de Cronbach original: {e}")

    # Calcula o Ômega de MacDonald original
    omega_total = None
    if df_filtrado.shape[1] > 1:
        omega_total = calcular_omega(df_filtrado)

    # Calcula o alfa de Cronbach e Ômega se cada coluna for removida
    alfas_removidos = {}
    omegas_removidos = {}
    for coluna in colunas:
        temp_df = df_filtrado.drop(columns=[coluna])
        alfas_removidos[coluna] = None
        omegas_removidos[coluna] = None
        if temp_df.shape[1] > 1:
            try:
                alfas_removidos[coluna], _ = pg.cronbach_alpha(temp_df)
                omegas_removidos[coluna] = calcular_omega(temp_df)
            except Exception as e:
                print(f"Erro ao calcular os valores removendo a coluna {coluna}: {e}")

    # Exibe o alfa de Cronbach original e o Ômega de MacDonald
    resultados = []
    if alfa_original is not None:
        resultados.append(['Alfa de Cronbach Original', round(alfa_original, 3)])
    if omega_total is not None:
        resultados.append(['Ômega de MacDonald Original', round(omega_total, 3)])

    if resultados:
        print(tabulate(resultados, headers=['Métrica', 'Valor'], tablefmt='grid'))

    # Exibe o resumo do alfa de Cronbach e Ômega de MacDonald se item removido
    if exibir_resumo:
        resumo = pd.DataFrame({
            'Alfa se item removido': alfas_removidos,
            'Ômega se item removido': omegas_removidos
        })
        resumo_tabela = [[coluna, round(alfa, 3), round(omega, 3)] for coluna, (alfa, omega) in resumo.iterrows()]
        print("\nAlfa e Ômega se item removido:")
        print(tabulate(resumo_tabela, headers=['Coluna', 'Alfa', 'Ômega'], tablefmt='grid'))

    # Exibe a matriz de correlações
    if exibir_correlacoes:
        correlacoes_tabela = correlacoes.round(3).reset_index().values.tolist()
        correlacoes_tabela.insert(0, [''] + list(correlacoes.columns))
        print("\nCorrelações:")
        print(tabulate(correlacoes_tabela, headers='firstrow', tablefmt='grid'))

    # Exibe o heatmap das correlações
    if exibir_heatmap:
        sns.heatmap(correlacoes, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title("\nMatriz de Correlações")
        plt.show()


def display_kmo_bartlett_results(df, variables):
    """
    Calcula e exibe os resultados da Medida de Adequação de Amostragem de Kaiser-Meyer-Olkin (KMO)
    e do Teste de Esfericidade de Bartlett para as variáveis fornecidas.

    Parâmetros:
    df (pd.DataFrame): DataFrame contendo os dados.
    variables (list): Lista de variáveis para analisar.

    Retorna:
    None: Exibe uma tabela formatada com os resultados.
    """
    # Selecionar as variáveis a serem analisadas
    data = df[variables].dropna()

    # Calcular o KMO
    kmo_all, kmo_model = calculate_kmo(data)

    # Calcular o Teste de Esfericidade de Bartlett
    chi_square_value, p_value = calculate_bartlett_sphericity(data)

    # Calcular os graus de liberdade
    num_vars = len(variables)
    df_value = (num_vars * (num_vars - 1)) / 2
   
    # Formatar a tabela de resultados
    table = [
        ["Kaiser-Meyer-Olkin Measure of Sampling Adequacy.", f"{kmo_model:.3f}"],
        ["", ""],
        ["Bartlett's Test of Sphericity", ""],
        ["Approx. Chi-Square", f"{chi_square_value:.3f}"],
        ["df", f"{df_value:.0f}"],
        ["Sig.", f"{p_value:.3f}"]
    ]

    kmo_individual_table = [["KMO Individual\n(Diagonal de Anti-Image Correlations)", ""]]
    kmo_individual_table += [[var, f"{kmo_all[i]:.3f}"] for i, var in enumerate(variables)]

    print(tabulate(table, tablefmt="grid"))
    print()
    print(tabulate(kmo_individual_table, tablefmt="grid"))


def display_eigenvalues_and_variance_explained(df, variables, method, rotation, n_factors=None):
    """
    Calcula e exibe os resultados da Análise de Componentes Principais (PCA) ou outro método de extração
    para as variáveis fornecidas, incluindo autovalores, variância explicada, e um gráfico de Scree Plot.

    Parâmetros:
    df (pd.DataFrame): DataFrame contendo os dados.
    variables (list): Lista de variáveis para analisar.
    method (str): Método de extração a ser usado ('principal', 'ml', etc.).
    rotation (str): Método de rotação a ser usado ('varimax', 'promax', etc.).
    n_factors (int, opcional): Número de fatores a serem extraídos. Se None, o número de fatores será determinado automaticamente.

    Retorna:
    None: Exibe uma tabela formatada com os resultados e um gráfico de Scree Plot.
    """

    # Selecionar as variáveis a serem analisadas
    data = df[variables].dropna()

    ## Cálculos sem rotação e com method = 'principal' ##
    # Ajustar o fator analisador
    fa = FactorAnalyzer(rotation=None, method="principal", n_factors=len(variables))
    fa.fit(data)
    # Extrair autovalores
    eigenvalues, vectors = fa.get_eigenvalues()
    # Extrair as cargas fatoriais
    loadings = fa.loadings_
    # Calcular variância explicada e variância acumulada
    variance_explained, proportional_variance_explained, cumulative_variance_explained = fa.get_factor_variance()

    n_factors_extracted = next((index for index, value in enumerate(variance_explained) if value < 1), len(variance_explained))

    if n_factors is None:
        ## Identificar o primeiro índice onde variance_explained < 1 ##
        n_factors = n_factors_extracted

    ## Cálculos sem rotação com extração ##
    # Ajustar o fator analisador para PCA
    fa_ex = FactorAnalyzer(rotation=None, method=method, n_factors=n_factors)
    fa_ex.fit(data)
    # Extrair autovalores
    eigenvalues_ex, vectors_ex = fa_ex.get_eigenvalues()
    # Extrair as cargas fatoriais
    loadings_ex = fa_ex.loadings_
    # Calcular variância explicada e variância acumulada
    variance_explained_ex, proportional_variance_explained_ex, cumulative_variance_explained_ex = fa_ex.get_factor_variance()

    ## Cálculos com rotação com extração ##
    # Ajustar o fator analisador para PCA
    fa_rotated_ex = FactorAnalyzer(rotation=rotation, method=method, n_factors=n_factors)
    fa_rotated_ex.fit(data)
    # Extrair autovalores
    eigenvalues_rotated_ex, vectors_rotated_ex = fa_rotated_ex.get_eigenvalues()
    # Extrair as cargas fatoriais
    loadings_rotated_ex = fa_rotated_ex.loadings_
    # Calcular variância explicada e variância acumulada
    variance_explained_rotated_ex, proportional_variance_explained_rotated_ex, cumulative_variance_explained_rotated_ex = fa_rotated_ex.get_factor_variance()

    # Preparar tabela de resultados
    rows = []
    for i in range(len(variables)):
        if i < n_factors:
            rows.append([
                i + 1,
                f"{eigenvalues[i]}", f"{proportional_variance_explained[i]*100}", f"{cumulative_variance_explained[i]*100}",
                f"{variance_explained_ex[i]}", f"{proportional_variance_explained_ex[i]*100}", f"{cumulative_variance_explained_ex[i]*100}",
                f"{variance_explained_rotated_ex[i]}", f"{proportional_variance_explained_rotated_ex[i]*100}", f"{cumulative_variance_explained_rotated_ex[i]*100}"
            ])
        else:
            rows.append([
                i + 1,
                f"{variance_explained[i]}", f"{proportional_variance_explained[i]*100}", f"{cumulative_variance_explained[i]*100:.3f}",
                None, None, None,
                None, None, None
            ])

    headers = ["Component", "Total\nInitial\nEigenvalues", "% of Variance", "Cumulative %",
               "Total\nExtraction\nSS Loadings", "% of Variance", "Cumulative %",
               "Total\nRotation\nSS Loadings", "% of Variance", "Cumulative %"]

    floatfmt = (".0f", ".3f", ".2f", ".2f",
                ".3f", ".2f", ".2f",
                ".3f", ".2f", ".2f",)
    elements_name = {
        'principal': ('Principal Component Analysis', 'PCA'),
        'minres': ('Principal Axis Factoring', 'PAF'),
        'ml': ('Maximum Likelihood', 'ML'),
    }
    
    print(tabulate(rows, headers, tablefmt="grid", floatfmt=floatfmt))
    print(f"Extraction Method: {elements_name[method][0]}.")
    #print(f"Rotation Method: {rotation} with Kaiser Normalization.")
  
    # Gerar o gráfico de Scree Plot
    x_values = list(range(1, len(eigenvalues) + 1))
    fig = px.line(x=x_values, y=eigenvalues, markers=True, title="")
    fig.update_layout(
        xaxis_title="Component Number",
        yaxis_title="Eigenvalue",
        template="plotly_white",
        width=500,
        height=400,
        xaxis=dict(
            tickmode='array',
            tickvals=x_values,
            ticktext=x_values
        ),
    )
    fig.show()


def display_communality_and_component_matrix(df, variables, method, n_factors):
    """
    Calcula e exibe as comunalidades e a matriz de componentes para as variáveis fornecidas.

    Parâmetros:
    df (pd.DataFrame): DataFrame contendo os dados.
    variables (list): Lista de variáveis para analisar.
    method (str): Método de extração a ser usado ('principal', 'minres', 'ml', etc.).
    n_factors (int): Número de fatores a serem extraídos.

    Retorna:
    None: Exibe tabelas formatadas com os resultados.
    """
    # Selecionar as variáveis a serem analisadas
    data = df[variables].dropna()

    # Ajustar o fator analisador para PCA
    fa = FactorAnalyzer(rotation=None, method=method, n_factors=n_factors)
    fa.fit(data)

    # Extrair as comunalidades
    communalities = fa.get_communalities()

    # Ajustar o fator analisador para PCA com rotação Varimax
    fa = FactorAnalyzer(rotation=None, method=method, n_factors=n_factors)
    fa.fit(data)

    # Extrair a matriz de componentes
    loadings = fa.loadings_

    # Preparar tabela de comunalidades
    communality_rows = []
    for i, var in enumerate(variables):
        communality_rows.append([var, f"{communalities[i]:.3f}"])

    communality_headers = ["Communalities", "Extraction"]

    # Preparar tabela de matriz de componentes
    component_rows = []
    for i, var in enumerate(variables):
        component_rows.append([var] + [f"{loadings[i, j]:.3f}" for j in range(loadings.shape[1])])

    # Mapeamento da extração
    elements_name = {
        'principal': 'Components',
        'minres': 'Factors',
        'ml': 'Factors'
    }

    component_headers = [f"{elements_name.get(method, 'Unknown Method')}"] + [str(i + 1) for i in range(loadings.shape[1])]

    ## Exibir tabelas formatadas ##

    # Mapeamento de métodos para seus nomes completos
    method_names = {
        'principal': 'Principal Component Analysis (or PCA)',
        'minres': 'Minimum Residual Factor Analysis (or PAF)',
        'ml': 'Maximum Likelihood'
    }

    print(tabulate(communality_rows, communality_headers, tablefmt="grid"))
    print(f"Extraction Method: {method_names.get(method, 'Unknown Method')}.")
    print(f"{n_factors} {elements_name.get(method, 'Unknown Method')} extracted.")
    print()
    print(tabulate(component_rows, component_headers, tablefmt="grid"))
    print(f"Extraction Method: {method_names.get(method, 'Unknown Method')}.")
    print(f"{n_factors} {elements_name.get(method, 'Unknown Method')} extracted.")


def display_rotated_component_matrix(df, variables, method, n_factors, rotation, plot=False):
    """
    Calcula e exibe a matriz de componentes rotacionada para as variáveis fornecidas
    usando Análise de Componentes Principais (PCA) com rotação especificada.

    Parâmetros:
    df (pd.DataFrame): DataFrame contendo os dados.
    variables (list): Lista de variáveis para analisar.
    method (str): Método de extração a ser usado ('principal', 'minres', 'ml', etc.).
    n_factors (int): Número de fatores a serem extraídos.
    rotation (str): Método de rotação a ser usado ('varimax', 'promax', etc.).
    plot (bool): Se True, gera gráficos de dispersão das cargas fatoriais rotacionadas para todas as combinações de fatores.

    Retorna:
    None: Exibe uma tabela formatada com os resultados e, opcionalmente, gráficos de dispersão.
    """
    # Selecionar as variáveis a serem analisadas
    data = df[variables].dropna()

    # Ajustar o fator analisador para PCA com rotação especificada
    fa_rotated = FactorAnalyzer(rotation=rotation, method=method, n_factors=n_factors)
    fa_rotated.fit(data)

    # Extrair a matriz de componentes rotacionada
    loadings_rotated = fa_rotated.loadings_

    # Preparar tabela de matriz de componentes rotacionada
    component_rows = []
    for i, var in enumerate(variables):
        component_rows.append([var] + [loadings_rotated[i, j] for j in range(loadings_rotated.shape[1])])

    # Ordenar as linhas pelo módulo das maiores cargas fatoriais
    component_rows.sort(key=lambda row: tuple(-abs(row[i + 1]) for i in range(n_factors)))

    # Formatando os valores para exibição
    formatted_rows = [[row[0]] + [f"{value:.3f}" for value in row[1:]] for row in component_rows]

    # Mapeamento da extração
    elements_name = {
        'principal': 'Component',
        'minres': 'Factor',
        'ml': 'Factor'
    }

    component_headers = [f"{elements_name.get(method, 'Unknown Method')}"] + [str(i + 1) for i in range(loadings_rotated.shape[1])]

    # Exibir tabela formatada
    print(tabulate(formatted_rows, component_headers, tablefmt="grid"))

    # Mapeamento de métodos para seus nomes completos
    method_names = {
        'principal': 'Principal Component Analysis',
        'minres': 'Minimum Residual Factor Analysis',
        'ml': 'Maximum Likelihood'
    }

    print(f"Extraction Method: {method_names.get(method, 'Unknown Method')}.")
    print(f"Rotation Method: {rotation}.")

    # Gerar gráficos de dispersão para todas as combinações de fatores se plot=True
    if plot:
        for (i, j) in combinations(range(n_factors), 2):
            x_values = loadings_rotated[:, i]
            y_values = loadings_rotated[:, j]
            
            # Calcular os limites dos eixos
            margin = 0.2
            x_min, x_max = min(x_values), max(x_values) + margin
            y_min, y_max = min(y_values), max(y_values) + margin
            x_range = max(abs(x_min), abs(x_max))
            y_range = max(abs(y_min), abs(y_max))
           
            fig = px.scatter(
                x=x_values, 
                y=y_values, 
                text=variables, 
                title=f"{method_names.get(method, 'Unknown Method')} {i+1} vs {method_names.get(method, 'Unknown Method')} {j+1} in Rotated Space"
            )
            fig.update_layout(
                xaxis_title=f"{elements_name.get(method, 'Unknown Method')} {i+1}",
                yaxis_title=f"{elements_name.get(method, 'Unknown Method')} {j+1}",
                template="plotly_white",
                width=600,
                height=600,
                xaxis=dict(range=[-x_range, x_range], zeroline=True, zerolinewidth=1, zerolinecolor='black'),
                yaxis=dict(range=[-y_range, y_range], zeroline=True, zerolinewidth=1, zerolinecolor='black')
            )
            fig.update_traces(marker=dict(size=12))
            fig.show()

def display_and_store_component_matrices(df, variables, method, n_factors, rotation, print_results=False):
    """
    Calcula e exibe a matriz de transformação dos componentes e a matriz de coeficientes de pontuação dos componentes
    para as variáveis fornecidas usando Análise de Componentes Principais (PCA) com rotação especificada, e armazena
    os scores resultantes no DataFrame original.

    Parâmetros:
    df (pd.DataFrame): DataFrame contendo os dados.
    variables (list): Lista de variáveis para analisar.
    method (str): Método de extração a ser usado ('principal', 'minres', 'ml', etc.).
    n_factors (int): Número de fatores a serem extraídos.
    rotation (str): Método de rotação a ser usado ('varimax', 'promax', etc.).

    Retorna:
    pd.DataFrame: DataFrame original com os scores dos componentes/fatores adicionados.
    """
    # Selecionar as variáveis a serem analisadas
    data = df[variables].dropna()

    # Ajustar o fator analisador para PCA com rotação especificada
    fa_rotated = FactorAnalyzer(rotation=rotation, method=method, n_factors=n_factors)
    fa_rotated.fit(data)

    # Extrair a matriz de transformação dos componentes
    transformation_matrix = fa_rotated.rotation_matrix_

    # Extrair a matriz de componentes rotacionada
    loadings_rotated = fa_rotated.loadings_

    # Calcular a matriz de correlação das variáveis
    corr_matrix = np.corrcoef(data.T)

    # Calcular a matriz de coeficientes de pontuação dos componentes
    inv_corr_matrix = np.linalg.inv(corr_matrix)
    component_scores_matrix = np.dot(inv_corr_matrix, loadings_rotated)

    # Preparar tabela de matriz de transformação dos componentes
    transformation_rows = []
    for i in range(n_factors):
        transformation_rows.append([f"{i + 1}"] + [f"{transformation_matrix[i, j]:.3f}" for j in range(n_factors)])

    # Preparar tabela de matriz de coeficientes de pontuação dos componentes
    score_rows = []
    for i, var in enumerate(variables):
        score_rows.append([var] + [f"{component_scores_matrix[i, j]:.3f}" for j in range(n_factors)])

    # Mapeamento da extração
    elements_name = {
        'principal': ('Principal Component Analysis', 'PCA'),
        'minres': ('Principal Axis Factoring', 'PAF'),
        'ml': ('Maximum Likelihood', 'ML'),
    }

    #transformation_headers = ["Component Transformation Matrix"] + [f"{i + 1}" for i in range(n_factors)]
    score_headers = ["Component Score Coefficient Matrix"] + [f"{i + 1}" for i in range(n_factors)]

    if print_results:
        # Exibir tabelas formatadas
        #print(tabulate(transformation_rows, transformation_headers, tablefmt="grid"))
        #print(f"Extraction Method: {elements_name.get(method, 'Unknown Method')}.")
        #print(f"Rotation Method: {rotation} with Kaiser Normalization.")
        #print()
        print(tabulate(score_rows, score_headers, tablefmt="grid"))
        print(f"Extraction Method: {elements_name[method][0]}.")
        print(f"Rotation Method: {rotation} with Kaiser Normalization.")


    # Armazenar os scores numa cópia do DataFrame original
    df2 = df.copy(deep=True)
    scores = fa_rotated.transform(data)
    for i in range(n_factors):
        df2[f"{elements_name[method][1]}_{i + 1}"] = np.nan
        df2.loc[data.index, f"{elements_name[method][1]}_{i + 1}"] = scores[:, i]
    
    return df2



def calculate_reproduced_correlations_and_fit_indices(df, variables, method, n_factors, rotation, print_rc=False, print_fi=False):
    """
    Calcula e interpreta a matriz das correlações reproduzidas ou estimadas e os índices de bondade do ajustamento GFI, AGFI e RMSR.

    Parâmetros:
    df (pd.DataFrame): DataFrame contendo os dados.
    variables (list): Lista de variáveis para analisar.
    method (str): Método de extração a ser usado ('principal', 'minres', 'ml', etc.).
    n_factors (int): Número de fatores a serem extraídos.
    rotation (str): Método de rotação a ser usado ('varimax', 'promax', etc.).

    Retorna:
    None: Exibe tabelas formatadas com os resultados.
    """
    # Selecionar as variáveis a serem analisadas
    data = df[variables].dropna()

    # Ajustar o fator analisador para PCA ou PAF com rotação especificada
    fa = FactorAnalyzer(rotation=rotation, method=method, n_factors=n_factors)
    fa.fit(data)
    
    # Extrair a matriz de componentes rotacionada
    loadings = fa.loadings_

    # Calcular a matriz de correlação observada
    observed_corr_matrix = np.corrcoef(data.T)
    
    # Calcular a matriz das correlações reproduzidas
    reproduced_corr_matrix = np.dot(loadings, loadings.T)
    
    # Calcular a matriz residual
    residual_matrix = observed_corr_matrix - reproduced_corr_matrix

    # Preencher diagonal principal com np.nan, pois é a variância numa matriz de correlações
    np.fill_diagonal(residual_matrix, np.nan)

    # Converter matriz residual em DataFrame
    residual_df = pd.DataFrame(residual_matrix, index=variables, columns=variables)

    # Substituir NaN por strings vazias
    residual_df = residual_df.map(lambda x: "" if pd.isna(x) else x)
    
    # Preparar tabela combinada
    headers = ["Reproduced Correlation"] + variables
    combined_rows = []

    combined_rows.append(["Correlation"] + [""] * len(variables))
    for i, var in enumerate(variables):
        combined_rows.append([var] + [f"{reproduced_corr_matrix[i, j]:.3f}" for j in range(len(variables))])

    combined_rows.append(["Residual"] + [""] * len(variables))
    for i, var in enumerate(variables):
        combined_rows.append([var] + [f"{residual_df.iloc[i, j]}" if residual_df.iloc[i, j] == "" else f"{residual_df.iloc[i, j]:.3f}" for j in range(len(variables))])
    
    # Mapeamento da extração
    elements_name = {
        'principal': ('Principal Component Analysis', 'PCA'),
        'minres': ('Principal Axis Factoring', 'PAF'),
        'ml': ('Maximum Likelihood', 'ML'),
    }
    
    if print_rc:
        # Exibir tabela formatada
        print(tabulate(combined_rows, headers, tablefmt="grid"))
        print(f"Extraction Method: {elements_name[method][0]}.")
        print(f"Rotation Method: {rotation} with Kaiser Normalization.")


    # Calcular índices de bondade do ajustamento
    p = observed_corr_matrix.shape[0]
    q = n_factors
    
    # GFI
    # Criar cópias das matrizes para não modificar os originais
    observed_corr_matrix_no_diag = np.copy(observed_corr_matrix)
    reproduced_corr_matrix_no_diag = np.copy(reproduced_corr_matrix)

    # Remover a diagonal principal (definir como zero)
    np.fill_diagonal(observed_corr_matrix_no_diag, 0)
    np.fill_diagonal(reproduced_corr_matrix_no_diag, 0)

    # Calcular o GFI sem a diagonal principal
    numerator = np.sum(np.square(observed_corr_matrix_no_diag - reproduced_corr_matrix_no_diag))
    denominator = np.sum(np.square(observed_corr_matrix_no_diag))
    GFI = 1 - (numerator / denominator)

    # AGFI
    AGFI = 1 - ((p * (p + 1) / (2 * q * (p - 1))) * (1 - GFI))

    # RMSR
    residual_matrix_no_diag = observed_corr_matrix_no_diag - reproduced_corr_matrix_no_diag
    RMSR = np.sqrt(np.mean(np.square(residual_matrix_no_diag)))

    GFI = f"{GFI:.4f}"
    AGFI = f"{AGFI:.4f}"
    RMSR = f"{RMSR:.4f}"

    # Exibir índices de bondade do ajustamento
    fit_indices = {
        'GFI': GFI,
        'AGFI': AGFI,
        'RMSR': RMSR
    }

    if print_fi: 
        print("\nFit Indices:")
        print(tabulate(fit_indices.items(), headers=['Index', 'Value'], tablefmt="grid"))