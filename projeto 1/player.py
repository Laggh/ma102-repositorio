### TODO: PREENCHA SUAS INFORMAÇÕES AQUI ###
# Nome #01 (quem entregou o código):    [NOME COMPLETO #01] 
# RA #01 (quem entregou o código):      [RA #01]
# Nome #02:                             [NOME COMPLETO #02]
# RA #02:                               [RA #02]

"""Implemente aqui o seu código para adivinhar a regra.

Seu principal objetivo é implementar a função `player`, que deve retornar sua ação na rodada (chute de número ou chute de regra) e seu chute.
1. Se for um chute de número, ele deve ser um inteiro entre 1 e 100.000.
2. Se for um chute de regra, ele deve ser uma lista do tipo [TIPO, P1, P2], onde:
    - TIPO é uma string que pode ser "mod", "pot" ou "int", indicando o tipo da regra;
    - P1 e P2 são os parâmetros (números inteiros) da regra, que dependem do tipo.
        - Se TIPO for "mod", P1 é o valor de k e P2 é o valor de r.
        - Se TIPO for "pot", P1 é o valor de p. P2 é ignorado e pode ser qualquer valor.
        - Se TIPO for "int", P1 é o valor de a e P2 é o valor de b.

Exemplos de retornos válidos da função `player`:
- ["NUMBER", 42]             Chutando o número 42
- ["NUMBER", 100000]         Chutando o número 100.000
- ["RULE", ["mod", 3, 1]]    Chutando a regra "n mod 3 dá resto 1"
- ["RULE", ["pot", 2, 999]]  Chutando a regra "n é potência perfeita de ordem 2"
- ["RULE", ["int", 10, 20]]  Chutando a regra "n pertence ao intervalo [10, 20]"

Caso sua função não tenha um retorno adequado, a automatização não irá ocorrer tanto em game.py quanto em tournament.py.

---

A função `player` recebe duas listas como argumentos:
- number_guesses: lista de respostas aos chutes de número anteriores, onde cada elemento é uma lista do tipo [chute, direção, acerto], sendo:
    - chute:            o número inteiro chutado
    - direção:          a direção que indica se um número mais próximo que satisfaz a regra é maior ou menor do que o chute,
        sendo "igual" se o chute satisfizer a regra e menor se o chute estiver exatamente entre dois números que satisfazem a regra
    - acerto:           booleano indicando se o chute satisfaz a regra ou não

- rule_guesses: lista de respostas aos chutes de regras anteriores, onde cada elemento é uma lista do tipo [TIPO, P1, P2], 
    que significam a mesma coisa que os elementos do chute de regra descritos mais acima

Você pode implementar outras funções para auxiliar a função `player` e salvar informações entre os chutes usando variáveis globais (fora de qualquer função).

Para mais informações, verifique o README.md ou consulte um monitor.
"""

import time
import random

def mod_algorithm(number_guesses, rule_guesses):
    # Implementação do algoritmo para chutar regras do tipo "mod"
    # temporario:
    print("Tentando MOD")
    return ["RULE", ["mod", 3, 1]]

def pot_algorithm(number_guesses, rule_guesses):
    # Implementação do algoritmo para chutar regras do tipo "pot"
    # temporario:
    print("Tentando POT")
    return ["RULE", ["pot", 2, 0]]


# 1 hora e meia pra fazer isso
def int_algorithm(number_guesses, rule_guesses):
    pensamento = []
    number_hash = {}
    for ng in number_guesses:
        chute, direcao, acerto = ng
        number_hash[chute] = direcao #acerto nn precisa
        # pq se o chute for correto, a direção é "igual"
    
    menor = 1
    maior = 100_000
    corretos = []
    for ng in number_guesses:
        chute, direcao, acerto = ng
        if direcao == "maior" and not acerto:
            
            menor = max(menor, chute)
            pensamento.append(f"chute {chute} é menor que o número que satisfaz a regra, novo intervalo: {menor}-{maior}")
        elif direcao == "menor" and not acerto:
            
            maior = min(maior, chute)
            pensamento.append(f"chute {chute} é maior que o número que satisfaz a regra, novo intervalo: {menor}-{maior}")
        
        if acerto:
            corretos.append(chute)
            pensamento.append(f"chute {chute} é igual ao número que satisfaz a regra, novo intervalo: {menor}-{maior}")

    print(f"mn {menor}-{maior}")
    

    if len(corretos) == 0:
        to_test = (menor + maior) // 2
        return ["NUMBER", to_test]
    
    menor_c = None
    maior_c = None
    for i in corretos:
        if menor_c == None or maior_c == None:
            pensamento.append(f"primeiro correto encontrado: {i}")
            menor_c = i
            maior_c = i
            continue

        if i < menor_c:
            menor_c = i
            pensamento.append(f"{i} é menor que {menor_c}(menor_c), atualizando menor_c")
        if i > maior_c:
            maior_c = i
            pensamento.append(f"{i} é maior que {maior_c}(maior_c), atualizando maior_c")
    
    # testando se os valores fazem sentido:
    if menor_c == None or maior_c == None:
        raise Exception("ERRO, CORRETOS VAZIO, MAS AINDA ASSIM CHEGOU AQUI")
    
    if menor_c < menor or maior_c > maior:
        pensamento.append(f"menor_c {menor_c} ou maior_c {maior_c} estão fora do intervalo de pensamento, que é {menor}-{maior}")
        for i in pensamento:
            print(i)
        for i in corretos:
            print(f"correto {i}")
        raise Exception("ERRO, CORRETOS FORA DO INTERVALO, MAS AINDA ASSIM CHEGOU AQUI")
    
    # Testamos se a parte de cima ta certinha
    cima_ok = False
    cima_teste = number_hash.get(maior_c+1, None)
    if cima_teste == "menor":
        cima_ok = True
    
    if cima_teste == None:
        to_test = (maior_c + maior)// 2
        if to_test == maior_c:
            to_test += 1 #evita ficar travado testando o mesmo numero
        return ["NUMBER", to_test]
    
    if cima_teste == "maior":
        # isso é um erro, pq se maior_c é o maior numero que satisfaz a regra, o numero imediatamente acima dele nn pode satisfazer a regra
        raise Exception("ERRO, MAIOR_C+1 MAIOR, MAS MAIOR_C É O MAIOR QUE SATISFAZ A REGRA, MAS AINDA ASSIM CHEGOU AQUI")   
    
    # Testamos se a parte de baixo ta certinha
    baixo_ok = False
    baixo_teste = number_hash.get(menor_c-1, None)
    if baixo_teste == "maior":
        baixo_ok = True

    if baixo_teste == None:
        to_test = (menor_c + menor) // 2
        if to_test == menor_c:
            to_test -= 1 #evita ficar travado testando o mesmo numero
        return ["NUMBER", to_test]

    if baixo_teste == "menor":
        # isso é um erro, pq se menor_c é o menor numero que satisfaz a regra, o numero imediatamente abaixo dele nn pode satisfazer a regra
        raise Exception("ERRO, MENOR_C-1 MENOR, MAS MENOR_C É O MENOR QUE SATISFAZ A REGRA, MAS AINDA ASSIM CHEGOU AQUI")
    
    # Se chegou aqui, é pq tanto a parte de cima quanto a parte de baixo estão certinhas, então o intervalo entre menor_c e maior_c é o intervalo correto
    return ["RULE", ["int", menor_c, maior_c]]


        
    
        


    

    


    
## estrategia: um ser humano, vou botar print e input para ler o chute do jogador, e retornar o chute lido
def player(number_guesses, rule_guesses):
    qnt_rule = len(rule_guesses)

    if len(number_guesses) < 10:
        # nos primeiros 10 chutes, chutamos numeros aleatorios para ter uma ideia da regra
        # isso é temporario pq só tem o INT por enquanto ent ele nn tem info nenhuma pra usar
        chute = random.randint(1, 100_000)
        return ["NUMBER", chute]



    if qnt_rule == 0: 
        #verifica se a regra aplica pra todos os numeros
        return ["RULE", ["mod", 1, 0]]
    
    # A partir daqui nós fazemos um chute de regra para
    # cada regra, caso seja descoberto que não é a regra
    # um chute de regra qualquer é feito para passar para
    # testar a proxima regra.
    # OBS: Igor, pode trocar o MOD pelo POT, dependendo do seu algoritimo

    if qnt_rule == 1:
        chute = mod_algorithm(number_guesses, rule_guesses)
        if chute != None:
            return chute
    
    if qnt_rule == 2:
        chute = pot_algorithm(number_guesses, rule_guesses)
        if chute != None:
            return chute

    if qnt_rule >= 3:
        chute = int_algorithm(number_guesses, rule_guesses)
        if chute != None:
            return chute
    
    return ["NUMBER", 67]