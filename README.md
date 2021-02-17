Os códigos neste diretório têm como objetivo automatizar o processamento e a análise de dados meteorológicos do CEMADEN e do INMET, possibilitando a geração de relatórios em formato PDF contendo estatísticas de variáveis meteorológicas e algumas visualizações destes dados.


### Dependências
  * Python 3.6+
  * [Numpy](https://numpy.org/install/)
  * [Matplotlib](https://matplotlib.org/stable/users/installing.html)
  * [FPDF](https://pyfpdf.readthedocs.io/en/latest/)
  * [Pandas](https://pandas.pydata.org/getting_started.html)

Todas as etapas foram testadas em um computador Linux.


### Instalação
Para a instalação deste programa, basta baixar o repositório em formato ZIP e extraí-lo no local desejado ou cloná-lo.


### Utilização
A primeira etapa consiste na preparação dos dados de análise. O CEMADEN e o INMET utilizam a vírgula "," como separador decimal e o ponto e vírgula ";" como delimitador nos arquivos CSV. É necessário substituí-los pelo ponto "." e pela vírgula ",", respectivamente:

```bash
$ sed -i 's/,/./g' data1.csv
$ sed -i 's/;/,/g' data1.csv
```

Havendo múltiplos arquivos, repita o processo acima e concatene-os:

```bash
cat data1.csv data2.csv > data.csv
```

