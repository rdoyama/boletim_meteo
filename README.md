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

Finalmente, copie os arquivos processados para o diretório **data**, modifique o arquivo **config.ini** e execute:

```python
$ python3 auto.py
```

**Nota**: Se um dos arquivos não estiver presente, preencha o diretório no arquivo de configuração com uma string vazia. Os horários para início e término das análises devem estar no formato YYYY-MM-DD HH. Em caso de intervalos grandes (vários dias ou maiores), pode ser necessário alterar as configurações dos plots nos códigos. As demais variáveis do arquivo de configuração devem estar preenchidas com "True" ou "False".

O resultado da execução do programa é um arquivo em formato PDF "report.py" no diretório principal. 
