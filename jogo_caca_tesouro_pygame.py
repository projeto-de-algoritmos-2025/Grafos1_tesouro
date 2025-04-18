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