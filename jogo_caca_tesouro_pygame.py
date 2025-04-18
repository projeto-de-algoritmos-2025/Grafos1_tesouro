#!/usr/bin/env python3
# Jogo de Caça ao Tesouro - Implementação com Grafos e interface Pygame
# Usando BFS e DFS para encontrar caminhos

import pygame
import sys
import random
import time
from collections import deque

# Inicializa pygame
pygame.init()

# Configurações da tela
LARGURA, ALTURA = 1400, 900
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Caça ao Tesouro - Versão Tabuleiro")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (200, 200, 200)
CINZA_ESCURO = (100, 100, 100)
AZUL = (0, 120, 255)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)
AMARELO = (255, 255, 0)
LARANJA = (255, 165, 0)
ROXO = (128, 0, 128)
MARROM = (139, 69, 19)
MARROM_CLARO = (210, 180, 140)
AZUL_ESCURO = (25, 25, 112)

# Configurações de fonte
pygame.font.init()
fonte_pequena = pygame.font.SysFont('Arial', 14)
fonte_media = pygame.font.SysFont('Arial', 18)
fonte_grande = pygame.font.SysFont('Arial', 26)
fonte_titulo = pygame.font.SysFont('Arial', 36, bold=True)

# Carrega imagens do jogo
def carregar_imagens():
    imagens = {}
    try:
        # Imagem de fundo
        imagens['fundo'] = pygame.Surface((LARGURA, ALTURA))
        imagens['fundo'].fill(MARROM_CLARO)  # Cor base para o fundo
        
        # Imagens para os locais - Círculos mais sofisticados por enquanto
        imagens['local_normal'] = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(imagens['local_normal'], CINZA, (30, 30), 25)
        pygame.draw.circle(imagens['local_normal'], PRETO, (30, 30), 25, 2)
        
        imagens['local_atual'] = pygame.Surface((70, 70), pygame.SRCALPHA)
        pygame.draw.circle(imagens['local_atual'], AZUL, (35, 35), 30)
        pygame.draw.circle(imagens['local_atual'], PRETO, (35, 35), 30, 2)
        
        imagens['local_tesouro'] = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(imagens['local_tesouro'], VERDE, (30, 30), 25)
        pygame.draw.circle(imagens['local_tesouro'], PRETO, (30, 30), 25, 2)
        
        imagens['local_armadilha'] = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(imagens['local_armadilha'], VERMELHO, (30, 30), 25)
        pygame.draw.circle(imagens['local_armadilha'], PRETO, (30, 30), 25, 2)
        
        imagens['local_visitado'] = pygame.Surface((70, 70), pygame.SRCALPHA)
        pygame.draw.circle(imagens['local_visitado'], (147, 112, 219), (35, 35), 30)
        pygame.draw.circle(imagens['local_visitado'], PRETO, (35, 35), 30, 2)
        
        imagens['local_fronteira'] = pygame.Surface((70, 70), pygame.SRCALPHA)
        pygame.draw.circle(imagens['local_fronteira'], (173, 216, 230), (35, 35), 30)
        pygame.draw.circle(imagens['local_fronteira'], PRETO, (35, 35), 30, 2)
        
        imagens['local_caminho'] = pygame.Surface((70, 70), pygame.SRCALPHA)
        pygame.draw.circle(imagens['local_caminho'], AMARELO, (35, 35), 30)
        pygame.draw.circle(imagens['local_caminho'], PRETO, (35, 35), 30, 2)
        
        imagens['local_explorando'] = pygame.Surface((70, 70), pygame.SRCALPHA)
        pygame.draw.circle(imagens['local_explorando'], (255, 140, 0), (35, 35), 30)
        pygame.draw.circle(imagens['local_explorando'], PRETO, (35, 35), 30, 2)
        
        # Desenha textura no fundo
        for i in range(0, LARGURA, 40):
            for j in range(0, ALTURA, 40):
                if (i // 40 + j // 40) % 2 == 0:
                    pygame.draw.rect(imagens['fundo'], (190, 160, 120), (i, j, 40, 40))
        
        # Adiciona bordas ao tabuleiro
        pygame.draw.rect(imagens['fundo'], MARROM, (0, 0, LARGURA, ALTURA), 20)
        
        return imagens
    except Exception as e:
        print(f"Erro ao carregar imagens: {e}")
        return {}

# Imagens do jogo
IMAGENS = carregar_imagens()

class NoGrafo:
    def __init__(self, id, nome, pos_x, pos_y):
        self.id = id
        self.nome = nome
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.eh_tesouro = False
        self.eh_armadilha = False
        self.cor = CINZA
        self.raio = 25
        self.descricao = "Um lugar comum no mapa."
    
    def definir_tesouro(self):
        self.eh_tesouro = True
        self.cor = VERDE
        self.descricao = "Este lugar contém o tesouro!"
    
    def definir_armadilha(self):
        self.eh_armadilha = True
        self.cor = VERMELHO
        self.descricao = "Cuidado! Este lugar contém uma armadilha!"
    
    def desenhar(self, tela, atual=False, caminho=False):
        # Escolhe a imagem correta baseado no estado
        if atual:
            img = IMAGENS['local_atual']
            pos_x = self.pos_x - 35
            pos_y = self.pos_y - 35
        elif self.eh_tesouro:
            img = IMAGENS['local_tesouro']
            pos_x = self.pos_x - 30
            pos_y = self.pos_y - 30
        elif self.eh_armadilha:
            img = IMAGENS['local_armadilha']
            pos_x = self.pos_x - 30
            pos_y = self.pos_y - 30
        elif caminho:
            img = IMAGENS['local_caminho']
            pos_x = self.pos_x - 35
            pos_y = self.pos_y - 35
        else:
            img = IMAGENS['local_normal']
            pos_x = self.pos_x - 30
            pos_y = self.pos_y - 30
        
        # Desenha a imagem
        tela.blit(img, (pos_x, pos_y))
        
        # Desenha o número do local
        texto = fonte_media.render(str(self.id), True, PRETO)
        tela.blit(texto, (self.pos_x - texto.get_width()//2, self.pos_y - texto.get_height()//2))
    
    def contem_ponto(self, pos):
        return ((pos[0] - self.pos_x) ** 2 + (pos[1] - self.pos_y) ** 2) <= self.raio ** 2
    
    def __str__(self):
        return self.nome

class Grafo:
    def __init__(self):
        self.nos = {}
        self.arestas = {}
    
    def adicionar_no(self, no):
        self.nos[no.id] = no
        self.arestas[no.id] = []
    
    def adicionar_aresta(self, no1_id, no2_id):
        if no1_id in self.arestas and no2_id in self.nos:
            if no2_id not in self.arestas[no1_id]:
                self.arestas[no1_id].append(no2_id)
                # Grafo não direcionado
                if no2_id in self.arestas and no1_id not in self.arestas[no2_id]:
                    self.arestas[no2_id].append(no1_id)
    
    def desenhar(self, tela, no_atual=None, caminho=None, visitados=None, fronteira=None, caminho_atual=None, armadilhas_evitadas=None):
        # Desenha o fundo do tabuleiro
        tela.blit(IMAGENS['fundo'], (0, 0))
        
        # Desenha as arestas primeiro (caminhos do tabuleiro)
        for no_id, vizinhos in self.arestas.items():
            no = self.nos[no_id]
            for vizinho_id in vizinhos:
                if vizinho_id > no_id:  # Evita desenhar a mesma aresta duas vezes
                    vizinho = self.nos[vizinho_id]
                    
                    # Definir cor da aresta com base em diferentes condições
                    cor_aresta = MARROM
                    espessura = 6
                    
                    # Aresta em caminho sendo explorado atualmente
                    if caminho_atual and no_id in caminho_atual and vizinho_id in caminho_atual and abs(caminho_atual.index(no_id) - caminho_atual.index(vizinho_id)) == 1:
                        cor_aresta = (255, 140, 0)  # Laranja para caminho atual
                        espessura = 10
                    # Aresta no caminho final
                    elif caminho and no_id in caminho and vizinho_id in caminho and abs(caminho.index(no_id) - caminho.index(vizinho_id)) == 1:
                        cor_aresta = AMARELO
                        espessura = 8
                    
                    # Desenha caminho mais elaborado - linha pontilhada com marcas
                    if espessura > 6:  # Se for um caminho destacado
                        # Linha principal
                        pygame.draw.line(tela, cor_aresta, (no.pos_x, no.pos_y), 
                                        (vizinho.pos_x, vizinho.pos_y), espessura)
                    else:
                        # Linha pontilhada para caminhos normais
                        dx = vizinho.pos_x - no.pos_x
                        dy = vizinho.pos_y - no.pos_y
                        dist = (dx**2 + dy**2)**0.5
                        
                        if dist > 0:
                            dx, dy = dx / dist, dy / dist
                            
                            # Número de pontos na linha pontilhada
                            num_pontos = int(dist / 20)
                            
                            for i in range(num_pontos):
                                p = i / (num_pontos - 1)
                                x = no.pos_x + dx * dist * p
                                y = no.pos_y + dy * dist * p
                                pygame.draw.circle(tela, cor_aresta, (int(x), int(y)), 3)
        
        # Desenha os nós por cima
        for no_id, no in self.nos.items():
            # Define estados diferentes para visualização
            eh_atual = no_atual == no_id
            eh_caminho = caminho and no_id in caminho
            eh_visitado = visitados and no_id in visitados
            eh_fronteira = fronteira and no_id in fronteira
            eh_caminho_atual = caminho_atual and no_id in caminho_atual
            eh_armadilha_evitada = armadilhas_evitadas and no_id in armadilhas_evitadas
            
            # Desenha círculos extras para visualização dos estados
            if eh_fronteira and not eh_visitado:
                tela.blit(IMAGENS['local_fronteira'], (no.pos_x - 35, no.pos_y - 35))
            
            if eh_visitado:
                tela.blit(IMAGENS['local_visitado'], (no.pos_x - 35, no.pos_y - 35))
            
            if eh_caminho_atual:
                tela.blit(IMAGENS['local_explorando'], (no.pos_x - 35, no.pos_y - 35))
            
            # Desenha um X para armadilhas evitadas
            if eh_armadilha_evitada:
                pygame.draw.circle(tela, (255, 192, 203), (no.pos_x, no.pos_y), no.raio + 12)  # Rosa claro para armadilhas evitadas
                espessura = 3
                pygame.draw.line(tela, (139, 0, 0), 
                                (no.pos_x - no.raio - 5, no.pos_y - no.raio - 5),
                                (no.pos_x + no.raio + 5, no.pos_y + no.raio + 5), 
                                espessura)
                pygame.draw.line(tela, (139, 0, 0), 
                                (no.pos_x - no.raio - 5, no.pos_y + no.raio + 5),
                                (no.pos_x + no.raio + 5, no.pos_y - no.raio - 5), 
                                espessura)
            
            # Desenha o nó normalmente
            no.desenhar(tela, eh_atual, eh_caminho)
    
    def busca_bfs(self, inicio_id, destino_id):
        if inicio_id not in self.nos or destino_id not in self.nos:
            return None, [], [], [], []
        
        # Para visualização, retornamos histórico da busca
        historico_busca = []
        
        visitados = set()
        fronteira = set([inicio_id])
        fila = deque([(inicio_id, [inicio_id])])
        armadilhas_evitadas = set()
        
        # Registra o estado inicial para visualização
        historico_busca.append({
            'visitados': set(),
            'fronteira': set([inicio_id]),
            'caminho_atual': [inicio_id],
            'armadilhas_evitadas': set()
        })
        
        while fila:
            atual, caminho = fila.popleft()
            fronteira.discard(atual)  # Remove da fronteira mesmo se não existir
            
            if atual == destino_id:
                # Inclui o estado final no histórico
                historico_busca.append({
                    'visitados': visitados.copy(),
                    'fronteira': fronteira.copy(),
                    'caminho_atual': caminho,
                    'armadilhas_evitadas': armadilhas_evitadas.copy()
                })
                return caminho, historico_busca, visitados, fronteira, armadilhas_evitadas
            
            if atual not in visitados:
                visitados.add(atual)
                
                for vizinho in self.arestas[atual]:
                    # Registra armadilhas evitadas para visualização
                    if self.nos[vizinho].eh_armadilha:
                        armadilhas_evitadas.add(vizinho)
                        continue
                        
                    # Verifica se o vizinho é uma armadilha antes de adicioná-lo à fronteira
                    if vizinho not in visitados and vizinho not in fronteira:
                        novo_caminho = caminho.copy()
                        novo_caminho.append(vizinho)
                        fronteira.add(vizinho)
                        fila.append((vizinho, novo_caminho))
                        
                        # Registra o estado para visualização
                        historico_busca.append({
                            'visitados': visitados.copy(),
                            'fronteira': fronteira.copy(),
                            'caminho_atual': novo_caminho,
                            'armadilhas_evitadas': armadilhas_evitadas.copy()
                        })
        
        return None, historico_busca, visitados, fronteira, armadilhas_evitadas
    
    def busca_dfs(self, inicio_id, destino_id):
        if inicio_id not in self.nos or destino_id not in self.nos:
            return None, [], [], [], []
        
        # Para visualização, retornamos histórico da busca
        historico_busca = []
        
        visitados = set()
        fronteira = set([inicio_id])
        pilha = [(inicio_id, [inicio_id])]
        armadilhas_evitadas = set()
        
        # Registra o estado inicial para visualização
        historico_busca.append({
            'visitados': set(),
            'fronteira': set([inicio_id]),
            'caminho_atual': [inicio_id],
            'armadilhas_evitadas': set()
        })
        
        while pilha:
            atual, caminho = pilha.pop()
            fronteira.discard(atual)  # Remove da fronteira
            
            if atual == destino_id:
                # Inclui o estado final no histórico
                historico_busca.append({
                    'visitados': visitados.copy(),
                    'fronteira': fronteira.copy(),
                    'caminho_atual': caminho,
                    'armadilhas_evitadas': armadilhas_evitadas.copy()
                })
                return caminho, historico_busca, visitados, fronteira, armadilhas_evitadas
            
            if atual not in visitados:
                visitados.add(atual)
                
                # Em DFS, processa os vizinhos em ordem inversa para manter comportamento visual tradicional
                vizinhos = list(self.arestas[atual])
                vizinhos.reverse()
                
                for vizinho in vizinhos:
                    # Registra armadilhas evitadas para visualização
                    if self.nos[vizinho].eh_armadilha:
                        armadilhas_evitadas.add(vizinho)
                        continue
                    
                    # Verifica se o vizinho é válido para exploração
                    if vizinho not in visitados:
                        novo_caminho = caminho.copy()
                        novo_caminho.append(vizinho)
                        fronteira.add(vizinho)
                        pilha.append((vizinho, novo_caminho))
                        
                        # Registra o estado para visualização
                        historico_busca.append({
                            'visitados': visitados.copy(),
                            'fronteira': fronteira.copy(),
                            'caminho_atual': novo_caminho,
                            'armadilhas_evitadas': armadilhas_evitadas.copy()
                        })
        
        return None, historico_busca, visitados, fronteira, armadilhas_evitadas

def criar_mapa():
    grafo = Grafo()
    
    # Posições dos nós ajustadas para o tabuleiro maior
    posicoes = {
        1: (200, 130),    # Entrada da Caverna
        2: (400, 190),    # Salão Principal
        3: (200, 300),    # Corredor Escuro
        4: (600, 130),    # Câmara Misteriosa
        5: (400, 350),    # Ponto de Bifurcação
        6: (200, 500),    # Passagem Estreita
        7: (900, 130),    # Sala dos Cristais
        8: (600, 350),    # Túnel Úmido
        9: (400, 500),    # Abismo Profundo
        10: (200, 730),   # Sala do Tesouro
        11: (800, 250),   # Câmara Secreta
        12: (900, 350),   # Gruta Profunda
        13: (600, 550),   # Salão dos Espelhos
        14: (400, 650),   # Rio Subterrâneo
        15: (750, 650),   # Altar Antigo
    }
    
    # Criando os nós
    locais = [
        (1, "Entrada da Caverna"),
        (2, "Salão Principal"),
        (3, "Corredor Escuro"),
        (4, "Câmara Misteriosa"),
        (5, "Ponto de Bifurcação"),
        (6, "Passagem Estreita"),
        (7, "Sala dos Cristais"),
        (8, "Túnel Úmido"),
        (9, "Abismo Profundo"),
        (10, "Sala do Tesouro"),
        (11, "Câmara Secreta"),
        (12, "Gruta Profunda"),
        (13, "Salão dos Espelhos"),
        (14, "Rio Subterrâneo"),
        (15, "Altar Antigo")
    ]
    
    for id, nome in locais:
        pos_x, pos_y = posicoes[id]
        grafo.adicionar_no(NoGrafo(id, nome, pos_x, pos_y))
    
    # Adicionando arestas (caminhos entre locais)
    conexoes = [
        (1, 2), (1, 3),
        (2, 4), (2, 5),
        (3, 5), (3, 6),
        (4, 7), (4, 8),
        (5, 8), (5, 9),
        (6, 9), (6, 10),
        (7, 11), (7, 12),
        (8, 12), (8, 13),
        (9, 13), (9, 14),
        (10, 14), (10, 15),
        (11, 15), (12, 13),
        (13, 14), (14, 15)
    ]
    
    for no1, no2 in conexoes:
        grafo.adicionar_aresta(no1, no2)
    
    # Definindo o tesouro
    grafo.nos[15].definir_tesouro()  # Altar Antigo
    
    # Definindo armadilhas
    armadilhas = [4, 10, 13]  # Câmara Misteriosa, Abismo Profundo, Gruta Profunda
    for arm_id in armadilhas:
        grafo.nos[arm_id].definir_armadilha()
    
    return grafo

class Botao:
    def __init__(self, x, y, largura, altura, texto, cor=CINZA, cor_hover=CINZA_ESCURO, cor_texto=PRETO):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.cor = cor
        self.cor_original = cor
        self.cor_hover = cor_hover
        self.cor_texto = cor_texto
        self.ativo = True
    
    def desenhar(self, tela):
        if not self.ativo:
            # Desenha botão desativado
            pygame.draw.rect(tela, CINZA_ESCURO, self.rect)
            pygame.draw.rect(tela, PRETO, self.rect, 2)
            texto_superficie = fonte_media.render(self.texto, True, (150, 150, 150))
        else:
            # Verifica se o mouse está sobre o botão
            pos_mouse = pygame.mouse.get_pos()
            if self.rect.collidepoint(pos_mouse):
                pygame.draw.rect(tela, self.cor_hover, self.rect)
            else:
                pygame.draw.rect(tela, self.cor, self.rect)
            
            # Borda do botão
            pygame.draw.rect(tela, PRETO, self.rect, 2)
            
            # Texto do botão
            texto_superficie = fonte_media.render(self.texto, True, self.cor_texto)
        
        # Centraliza o texto no botão
        texto_rect = texto_superficie.get_rect(center=self.rect.center)
        tela.blit(texto_superficie, texto_rect)
    
    def clicado(self, pos):
        return self.ativo and self.rect.collidepoint(pos)

class Jogo:
    def __init__(self):
        self.grafo = criar_mapa()
        self.no_atual_id = 1  # Começa na Entrada da Caverna
        self.no_tesouro_id = 15  # Altar Antigo
        self.caminho_atual = None
        self.historico_movimentos = [1]  # Começa na entrada
        self.estado = "JOGANDO"  # JOGANDO, VITORIA, DERROTA, ANIMANDO_BFS, ANIMANDO_DFS
        self.mensagem = "Bem-vindo à caça ao tesouro! Encontre o tesouro e evite as armadilhas."
        
        # Área de informações (painel direito)
        self.painel_info = pygame.Rect(1050, 0, 350, ALTURA)
        
        # Botões - Ajuste para o novo tamanho de tela
        self.botoes = {
            "mover": Botao(1070, 390, 310, 50, "Mover para o Local Selecionado", CINZA),
            "bfs": Botao(1070, 450, 310, 50, "Encontrar caminho (BFS)", AZUL),
            "dfs": Botao(1070, 510, 310, 50, "Explorar caminho (DFS)", ROXO),
            "seguir": Botao(1070, 570, 310, 50, "Seguir Caminho Automaticamente", VERDE),
            "reiniciar": Botao(1070, 840, 310, 50, "Reiniciar Jogo", LARANJA)
        }
        
        # Desativa o botão de seguir caminho inicialmente
        self.botoes["seguir"].ativo = False
        
        self.no_selecionado = None
        self.algoritmo_usado = None
        
        # Variáveis para animação 
        self.historico_busca = []
        self.indice_historico = 0
        self.visitados = set()
        self.fronteira = set()
        self.caminho_atual_bfs = None
        self.armadilhas_evitadas = set()
        self.tempo_ultimo_passo = 0
        self.intervalo_animacao = 700  # milissegundos (aumentado para melhor visualização)
    
    def reiniciar(self):
        self.grafo = criar_mapa()
        self.no_atual_id = 1
        self.caminho_atual = None
        self.historico_movimentos = [1]
        self.estado = "JOGANDO"
        self.mensagem = "Jogo reiniciado! Boa sorte!"
        self.no_selecionado = None
        self.algoritmo_usado = None
        self.botoes["seguir"].ativo = False
        
        # Limpa variáveis de animação
        self.historico_busca = []
        self.indice_historico = 0
        self.visitados = set()
        self.fronteira = set()
        self.caminho_atual_bfs = None
        self.armadilhas_evitadas = set()
    
    def mover_para(self, no_id):
        if no_id in self.grafo.arestas[self.no_atual_id]:
            self.no_atual_id = no_id
            self.historico_movimentos.append(no_id)
            
            # Verifica se caiu em armadilha
            if self.grafo.nos[no_id].eh_armadilha:
                self.estado = "DERROTA"
                self.mensagem = f"Oh não! Você caiu em uma armadilha na {self.grafo.nos[no_id].nome}!"
            
            # Verifica se encontrou o tesouro
            elif self.grafo.nos[no_id].eh_tesouro:
                self.estado = "VITORIA"
                self.mensagem = f"Parabéns! Você encontrou o tesouro na {self.grafo.nos[no_id].nome}!"
            
            else:
                self.mensagem = f"Você se moveu para {self.grafo.nos[no_id].nome}."
            
            return True
        return False
    
    def calcular_caminho(self, algoritmo):
        if algoritmo == "BFS":
            self.estado = "ANIMANDO_BFS"
            self.caminho_atual, self.historico_busca, self.visitados, self.fronteira, self.armadilhas_evitadas = self.grafo.busca_bfs(self.no_atual_id, self.no_tesouro_id)
            self.algoritmo_usado = "BFS"
            self.indice_historico = 0
            self.mensagem = "Iniciando busca com BFS. Observe a exploração dos caminhos..."
            self.tempo_ultimo_passo = pygame.time.get_ticks()
        else:  # DFS
            self.estado = "ANIMANDO_DFS"
            self.caminho_atual, self.historico_busca, self.visitados, self.fronteira, self.armadilhas_evitadas = self.grafo.busca_dfs(self.no_atual_id, self.no_tesouro_id)
            self.algoritmo_usado = "DFS"
            self.indice_historico = 0
            self.mensagem = "Iniciando busca com DFS. Observe a exploração dos caminhos..."
            self.tempo_ultimo_passo = pygame.time.get_ticks()
        
        if self.caminho_atual:
            self.botoes["seguir"].ativo = True
        else:
            self.mensagem = "Não foi possível encontrar um caminho até o tesouro!"

    def atualizar_animacao_bfs(self):
        tempo_atual = pygame.time.get_ticks()
        
        # Se passou o intervalo de tempo para o próximo passo
        if tempo_atual - self.tempo_ultimo_passo >= self.intervalo_animacao:
            self.tempo_ultimo_passo = tempo_atual
            
            # Se ainda há passos na animação
            if self.indice_historico < len(self.historico_busca):
                passo = self.historico_busca[self.indice_historico]
                self.visitados = passo['visitados']
                self.fronteira = passo['fronteira']
                self.caminho_atual_bfs = passo['caminho_atual']
                self.armadilhas_evitadas = passo.get('armadilhas_evitadas', set())
                
                if len(self.caminho_atual_bfs) > 1:
                    ultimo_no = self.caminho_atual_bfs[-1]
                    penultimo_no = self.caminho_atual_bfs[-2]
                    self.mensagem = f"Explorando de {self.grafo.nos[penultimo_no].nome} para {self.grafo.nos[ultimo_no].nome}..."
                else:
                    self.mensagem = "Iniciando busca do caminho..."
                
                self.indice_historico += 1
            else:
                # Animação concluída
                self.estado = "JOGANDO"
                if self.caminho_atual:
                    self.mensagem = f"Caminho encontrado com BFS! {len(self.visitados)} nós visitados, {len(self.armadilhas_evitadas)} armadilhas evitadas, melhor caminho tem {len(self.caminho_atual)} nós."
                else:
                    self.mensagem = "Não foi possível encontrar um caminho até o tesouro!"
                self.caminho_atual_bfs = None

    def atualizar_animacao_dfs(self):
        tempo_atual = pygame.time.get_ticks()
        
        # Se passou o intervalo de tempo para o próximo passo
        if tempo_atual - self.tempo_ultimo_passo >= self.intervalo_animacao:
            self.tempo_ultimo_passo = tempo_atual
            
            # Se ainda há passos na animação
            if self.indice_historico < len(self.historico_busca):
                passo = self.historico_busca[self.indice_historico]
                self.visitados = passo['visitados']
                self.fronteira = passo['fronteira']
                self.caminho_atual_bfs = passo['caminho_atual']
                self.armadilhas_evitadas = passo.get('armadilhas_evitadas', set())
                
                if len(self.caminho_atual_bfs) > 1:
                    ultimo_no = self.caminho_atual_bfs[-1]
                    penultimo_no = self.caminho_atual_bfs[-2]
                    self.mensagem = f"Explorando em profundidade de {self.grafo.nos[penultimo_no].nome} para {self.grafo.nos[ultimo_no].nome}..."
                else:
                    self.mensagem = "Iniciando busca em profundidade..."
                
                self.indice_historico += 1
            else:
                # Animação concluída
                self.estado = "JOGANDO"
                if self.caminho_atual:
                    self.mensagem = f"Caminho encontrado com DFS! {len(self.visitados)} nós visitados, {len(self.armadilhas_evitadas)} armadilhas evitadas, caminho tem {len(self.caminho_atual)} nós."
                else:
                    self.mensagem = "Não foi possível encontrar um caminho até o tesouro!"
                self.caminho_atual_bfs = None
    
    def seguir_caminho(self):
        if not self.caminho_atual or len(self.caminho_atual) <= 1:
            self.mensagem = "Não há caminho para seguir!"
            return
        
        # Inicia a partir do segundo nó no caminho (o primeiro é onde já estamos)
        indice_atual = self.caminho_atual.index(self.no_atual_id)
        
        if indice_atual + 1 < len(self.caminho_atual):
            proximo_no = self.caminho_atual[indice_atual + 1]
            self.mover_para(proximo_no)
        else:
            self.mensagem = "Você já está no fim do caminho!"
            self.botoes["seguir"].ativo = False
        
        # Se o jogo acabou, desativa o botão de seguir
        if self.estado != "JOGANDO":
            self.botoes["seguir"].ativo = False
    
    def desenhar(self, tela):
        # Limpa a tela
        tela.fill(AZUL_ESCURO)
        
        # Desenha o grafo (tabuleiro)
        if self.estado == "ANIMANDO_BFS" or self.estado == "ANIMANDO_DFS":
            self.grafo.desenhar(tela, self.no_atual_id, self.caminho_atual, 
                               self.visitados, self.fronteira, self.caminho_atual_bfs,
                               self.armadilhas_evitadas)
        else:
            self.grafo.desenhar(tela, self.no_atual_id, self.caminho_atual)
        
        # Desenha a área de informações
        pygame.draw.rect(tela, CINZA, self.painel_info)
        pygame.draw.line(tela, PRETO, (1050, 0), (1050, ALTURA), 3)
        
        # Desenha o título no painel
        titulo = fonte_titulo.render("Caça ao Tesouro", True, PRETO)
        tela.blit(titulo, (self.painel_info.centerx - titulo.get_width()//2, 20))
        
        # Desenha a legenda
        pygame.draw.rect(tela, BRANCO, (1070, 80, 310, 230))
        pygame.draw.rect(tela, PRETO, (1070, 80, 310, 230), 2)
        
        legenda_titulo = fonte_grande.render("Legenda:", True, PRETO)
        tela.blit(legenda_titulo, (1080, 90))
        
        # Itens da legenda
        legenda_items = [
            (AZUL, "Posição Atual"),
            (VERDE, "Tesouro"),
            (VERMELHO, "Armadilha"),
            (AMARELO, "Caminho Final"),
            ((255, 140, 0), "Explorando agora"),
            ((173, 216, 230), "Fronteira"),
            ((147, 112, 219), "Visitado"),
            ((255, 192, 203), "Armadilha Evitada"),
            (CINZA, "Local Normal")
        ]
        
        for i, (cor, texto) in enumerate(legenda_items):
            y = 120 + i * 22
            pygame.draw.circle(tela, cor, (1085, y), 8)
            pygame.draw.circle(tela, PRETO, (1085, y), 8, 1)
            texto_leg = fonte_media.render(texto, True, PRETO)
            tela.blit(texto_leg, (1100, y - 8))
        
        # Desenha informações do local atual
        info_y = 340
        local_titulo = fonte_grande.render("Local Atual:", True, PRETO)
        tela.blit(local_titulo, (1070, info_y))
        
        no_atual = self.grafo.nos[self.no_atual_id]
        nome_local = fonte_media.render(f"{no_atual.nome}", True, PRETO)
        tela.blit(nome_local, (1070, info_y + 30))
        
        # Desenhar a descrição do local em multi-linhas
        desc_y = info_y + 50
        self.renderizar_texto_multilinhas(tela, no_atual.descricao, 1070, desc_y, 310)
        
        # Desenha botões
        for botao in self.botoes.values():
            botao.desenhar(tela)
        
        # Desenha a mensagem
        mensagem_surf = pygame.Surface((1030, 90))
        mensagem_surf.fill(BRANCO)
        pygame.draw.rect(mensagem_surf, PRETO, (0, 0, 1030, 90), 2)
        self.renderizar_texto_multilinhas(mensagem_surf, self.mensagem, 10, 10, 1010)
        tela.blit(mensagem_surf, (10, 800))
        
        # Se o jogo acabou, mostra uma mensagem especial
        if self.estado not in ["JOGANDO", "ANIMANDO_BFS", "ANIMANDO_DFS"]:
            cor_overlay = VERDE if self.estado == "VITORIA" else VERMELHO
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((cor_overlay[0], cor_overlay[1], cor_overlay[2], 100))
            tela.blit(overlay, (0, 0))
            
            status_texto = "VITÓRIA!" if self.estado == "VITORIA" else "DERROTA!"
            status_surf = fonte_titulo.render(status_texto, True, PRETO)
            tela.blit(status_surf, (525 - status_surf.get_width()//2, 400))
    
    def renderizar_texto_multilinhas(self, superficie, texto, x, y, largura_max, cor=PRETO):
        palavras = texto.split()
        linhas = []
        linha_atual = []
        
        for palavra in palavras:
            teste_linha = ' '.join(linha_atual + [palavra])
            largura_texto = fonte_pequena.size(teste_linha)[0]
            
            if largura_texto > largura_max:
                linhas.append(' '.join(linha_atual))
                linha_atual = [palavra]
            else:
                linha_atual.append(palavra)
        
        if linha_atual:
            linhas.append(' '.join(linha_atual))
        
        for i, linha in enumerate(linhas):
            texto_surf = fonte_pequena.render(linha, True, cor)
            superficie.blit(texto_surf, (x, y + i * 20))
    
    def processar_evento(self, evento):
        if evento.type == pygame.QUIT:
            return False
        
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = pygame.mouse.get_pos()
            
            # Se estiver animando, ignora cliques (exceto no botão de reiniciar)
            if (self.estado == "ANIMANDO_BFS" or self.estado == "ANIMANDO_DFS") and not self.botoes["reiniciar"].clicado(pos):
                return True
            
            # Verifica cliques nos botões
            if self.botoes["mover"].clicado(pos):
                if self.no_selecionado and self.no_selecionado in self.grafo.arestas[self.no_atual_id]:
                    self.mover_para(self.no_selecionado)
                    self.no_selecionado = None
                else:
                    self.mensagem = "Selecione um local conectado para se mover!"
            
            elif self.botoes["bfs"].clicado(pos) and self.estado == "JOGANDO":
                self.calcular_caminho("BFS")
            
            elif self.botoes["dfs"].clicado(pos) and self.estado == "JOGANDO":
                self.calcular_caminho("DFS")
            
            elif self.botoes["seguir"].clicado(pos) and self.estado == "JOGANDO":
                self.seguir_caminho()
            
            elif self.botoes["reiniciar"].clicado(pos):
                self.reiniciar()
            
            # Verifica cliques nos nós do grafo
            else:
                for no_id, no in self.grafo.nos.items():
                    if no.contem_ponto(pos):
                        self.no_selecionado = no_id
                        self.mensagem = f"Selecionado: {no.nome}"
                        break
        
        return True

def main():
    jogo = Jogo()
    clock = pygame.time.Clock()
    executando = True
    
    while executando:
        for evento in pygame.event.get():
            executando = jogo.processar_evento(evento)
        
        # Atualiza a animação se necessário
        if jogo.estado == "ANIMANDO_BFS":
            jogo.atualizar_animacao_bfs()
        elif jogo.estado == "ANIMANDO_DFS":
            jogo.atualizar_animacao_dfs()
        
        jogo.desenhar(tela)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 