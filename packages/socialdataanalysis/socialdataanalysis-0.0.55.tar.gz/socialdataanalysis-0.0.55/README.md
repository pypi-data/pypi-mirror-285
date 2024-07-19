# socialdataanalysis

**Funções personalizadas para análise de dados nas ciências sociais, complementando o uso do SPSS.**

Este pacote oferece uma coleção de funções úteis para análise de dados, especialmente projetadas para complementar as capacidades do SPSS em pesquisas nas ciências sociais. As funções incluídas cobrem diversos aspectos da análise de associação, conforme descrito no livro [Análise de Dados Para Ciências Sociais: A Complementaridade do SPSS](https://silabo.pt/catalogo/informatica/aplicativos-estatisticos/livro/analise-de-dados-para-ciencias-sociais/).

## Recursos

- Análise de Associação
- Análise Fatorial Exploratória

## Instalação

Você pode instalar o pacote diretamente do PyPI usando pip:

```bash
pip install socialdataanalysis
```

## Uso

Aqui está um exemplo de como usar este pacote em um script Python:

```python
import socialdataanalysis as sda

# Exemplo de uso das funções de análise de associação
result = sda.association_analysis(data)
print(result)

# Exemplo de uso das funções de análise fatorial exploratória
factor_analysis_result = sda.exploratory_factor_analysis(data)
print(factor_analysis_result)
```

## Notebooks

Este pacote inclui notebooks de exemplo para demonstrar o uso das funções. Eles podem ser encontrados na pasta `notebooks` do pacote instalado.

## Contribuição

Se você deseja contribuir para este projeto, por favor, envie um pull request. Para problemas ou sugestões, utilize o issue tracker no GitHub.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Autor

Ricardo Mergulhão - [ricardomergulhao@gmail.com](mailto:ricardomergulhao@gmail.com)

## Agradecimentos

Agradecimentos especiais a todos os colaboradores e usuários deste pacote.
