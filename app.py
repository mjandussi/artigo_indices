import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(
    page_title="Indices",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Definir entes para seleção
lista_entes = [3304557, 3304904, 3301702, 3303500, 3301009]

# Dicionário para mapeamento de nomes dos municípios
ibge_to_nome = {
    3304557: "1_Rio de Janeiro",
    3304904: "2_São Gonçalo",
    3301702: "3_Duque de Caxias",
    3303500: "4_Nova Iguaçu",
    3301009: "5_Campos dos Goytacazes"
}

# Widgets Streamlit para inputs do usuário
entes_selecionados = st.multiselect("Selecione os municípios:", options=lista_entes, format_func=lambda x: ibge_to_nome[x])

#ano = st.number_input('Ano', min_value=2020, max_value=2025, value=2021)
ano = '2021'


resultados = []

# Verificar se entes foram selecionados
if entes_selecionados:
    for ente in entes_selecionados:

        ############################## IMPORTANDO os ANEXOS do RREO (6o Bimentre)
        ## Anexo 1
        link_rreo_1 = f'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo?an_exercicio={ano}&nr_periodo=6&co_tipo_demonstrativo=RREO&no_anexo=RREO-Anexo%2001&id_ente={ente}'
        rreo_1 = requests.get(link_rreo_1)
        df_rreo_1 = rreo_1.json()
        df_rreo_1 = pd.DataFrame(df_rreo_1["items"])
        time.sleep(0.5)

        ## Anexo 2 >> Demonstrativo da Execução da Despesa por Função/Subfunção (Anexo 02)
        link_rreo_2 = f'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo?an_exercicio={ano}&nr_periodo=6&co_tipo_demonstrativo=RREO&no_anexo=RREO-Anexo%2002&id_ente={ente}'
        #rreo_2 = requests.get(link_rreo_2, verify=False)
        rreo_2 = requests.get(link_rreo_2)
        df_rreo_2 = rreo_2.json()
        df_rreo_2 = pd.DataFrame(df_rreo_2["items"])
        time.sleep(0.5)

        ## Anexo 3
        link_rreo_3 = f'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo?an_exercicio={ano}&nr_periodo=6&co_tipo_demonstrativo=RREO&no_anexo=RREO-Anexo%2003&id_ente={ente}'
        rreo_3 = requests.get(link_rreo_3)
        df_rreo_3 = rreo_3.json()
        df_rreo_3 = pd.DataFrame(df_rreo_3["items"])
        time.sleep(0.5)

        ########################################################################################

        ############################## IMPORTANDO os ANEXOS da DCA 
        ## Anexo AB (BP)
        link_dca_ab = f'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca?an_exercicio={ano}&no_anexo=DCA-Anexo%20I-AB&id_ente={ente}'
        dca_ab = requests.get(link_dca_ab)
        df_dca_ab = dca_ab.json()
        df_dca_ab = pd.DataFrame(df_dca_ab["items"])
        time.sleep(0.5)

        ####################################################################################

        df_ibge = pd.read_excel('PIB dos Municípios - base de dados 2010-2021.xlsx')
        # Colunas selecionadas
        colunas_desejadas = [
            'Ano',
            'Sigla da Unidade da Federação',
            'Código do Município',
            'Nome do Município',
            'Produto Interno Bruto, \na preços correntes\n(R$ 1.000)',
            'Produto Interno Bruto per capita, \na preços correntes\n(R$ 1,00)'
        ]

        df_ibge_resu = df_ibge[colunas_desejadas]

        ####################################################################################

        populacao = pd.read_excel('POP_2022_Municipios.xlsx', header=1, dtype=object)
        #Deletar as Ultimas Linhas 
        populacao.drop(populacao.tail(35).index, inplace = True)
        populacao['POPULAÇÃO'] = pd.to_numeric(populacao['POPULAÇÃO'],errors = 'coerce')
        populacao['COD. UF'] = populacao['COD. UF'].apply(str)
        populacao['COD. MUNIC'] = populacao['COD. MUNIC'].apply(str)
        populacao['cod_ibge'] = populacao['COD. UF'] + populacao['COD. MUNIC']
        populacao_valor = populacao['POPULAÇÃO'].values[0]

        ####################################################################################

        # Buscar PIB do município
        pib_munic = df_ibge.query(f'`Código do Município` == {ente} and Ano == {ano}')
        nro_habitantes_df = populacao.query(f'cod_ibge == "{ente}"')

        # Consultar dados RREO e DCA
        rec_rreo_1_df = df_rreo_1.query('coluna == "Até o Bimestre (c)" & cod_conta == "TotalReceitas"')
        iptu_rreo_3_df = df_rreo_3[df_rreo_3["conta"].str.contains("IPTU")]
        iptu_rreo_3_df = iptu_rreo_3_df.query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')
        iss_rreo_3_df = df_rreo_3[df_rreo_3["conta"].str.contains("ISS")]
        iss_rreo_3_df = iss_rreo_3_df.query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')
        div_ativa_trib_dca_ab_df = df_dca_ab.query('cod_conta == "P1.1.2.5.0.00.00" or cod_conta == "P1.2.1.1.1.04.00"')
        despesa_total_df = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "TotalDespesas"')
        despesa_investimentos_df = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "Investimentos"')
        despesa_saude_df = df_rreo_2.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)" & conta == "Saúde" & cod_conta == "RREO2TotalDespesas"')
        despesa_educacao_df = df_rreo_2.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)" & conta == "Educação" & cod_conta == "RREO2TotalDespesas"')
        legislativo_rreo_2_df = df_rreo_2.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)" & conta == "Legislativa" & cod_conta == "RREO2TotalDespesas"')
        rec_trib_rreo_1_df = df_rreo_1.query('coluna == "Até o Bimestre (c)" & cod_conta == "ReceitaTributaria"')
        tranf_corr_rreo_1_df = df_rreo_1.query('coluna == "Até o Bimestre (c)" & cod_conta == "TransferenciasCorrentes"')
        at_circ_df = df_dca_ab.query('cod_conta == "P1.1.0.0.0.00.00"')
        at_circ_disp_df = df_dca_ab.query('cod_conta == "P1.1.1.0.0.00.00"')
        at_nao_circ_df = df_dca_ab.query('cod_conta == "P1.2.0.0.0.00.00"')
        pass_circ_df = df_dca_ab.query('cod_conta == "P2.1.0.0.0.00.00"')
        pass_nao_circ_df = df_dca_ab.query('cod_conta == "P2.2.0.0.0.00.00"')
        emp_rreo_1_df = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" & cod_conta == "TotalDespesas"')
        pago_rreo_1_df = df_rreo_1.query('coluna == "DESPESAS PAGAS ATÉ O BIMESTRE (j)" & cod_conta == "TotalDespesas"')
        vlr_restit_df = df_dca_ab.query('cod_conta == "P2.1.8.8.0.00.00"')
        estoques_df = df_dca_ab.query('cod_conta == "P1.1.5.0.0.00.00"')
        ativo_df = df_dca_ab.query('cod_conta == "P1.0.0.0.0.00.00"')
        passivo_df = df_dca_ab.query('cod_conta == "P2.1.0.0.0.00.00" | cod_conta == "P2.2.0.0.0.00.00"')
        imobilizado_df = df_dca_ab.query('cod_conta == "P1.2.3.0.0.00.00"')
        investimentos_ativo_df = df_dca_ab.query('cod_conta == "P1.1.4.0.0.00.00"')
        pl_df = df_dca_ab.query('cod_conta == "P2.3.0.0.0.00.00"')
        dps_corr_liq_rreo_1_df = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "DespesasCorrentes"')
        rec_corre_rreo_1_df = df_rreo_1.query('coluna == "Até o Bimestre (c)" & cod_conta == "ReceitasCorrentes"')
        dps_capital_liq_rreo_1_df = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "DespesasDeCapital"')
        rec_capital_rreo_1_df = df_rreo_1.query('coluna == "Até o Bimestre (c)" & cod_conta == "ReceitasDeCapital"')
        dps_pess_e_encarg_liq_rreo_1_df = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "PessoalEEncargosSociais"')
        dps_invest_liq_rreo_1_df = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "Investimentos"')
        rcl_rreo3_df = df_rreo_3.query('cod_conta == "RREO3ReceitaCorrenteLiquida" and coluna == "TOTAL (ÚLTIMOS 12 MESES)"')
        rec_prevista_df = df_rreo_1.query('coluna == "PREVISÃO ATUALIZADA (a)" & cod_conta == "TotalReceitas"')
        desp_fixada_df = df_rreo_1.query('coluna == "DOTAÇÃO INICIAL (d)" & cod_conta == "TotalDespesas"')
        oper_cred_df = df_rreo_1.query('coluna == "Até o Bimestre (c)" & cod_conta == "ReceitasDeOperacoesDeCredito"')
        juros_e_encargos_div_df = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "JurosEEncargosDaDivida"')

        # Extrair valores das tabelas
        nro_habitantes = nro_habitantes_df['POPULAÇÃO'].sum()
        pib_munic_valor = pib_munic['Produto Interno Bruto per capita, \na preços correntes\n(R$ 1,00)'].sum()
        rec_rreo_1 = rec_rreo_1_df['valor'].sum()
        iptu_rreo_3 = iptu_rreo_3_df['valor'].sum()
        iss_rreo_3 = iss_rreo_3_df['valor'].sum()
        div_ativa_trib_dca_ab = div_ativa_trib_dca_ab_df['valor'].sum()
        despesa_educacao = despesa_educacao_df['valor'].sum()
        despesa_total = despesa_total_df['valor'].sum()
        despesa_investimentos = despesa_investimentos_df['valor'].sum()
        despesa_saude = despesa_saude_df['valor'].sum()
        despesa_educacao = despesa_educacao_df['valor'].sum()
        legislativo_rreo_2 = legislativo_rreo_2_df['valor'].sum()
        rec_trib_rreo_1 = rec_trib_rreo_1_df['valor'].sum()
        tranf_corr_rreo_1 = tranf_corr_rreo_1_df['valor'].sum()
        at_circ = at_circ_df['valor'].sum()
        at_circ_disp = at_circ_disp_df['valor'].sum()
        at_nao_circ = at_nao_circ_df['valor'].sum()
        pass_circ = pass_circ_df['valor'].sum()
        pass_nao_circ = pass_nao_circ_df['valor'].sum()
        emp_rreo_1 = emp_rreo_1_df['valor'].sum()
        pago_rreo_1 = pago_rreo_1_df['valor'].sum()
        vlr_restit = vlr_restit_df['valor'].sum()
        estoques = estoques_df['valor'].sum()
        ativo = ativo_df['valor'].sum()
        passivo = passivo_df['valor'].sum()
        imobilizado = imobilizado_df['valor'].sum()
        investimentos_ativo = investimentos_ativo_df['valor'].sum()
        pl = pl_df['valor'].sum()
        dps_corr_liq_rreo_1 = dps_corr_liq_rreo_1_df['valor'].sum()
        rec_corre_rreo_1 = rec_corre_rreo_1_df['valor'].sum()
        dps_capital_liq_rreo_1 = dps_capital_liq_rreo_1_df['valor'].sum()
        rec_capital_rreo_1 = rec_capital_rreo_1_df['valor'].sum()
        dps_pess_e_encarg_liq_rreo_1 = dps_pess_e_encarg_liq_rreo_1_df['valor'].sum()
        dps_invest_liq_rreo_1 = dps_invest_liq_rreo_1_df['valor'].sum()
        rcl = rcl_rreo3_df['valor'].sum()
        rec_prevista = rec_prevista_df['valor'].sum()
        desp_fixada = desp_fixada_df['valor'].sum()
        oper_cred = oper_cred_df['valor'].sum()
        juros_e_encargos_div = juros_e_encargos_div_df['valor'].sum()


        # Calcular indicadores
        pib_per_capita = pib_munic_valor
        receita_total_per_capita = rec_rreo_1 / nro_habitantes
        iptu_per_capita = iptu_rreo_3 / nro_habitantes
        iss_per_capita = iss_rreo_3 / nro_habitantes
        div_ativa_per_capita = div_ativa_trib_dca_ab / nro_habitantes
        despesa_orcam_per_capita = despesa_total / nro_habitantes
        investimentos_per_capita = despesa_investimentos / nro_habitantes
        saude_per_capita = despesa_saude / nro_habitantes
        educacao_per_capita = despesa_educacao / nro_habitantes
        transf_legislativo_per_capita = legislativo_rreo_2 / nro_habitantes
        rec_trib_per_capita = rec_trib_rreo_1 / nro_habitantes
        rec_transf_per_capita = tranf_corr_rreo_1 / nro_habitantes
        liquidez_imediata = at_circ_disp / pass_circ
        #liquidez_rp = at_circ_disp / rp
        liquidez_recurso_terceiros = at_circ_disp / vlr_restit
        liquidez_corrente = at_circ / pass_circ
        #liquidez_com_aut_orcam = 
        liquidez_seca = (at_circ - estoques) / pass_circ
        liquidez_geral = (at_circ + at_nao_circ)/ (pass_circ + pass_nao_circ)
        #liquidez_com_op_cred = 
        #liquidez_com_precat = 
        solvencia_geral = ativo / (pass_circ + pass_nao_circ)
        endivid_geral = (passivo / ativo) * 100
        composicao_exigibilidades = (pass_circ/ passivo) * 100
        imobilizacao_pl = ((imobilizado + investimentos_ativo) / pl) * 100
        comprometimento_corrente = (dps_corr_liq_rreo_1 / rec_corre_rreo_1) * 100
        comprometimento_capital = (dps_capital_liq_rreo_1 / rec_capital_rreo_1) * 100
        gasto_pessoal_dps_orcam = (dps_pess_e_encarg_liq_rreo_1 / dps_corr_liq_rreo_1) * 100
        gasto_invest_dps_orcam =  (dps_invest_liq_rreo_1 / dps_corr_liq_rreo_1) * 100
        gasto_pessoal_rcl = (dps_pess_e_encarg_liq_rreo_1 / rcl) * 100
        rec_corr_proprias = ((rec_corre_rreo_1 - tranf_corr_rreo_1) / rec_corre_rreo_1) * 100
        exec_orcam_rec = (rec_rreo_1 / rec_prevista) * 100
        exec_orcam_desp = (despesa_total / desp_fixada) * 100
        resultado_exec_orcam = (despesa_total / rec_rreo_1) * 100
        autonomia_orcam = ((rec_corre_rreo_1 - tranf_corr_rreo_1) / despesa_total) * 100
        amortizacao_e_refinanc_div = (oper_cred / despesa_total) * 100
        encargos_div_dps_corr = (juros_e_encargos_div / despesa_total) * 100


        
        # Adicionar à lista de resultados
        resultados.append({
            "Município": ente,
            "A1_PIB per Capita": pib_per_capita,
            "A2_Receita Total per Capita": receita_total_per_capita,
            "A3_IPTU per Capita": iptu_per_capita,
            "A4_ISS per Capita": iss_per_capita,
            "A5_Dívida Ativa per Capita": div_ativa_per_capita,
            "B1_Despesas Orçamentárias per Capita": despesa_orcam_per_capita,
            "B2_Investimentos per Capita": investimentos_per_capita,
            "B3_Gastos com Saúde per Capita": saude_per_capita,
            "B4_Gastos com Educação per Capita": educacao_per_capita,
            "B5_Transferências para o Legislativo per Capita": transf_legislativo_per_capita,
            "C1_Receita Tributária per Capita": rec_trib_per_capita,
            "C2_Receita de Transferências per Capita": rec_transf_per_capita,
            "D1_Liquidez Instantânea ou Imediata": liquidez_imediata,
            #"D2_Liquidez com restos a pagar": liquidez_rp,
            "D3_Liquidez com recursos de terceiros": liquidez_recurso_terceiros,
            "D4_Liquidez Corrente": liquidez_corrente,
            #"E1_Liquidez com autorização orçamentária": liquidez_com_aut_orcam,
            "E2_Liquidez Seca": liquidez_seca,
            "E3_Liquidez Geral": liquidez_geral,
            #"E4_Liquidez com operações de crédito": liquidez_com_op_cred,
            #"E5_Liquidez com precatórios": liquidez_com_precat,
            "E6_Solvência Geral": solvencia_geral,
            "F1_Endividamento Geral": endivid_geral,
            "F2_Composição das Exigibilidades": composicao_exigibilidades,
            "F3_Imobilização do Patrimônio Líquido ou Capital Próprio": imobilizacao_pl,
            "F4_Grau de Comprometimento da Categoria Econômica Corrente": comprometimento_corrente,
            "F5_Grau de Comprometimento da Categoria Econômica de Capital": comprometimento_capital,
            "G1_Grau de Gasto com Pessoal em relação a Despesa Orçamentária": gasto_pessoal_dps_orcam,
            "G2_Grau de Investimento em relação a Despesa Orçamentária": gasto_invest_dps_orcam,
            "G3_Grau de Gasto com Pessoal em relação a Receita corrente Líquida": gasto_pessoal_rcl,
            "G4_Grau de Receitas Correntes Próprias ": rec_corr_proprias,
            "H1_Grau de Execução Orçamentária da Receita": exec_orcam_rec,
            "H2_Grau de Execução Orçamentária da Despesa": exec_orcam_desp,
            "H3_Grau do Resultado da Execução Orçamentária": resultado_exec_orcam,
            "H4_Grau de Autonomia Orçamentária": autonomia_orcam,
            "H5_Grau de Amortização e refinanciamento de dívida": amortizacao_e_refinanc_div,
            "H6_Grau de Encargos da dívida na despesa corrente": encargos_div_dps_corr,
        })
        time.sleep(0.5)

    


    # Converter para DataFrame
    df_resultados = pd.DataFrame(resultados)
    #df_resultados['Ano'] = ano  # Adiciona a coluna Ano

    # ibge_to_nome = {
    #     3304557: "1_Rio de Janeiro",
    #     3304904: "2_São Gonçalo",
    #     3301702: "3_Duque de Caxias",
    #     3303500: "4_Nova Iguaçu",
    #     3301009: "5_Campos dos Goytacazes"
    # }

    # Substituir códigos IBGE pelos nomes dos municípios
    df_resultados['Município'] = df_resultados['Município'].replace(ibge_to_nome)


    # Redefinir layout, usando um pivot
    df_pivot = df_resultados.melt(id_vars=["Município"], var_name="Índice", value_name="Valor")
    tabela_final = df_pivot.pivot_table(index="Índice", columns="Município", values="Valor")

    # Calcular a média simples de cada linha
    tabela_final['Média'] = tabela_final.mean(axis=1)

    # Dicionários para interpretações e fórmulas
    interpretacoes = {
            "A1_PIB per Capita": "Renda média por habitante",
            "A2_Receita Total per Capita": "Arrecadação por habitante",
            "A3_IPTU per Capita": "Arrecadação de IPTU por habitante",
            "A4_ISS per Capita": "Arrecadação de ISS por habitante",
            "A5_Dívida Ativa per Capita": "Valor em Dívida Ativa por habitante",
            "B1_Despesas Orçamentárias per Capita": "Quanto representa a Despesa por habitantes?",
            "B2_Investimentos per Capita": "Quanto representa o investimento por habitantes?",
            "B3_Gastos com Saúde per Capita": "Quanto representa o gasto com Saúde por pessoa?",
            "B4_Gastos com Educação per Capita": "Quanto representa o gasto com Educação por pessoa?",
            "B5_Transferências para o Legislativo per Capita": "Quanto representa o gasto com Legislativo por habitante?",
            "C1_Receita Tributária per Capita": "Quanto representa a Receita Tributária por habitante?",
            "C2_Receita de Transferências per Capita": "Quanto representa a Receita de Transferências por habitante?",
            "D1_Liquidez Instantânea ou Imediata": "Hoje consegue pagar suas dívidas de um ano?",
            #"D2_Liquidez com restos a pagar": "Hoje consegue pagar os Restos a Pagar?",
            "D3_Liquidez com recursos de terceiros": "Hoje consegue pagar os recursos de terceiros? ",
            "D4_Liquidez Corrente": "Durante um ano consegue pagar suas dívidas?",
            #"E1_Liquidez com autorização orçamentária": "Durante um ano consegue pagar suas dívidas com Recursos Orçamentários?",
            "E2_Liquidez Seca": "Sem Estoque consegue pagar suas dívidas de um ano?",
            "E3_Liquidez Geral": "No futuro conseguirá pagar suas dívidas?",
            #"E4_Liquidez com operações de crédito": "No futuro conseguirá pagar suas dívidas Onerosas?",
            #"E5_Liquidez com precatórios": "No futuro conseguirá pagar suas dívidas judiciais?",
            "E6_Solvência Geral": "No geral conseguirá pagar suas Dívidas?",
            "F1_Endividamento Geral": "Quanto do Ativo está Endividado?",
            "F2_Composição das Exigibilidades": "Quanto representa o PC do total da Dívida?",
            "F3_Imobilização do Patrimônio Líquido ou Capital Próprio": "Quanto os Ativos Investimento e Imobilizado usaram do Patrimônio Líquido?",
            "F4_Grau de Comprometimento da Categoria Econômica Corrente": "Quanto a Despesa Corrente utilizou da Receita Corrente?",
            "F5_Grau de Comprometimento da Categoria Econômica de Capital": "Quanto a Despesa de Capital utilizou da Receita de Capital?",
            "G1_Grau de Gasto com Pessoal em relação a Despesa Orçamentária": "Quanto representou o Gasto com Pessoal em relação a Despesa Orçamentária?",
            "G2_Grau de Investimento em relação a Despesa Orçamentária": "Quanto representou o Investimento em relação a Despesa Orçamentária?",
            "G3_Grau de Gasto com Pessoal em relação a Receita corrente Líquida": "Quanto representou o Gasto com Pessoal em relação Receita corrente Líquida?",
            "G4_Grau de Receitas Correntes Próprias ": "Qual o Grau de independência das Receitas Correntes? ",
            "H1_Grau de Execução Orçamentária da Receita": "Quanto da Receita foi Executada?",
            "H2_Grau de Execução Orçamentária da Despesa": "Quanto da Despesa foi Executada?",
            "H3_Grau do Resultado da Execução Orçamentária": "Qual o grau do resultado da execução orçamentária?",
            "H4_Grau de Autonomia Orçamentária": "Quanto representa a receita própria em relação a despesa executada",
            "H5_Grau de Amortização e refinanciamento de dívida": "Quanto representam as operações de crédito em relação a despesa executada",
            "H6_Grau de Encargos da dívida na despesa corrente": "Quanto representa a despesa financeira da despesa orçamentária",
    }

    formulas = {
            "A1_PIB per Capita": "PIB Total/ Nr Habitantes",
            "A2_Receita Total per Capita": "Receita Arrecadada / Nr Habitantes",
            "A3_IPTU per Capita": "IPTU / Nr Habitantes",
            "A4_ISS per Capita": "ISS / Nr Habitantes",
            "A5_Dívida Ativa per Capita": "Dívida Ativa / Nr Habitante",
            "B1_Despesas Orçamentárias per Capita": "Despesa Executada / Nr Habitantes",
            "B2_Investimentos per Capita": "Investimentos / Nr Habitantes",
            "B3_Gastos com Saúde per Capita": "Despesas com Saúde / Nr Habitantes",
            "B4_Gastos com Educação per Capita": "Despesas com Educação / Nr Habitantes",
            "B5_Transferências para o Legislativo per Capita": "Transferência para o Legislativo / Nr de Habitantes",
            "C1_Receita Tributária per Capita": "Receita Tributária / Nr de Habitantes",
            "C2_Receita de Transferências per Capita": "Receita de Transferências / Nr de Habitantes",
            "D1_Liquidez Instantânea ou Imediata": "Ativo Circulante Disponível / Passivo Circulante",
            #"D2_Liquidez com restos a pagar": "Ativo Circulante Disponibilidade / Restos a pagar processados",
            "D3_Liquidez com recursos de terceiros": "Ativo Circulante Disponibilidade / Depósitos de Diversas Origens",
            "D4_Liquidez Corrente": "Ativo Circulante / Passivo Circulante",
            #"E1_Liquidez com autorização orçamentária": "(Ativo Realizável – Recursos Extraorçamentários) / (Passivo Exigível – Dívidas Extraorç)",
            "E2_Liquidez Seca": "(Ativo circulante – Estoques) / Passivo Circulante",
            "E3_Liquidez Geral": "(Ativo Circulante + Ativo Não Circulante Direitos) / (Passivo Circulante + Passivo Não Circulante)",
            #"E4_Liquidez com operações de crédito": "Ativos Realizáveis / Passivos Exigíveis Onerosos ou com Operações de crédito e Financiamentos",
            #"E5_Liquidez com precatórios": "Ativos Realizáveis / Passivos Exigíveis Judiciais ou Precatórios a pagar",
            "E6_Solvência Geral": "Ativo Total / Passivo Exigível",
            "F1_Endividamento Geral": "(Passivo Exigível / Ativo Total) x 100",
            "F2_Composição das Exigibilidades": "(Passivo Circulante / Passivo Exigível) x 100",
            "F3_Imobilização do Patrimônio Líquido ou Capital Próprio": "((Ativos Investimento + Imobilizado) / Patrimônio Líquido) x 100",
            "F4_Grau de Comprometimento da Categoria Econômica Corrente": "(Despesas Correntes / Receitas Correntes) x 100",
            "F5_Grau de Comprometimento da Categoria Econômica de Capital": "(Despesas de Capital / Receitas de Capital) x 100",
            "G1_Grau de Gasto com Pessoal em relação a Despesa Orçamentária": "(Pessoal Ativo e Encargos / Despesas Orçamentárias) x 100",
            "G2_Grau de Investimento em relação a Despesa Orçamentária": "(Investimentos / Despesas Orçamentária) x 100",
            "G3_Grau de Gasto com Pessoal em relação a Receita corrente Líquida": "(Pessoal Ativo e Encargos / Receita corrente Líquida) x 100",
            "G4_Grau de Receitas Correntes Próprias ": "((Receitas Correntes – Transferências) / Receitas Correntes) x 100",
            "H1_Grau de Execução Orçamentária da Receita": "(Receita Executada / Receita Prevista) x 100",
            "H2_Grau de Execução Orçamentária da Despesa": "(Despesa Executada / Despesa Fixada) x 100",
            "H3_Grau do Resultado da Execução Orçamentária": "(Despesa Executada / Receita Executada) x 100",
            "H4_Grau de Autonomia Orçamentária": "((Receitas Correntes – Transferências) / despesas totais) x 100",
            "H5_Grau de Amortização e refinanciamento de dívida": "(Operações de Crédito / despesas totais) x 100",
            "H6_Grau de Encargos da dívida na despesa corrente": "(Juros e encargos da dívida / Despesas Executadas) x 100",
    }



    # Adicionando as novas colunas ao DataFrame
    tabela_final["Interpretações"] = tabela_final.index.map(interpretacoes)
    tabela_final["Fórmulas"] = tabela_final.index.map(formulas)
    tabela_final["Ano"] = 2021



    # # Criar as colunas de variação percentual e classificação
    # for municipio in ["1_Rio de Janeiro", "2_São Gonçalo", "3_Duque de Caxias", "4_Nova Iguaçu", "5_Campos dos Goytacazes"]:
    #     # Calcular a variação percentual em relação à média
    #     tabela_final[f'{municipio}_Variação (%)'] = ((tabela_final[municipio] - tabela_final["Média"]) / tabela_final["Média"]) * 100

    #     # Classificar com base na variação percentual
    #     def classificar_variacao(variacao):
    #         # Converter a variação em um valor absoluto
    #         variacao_absoluta = abs(variacao)
    #         if variacao_absoluta <= 10:
    #             return 1
    #         elif 11 <= variacao_absoluta <= 30:
    #             return 2
    #         elif 31 <= variacao_absoluta <= 50:
    #             return 3
    #         else:  # 51% a 100% ou mais
    #             return 4

    #     # Aplicar a classificação
    #     tabela_final[f'{municipio}_Classificação'] = tabela_final[f'{municipio}_Variação (%)'].apply(classificar_variacao)


    # Exibir os resultados no app do Streamlit
    st.dataframe(tabela_final)
