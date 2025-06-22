import time
import logging
import threading

def executar_logica_passageiro(id_passageiro_unico, obj_estado, params_cenario):
    tempo_individual_acao = params_cenario["TEMPO_INDIVIDUAL_EMBARQUE_DESEMBARQUE_SEG"]

    tempo_real_chegada = time.time()
    logging.info(f"Passageiro {id_passageiro_unico:03d} chegou.")

    # Entra na fila e sinaliza ao carro que há um passageiro esperando.
    obj_estado.trava_acesso_geral.acquire()
    obj_estado.passageiros_na_fila_contador += 1
    obj_estado.fila_de_espera_passageiros.append(id_passageiro_unico)
    obj_estado.trava_acesso_geral.release()
    
    obj_estado.semaforo_passageiro_na_fila.release() 

    # Espera ser chamado para embarcar.
    obj_estado.semaforo_carro_pode_chamar_passageiro.acquire()
    
    # Foi chamado, agora realiza o embarque.
    obj_estado.trava_acesso_geral.acquire()
    id_carro_de_embarque = obj_estado.id_carro_processando_embarque 
    obj_estado.trava_acesso_geral.release()

    # Calcula o tempo de espera na fila.
    tempo_real_inicio_embarque = time.time()
    tempo_espera_calculado_seg = tempo_real_inicio_embarque - tempo_real_chegada
    
    obj_estado.trava_acesso_geral.acquire()
    obj_estado.lista_tempos_espera_fila.append(tempo_espera_calculado_seg)
    obj_estado.trava_acesso_geral.release()

    logging.info(f"Passageiro {id_passageiro_unico:03d} embarcando no Carro {id_carro_de_embarque}. (Esperou {tempo_espera_calculado_seg:.2f}s)")
    time.sleep(tempo_individual_acao) 
    logging.info(f"Passageiro {id_passageiro_unico:03d} embarcou no Carro {id_carro_de_embarque}.")
    
    # Confirma que o embarque foi concluído.
    obj_estado.semaforo_passageiro_confirmou_embarque.release() 

    # Agora, espera a viagem terminar e ser chamado para desembarcar.
    obj_estado.semaforo_carro_pode_liberar_passageiro.acquire()
    
    #Lê o ID do carro novamente para garantir que a mensagem de log seja precisa.
    obj_estado.trava_acesso_geral.acquire()
    id_carro_de_desembarque = obj_estado.id_carro_processando_embarque
    obj_estado.trava_acesso_geral.release()
    
    logging.info(f"Passageiro {id_passageiro_unico:03d} desembarcando do Carro {id_carro_de_desembarque}.")
    time.sleep(tempo_individual_acao) 
    logging.info(f"Passageiro {id_passageiro_unico:03d} desembarcou do Carro {id_carro_de_desembarque}.")

    # Confirma que o desembarque foi concluído.
    obj_estado.semaforo_passageiro_confirmou_desembarque.release()


