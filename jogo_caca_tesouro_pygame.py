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