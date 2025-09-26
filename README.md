# Plataforma Geométrica II 🎮✨

Oi!  
Esse aqui é o meu projetinho de jogo feito em **Python com PgZero**.  
A ideia foi criar um jogo de plataforma simples, com inimigos, portais mágicos e até um chefão no final 👾.  

---

## 🎯 Como jogar
- **← / →** → andar  
- **↑** ou **Barra de espaço** → pular  
- **Tecla X** → atirar bolinhas de energia 🔥  

⚠️ Cuidado:  
- Se encostar em um inimigo sem atacar → **game over** 💀  
- Para derrotar inimigos:  
  - 🔴 **Vermelho (fraco):** 1 tiro ou pulo na cabeça  
  - ⚪ **Cinza (forte):** precisa de **3 tiros**  
  - 🟣 **Roxo (boss):** precisa de **5 tiros**  
- Portais dourados servem para passar de fase ✨  

---

## 🧩 Estrutura do código

### 1. **Configurações**
Variáveis principais do jogo: tamanho da tela, gravidade, velocidade do jogador, etc.  

### 2. **Níveis**
São 5 níveis no total:  
- **1 e 2** → fases introdutórias com inimigos simples.  
- **3 e 4** → fases médias, com mais plataformas e desafios.  
- **5** → fase final: luta contra o boss roxo.  

Cada nível define:  
- Posição inicial do jogador (`player_start`)  
- Plataformas (`platforms`)  
- Lista de inimigos (`enemies`)  
- Portal (`portal_pos`) – só aparece se não for o último nível.  

### 3. **Classes**
- **Player** → controla movimento, pulo e tiros.  
- **Enemy** → inimigos (fracos, fortes e boss).  
- **Projectile** → os tiros do jogador.  
- **Portal** → círculo mágico para avançar de fase.  

### 4. **Lógica do jogo**
- `setup_level()` → carrega a fase.  
- `update()` → roda a lógica a cada frame (movimento, colisões, mortes).  
- `draw()` → desenha os elementos na tela.  
- `on_key_down()` → controles do jogador.  
- `on_mouse_down()` → botões do menu inicial.  

---

## 🚀 Como rodar o jogo

1. Instale o **PgZero**:
    pip install pgzero

2. Salve o código em um arquivo, tipo jogo.py.

3. Rode com:
    pgzrun jogo.py

4. Divirta-se 💙
