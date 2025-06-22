# src/constantes.py

PARAMETROS_CENARIO_1 = {
    "ID_CENARIO": 1,
    "NUM_PASSAGEIROS": 65,
    "NUM_CARROS": 1,
    "CAPACIDADE_CARRO": 5,
    "TEMPO_PASSEIO_SEG": 60,
    "TEMPO_TOTAL_EMBARQUE_DESEMBARQUE_SEG": 25,
    "INTERVALO_MIN_CHEGADA_SEG": 10,
    "INTERVALO_MAX_CHEGADA_SEG": 20
}

PARAMETROS_CENARIO_2 = {
    "ID_CENARIO": 2,
    "NUM_PASSAGEIROS": 65,
    "NUM_CARROS": 2,
    "CAPACIDADE_CARRO": 5,
    "TEMPO_PASSEIO_SEG": 60,
    "TEMPO_TOTAL_EMBARQUE_DESEMBARQUE_SEG": 25,
    "INTERVALO_MIN_CHEGADA_SEG": 10,
    "INTERVALO_MAX_CHEGADA_SEG": 20
}

PARAMETROS_CENARIO_3 = {
    "ID_CENARIO": 3,
    "NUM_PASSAGEIROS": 1000,
    "NUM_CARROS": 4,  # Você pode ajustar o 'N' aqui para o cenário N
    "CAPACIDADE_CARRO": 10,
    "TEMPO_PASSEIO_SEG": 60,
    "TEMPO_TOTAL_EMBARQUE_DESEMBARQUE_SEG": 25,
    "INTERVALO_MIN_CHEGADA_SEG": 10,
    "INTERVALO_MAX_CHEGADA_SEG": 20
}

def obter_parametros_cenario(numero_cenario):
    if numero_cenario == 1:
        return PARAMETROS_CENARIO_1
    elif numero_cenario == 2:
        return PARAMETROS_CENARIO_2
    else:  # Padrão ou 3
        return PARAMETROS_CENARIO_3

def calcular_tempo_individual_passageiro_embarque(params):
    capacidade = params["CAPACIDADE_CARRO"]
    tempo_total = params["TEMPO_TOTAL_EMBARQUE_DESEMBARQUE_SEG"]
    return tempo_total / capacidade if capacidade > 0 else 0