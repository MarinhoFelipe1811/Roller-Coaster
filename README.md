# 🎢 Simulação de Simulação de Montanha-Russa Multithread

## ⚙️ Conceitos Principais
O núcleo do projeto é a resolução de um problema clássico de concorrência, similar ao problema do produtor-consumidor, aplicado a um cenário do mundo real:

- Passageiros (Produtores): Chegam à atração em intervalos de tempo variados e "produzem" a si mesmos na fila de espera.
- Carros (Consumidores): "Consomem" os passageiros da fila para iniciar uma viagem.
  
Recursos Críticos Compartilhados:
- A Estação de Embarque: Apenas um carro pode realizar o processo de embarque/desembarque por vez.
- O Trilho do Passeio: Apenas um carro pode estar no trilho realizando o passeio por vez.
- A Fila de Passageiros: É uma estrutura de dados compartilhada que precisa ser acessada de forma segura (thread-safe).

Para gerenciar o acesso a esses recursos e coordenar as ações entre as threads, a simulação faz uso intensivo de Semáforos e Travas.

## ✨ Funcionalidades

Visualização em Tempo Real - Uma interface gráfica criada com Pygame mostra o estado atual da simulação, incluindo:
- A posição e o status de cada carro (na estação, embarcando, em passeio, desembarcando).
- O número de passageiros na fila de espera.
- Os passageiros dentro de cada carro.
- O status geral da simulação (passageiros transportados).
  
- Configuração de Cenários: É possível alterar facilmente os parâmetros da simulação (número de carros, capacidade, número de passageiros, tempos de duração) através do arquivo src/constantes.py.
- Sincronização Complexa: Implementa uma lógica robusta para evitar condições de corrida e deadlocks, garantindo que carros e passageiros interajam corretamente.
- Logging Detalhado: O console exibe um log detalhado de todos os eventos importantes (chegada de passageiros, início de embarque, partida de carros, etc.), com timestamps precisos.
- Relatório de Desempenho: Ao final da simulação, um relatório é gerado no console com métricas importantes:
- Tempo total da simulação.
- Tempos de espera (mínimo, máximo e médio) dos passageiros na fila.
- Número total de viagens.
- Eficiência da atração (percentual do tempo total em que os carros estiveram em movimento).

## 🚀 Como Executar
- Certifique-se de ter o Python 3 instalado. Você precisará da biblioteca pygame.
- Clone este repositório.
- Execute a simulação a partir do terminal. Você pode escolher o cenário desejado.

## 🧠 Mecanismos de Sincronização Detalhados

A robustez da simulação depende de vários semáforos, cada um com uma responsabilidade específica:
- trava_acesso_geral: Um semáforo binário (lock) usado para proteger o acesso a contadores e listas simples (como a fila de passageiros), garantindo que as operações de leitura e escrita sejam atômicas.
- semaforos_turno_dos_carros: Uma lista de semáforos que implementa um sistema de revezamento. Garante que apenas um carro por vez possa ocupar a estação de embarque. O carro que termina sua vez na estação é responsável por liberar (.release()) o semáforo do próximo carro na ordem.
- trilho_esta_livre: Um semáforo binário que representa o trilho do passeio. Um carro deve adquiri-lo (.acquire()) antes de partir e só o libera (.release()) após completar o passeio e o desembarque, garantindo exclusividade de uso do trilho.
- semaforo_passageiro_na_fila: Um semáforo contador. Cada passageiro que entra na fila o incrementa (.release()). O carro que está embarcando o decrementa (.acquire()) para cada passageiro que precisa, esperando até que a quantidade necessária de passageiros esteja disponível na fila.

Semáforos de "Handshake" (Embarque/Desembarque):
- semaforo_carro_pode_chamar_passageiro: Liberado pelo carro para "chamar" o próximo passageiro para embarcar.
- semaforo_passageiro_confirmou_embarque: Liberado pelo passageiro para sinalizar que ele completou sua ação de embarque.
- semaforo_carro_pode_liberar_passageiro: Liberado pelo carro para "autorizar" um passageiro a desembarcar.
- semaforo_passageiro_confirmou_desembarque: Liberado pelo passageiro para confirmar que desembarcou com sucesso.
