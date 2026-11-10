# ML Viewer

Aplicação desktop para cadastrar conjuntos de dados, importar modelos, executar experimentos e exportar o resultado. Este roteiro usa os arquivos de `examples/`.

## 1. Requisito

Python 3.11 ou superior. Ative um ambiente virtual antes de instalar.

```bash
python -m venv .venv
source .venv/bin/activate
```

## 2. Instalação

```bash
pip install "git+https://github.com/hott-henrique/ml-viewer.git"
ml-viewer
```

A janela abre na tela de Datasets. A barra lateral dá acesso a Datasets, Modelos, Análises e Experimentos.

## 3. Cadastrar o Iris

Em Datasets, escolha incluir um conjunto.

- Nome: `Iris`
- Paradigma: classificação
- Cabeçalho presente: marcado
- Arquivo de treino: `examples/data/iris_train.csv`
- Arquivo de teste: `examples/data/iris_test.csv`
- Coluna alvo: `species`

## 4. Cadastrar os imóveis

Inclua outro conjunto.

- Nome: `Imóveis`
- Paradigma: regressão
- Cabeçalho presente: marcado
- Arquivo de treino: `examples/data/imoveis_train.csv`
- Arquivo de teste: `examples/data/imoveis_test.csv`
- Coluna alvo: `MedHouseVal`

## 5. Importar um modelo

Em Modelos, use Importar e selecione `examples/tutorial/tutorial_classification.py`.

Cada arquivo de `examples/tutorial/` cobre um tipo de problema:

| Arquivo | Tipo |
|---|---|
| `tutorial_classification.py` | Classificação |
| `tutorial_regression.py` | Regressão |
| `tutorial_clustering.py` | Agrupamento |
| `tutorial_dimensionality_reduction.py` | Redução de dimensionalidade |
| `tutorial_association_rules.py` | Regras de associação |
| `tutorial_semi_supervised_classification.py` | Classificação semi-supervisionada |
| `tutorial_semi_supervised_regression.py` | Regressão semi-supervisionada |
| `tutorial_reinforcement.py` | Aprendizado por reforço |

## 6. Importar a análise

Em Análises, importe `examples/tutorial/tutorial_analysis_classification.py`. Ela calcula a fração de previsões iguais aos rótulos reais.

## 7. Executar um experimento de classificação

Em Experimentos, comece uma execução.

- Fonte: Dataset
- Conjunto: `Iris`
- Modelo: o classificador de tutorial
- Análise: a acurácia de tutorial, com um rótulo qualquer

Confirme a execução. Ver resultados abre as métricas daquela execução. Exportar gera um arquivo compactado com o registro, as métricas e, quando houver, o modelo treinado.

## 8. Executar o agente

Importe `examples/tutorial/tutorial_reinforcement.py` em Modelos. Em uma nova execução:

- Fonte: Ambiente (RL)
- Ambiente: `CartPole-v1`
- Modelo: o agente de tutorial
- Episódios: um inteiro maior ou igual a 1

Não há CSV. O CartPole já vem com o Gymnasium instalado junto com a aplicação.
