# Faturas de teste imitando o jeito de cada banco (montadas à mão; layout aproximado)
F={}
F['nubank']=dict(D='2026-10',exp=dict(n=6,total=130.43,due='2026-10',holders=0),lines='''
Nu Pagamentos S.A. - Instituição de Pagamento
Olá, Kaue
Esta é a sua fatura de outubro, no valor de R$ 130,43
Data de vencimento: 10 OUT 2026
Período vigente: 03 SET a 03 OUT
RESUMO DA FATURA ATUAL
Fatura anterior R$ 2.000,00
Pagamento recebido −R$ 2.000,00
Total a pagar R$ 130,43
TRANSAÇÕES DE 03 SET A 03 OUT
05 SET Pagamento em 05 SET −R$ 2.000,00
05 SET Uber *Trip R$ 23,50
06 SET Amazon.com.br - Parcela 2/5 R$ 99,90
07 SET Estorno de "Loja X" −R$ 50,00
08 SET Netflix.com USD 10,00 R$ 55,80
08 SET IOF de "Netflix.com" R$ 1,23
''')
F['inter']=dict(D='2026-11',exp=dict(n=4,total=850.00,due='2026-11',holders=2),lines='''
Banco Inter S.A.
Fatura do cartão
Data de vencimento 10/11/2026
Total da fatura R$ 850,00
CARTÃO 5367****1234
Data Movimentação Beneficiário Valor
05 de out. 2026 SUPERMERCADO CONDOR - R$ 200,00
06 de out. 2026 LOJA Y (Parcela 02 de 03) - R$ 150,00
07 de out. 2026 PAGAMENTO ON LINE + R$ 1.000,00
Total CARTÃO 5367****1234 R$ 350,00
CARTÃO 5367****9876
08 de out. 2026 FARMACIA SAO JOAO - R$ 500,00
''')
F['c6']=dict(D='2026-11',exp=dict(n=5,total=412.30,due='2026-11',holders=2),lines='''
C6 Bank
Vencimento: 10/11/2026
Valor da fatura: R$ 229,90
Transações do cartão C6 Carbon Final 4321 - KAUE MANNES
05 out Posto Shell 180,00
06 out Spotify 21,90
09 out Ifood *Restaurante - Parcela 1/2 40,00
Transações do cartão Virtual Final 8765 - KAUE MANNES
10 out Apple.com/bill 9,90
12 out Estorno Spotify -21,90
Total de transações R$ 229,90
'''.replace('Total de transações R$ 229,90','Lançamentos futuros\n05 nov Ifood *Restaurante - Parcela 2/2 40,00'))
F['c6']['exp']['total']=229.90
F['bradesco']=dict(D='2026-11',exp=dict(n=5,total=1330.00,due='2026-11',holders=2),lines='''
Bradesco Cartões
Vencimento 10/11/2026
Total da fatura em real R$ 1.330,00
KAUE P MANNES Cartão 4551 XXXX XXXX 1122
Data Histórico Valor
05/10 MERCADO CONDOR CURITIBA 300,00
06/10 MAGAZINE LUIZA PARC 03/10 120,00
07/10 PAGTO. POR DEB EM C/C 2.000,00-
KAOANNA MANNES Cartão 4551 XXXX XXXX 3344
08/10 RENNER SHOPPING 410,00
09/10 DROGARIA RAIA 500,00
'''.replace('2.000,00-','2.000,00-'))
F['bradesco']['exp']['total']=1330.00
F['santander']=dict(D='2026-11',exp=dict(n=4,total=640.00,due='2026-11',holders=1),lines='''
Santander
Vencimento 10/11/2026
Total a Pagar R$ 640,00
KAUE P MANNES - 5412 XXXX XXXX 7788
Data Descrição Parcela R$ US$
05/10 LOJAS AMERICANAS 02/05 100,00
06/10 POSTO IPIRANGA 250,00
07/10 AMAZON PRIME 14,90
08/10 RESTAURANTE MADERO 275,10
''')
F['bb']=dict(D='2026-11',exp=dict(n=3,total=545.50,due='2026-11',holders=0),lines='''
Banco do Brasil - Ourocard
Vencimento 10/11/2026
Total da Fatura R$ 545,50
05.10 SUPERMERCADO ANGELONI 345,50
06.10 NETFLIX.COM 55,90
07.10 FARMACIA NISSEI 144,10
''')
F['caixa']=dict(D='2026-11',exp=dict(n=4,total=470.00,due='2026-11',holders=0),lines='''
CAIXA ECONÔMICA FEDERAL
Vencimento: 10/11/2026
Valor total da fatura: R$ 470,00
05/10 SUPERMERCADO BIG CURITIBA 300,00 D
06/10 POSTO BR 200,00 D
07/10 ESTORNO TARIFA 30,00 C
08/10 PADARIA PAO QUENTE 0,00 D
'''.replace('08/10 PADARIA PAO QUENTE 0,00 D','08/10 PADARIA PAO QUENTE 0,01 D'))
F['caixa']['exp']['total']=470.01
F['caixa']['lines']=F['caixa']['lines'].replace('R$ 470,00','R$ 470,01')
F['xp_intl']=dict(D='2026-11',exp=dict(n=4,total=389.75,due='2026-11',holders=0),lines='''
XP Investimentos - Cartão XP Visa Infinite
Data de vencimento: 15/11/2026
Total da fatura: R$ 389,75
Lançamentos
02/10/2026 OPENAI *CHATGPT SUBSCR USD 20,00 R$ 110,40
02/10/2026 IOF Transação Internacional R$ 3,86
14/10/2026 PADARIA BELA VISTA R$ 25,49
20/10/2026 HOTEL IBIS PARCELA 1 DE 2 R$ 250,00
''')
