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

    
    
def pot_mod_algorithm(number_guesses, rule_guesses):
    # hashmap para facilitar nas buscas
    historico = {chute: (direcao, acerto) for chute, direcao, acerto in number_guesses}
    
    if len(number_guesses) == 0:
        # Chuta 100 primeiro pq
        # no mod tem plmns 1 numero pra esquerda e direita
        # no pot a dist maxima é 99
        # pro int é meio ruim, mas fzr oq 
        return ["NUMBER", 100]

    # Encontrar se temos os corretos
    corretos = []
    for chute, direcao, acerto in number_guesses:
        if acerto:
            corretos.append(chute)

    # evita repetidos, no caso do mod pode acontecer de ter mais de um chute correto, mas eles seriam o mesmo numero
    corretos = list(set(corretos)) 



    # caso nn tenha chute correto, usa a direção q o 100 aponta     
    if len(corretos) == 0:
        if len(number_guesses) > 30: # distmax do mod é 50, ent chutamos um pouco mais vezes que a metade dele
            print("Tentando POT")
            pots_possiveis = []
            for i in range(1, 400):
                for j in range(2, 11):
                    # i^j (potência)
                    pots_possiveis.append((i**j, j))

            for chute, direcao, acerto in number_guesses:
                if direcao == "maior" and not acerto:
                    pots_possiveis = [ (val, j) for (val, j) in pots_possiveis if val > chute ]
                elif direcao == "menor" and not acerto:
                    pots_possiveis = [ (val, j) for (val, j) in pots_possiveis if val < chute ]

            pots_paraChutar = list(set([j for (val, j) in pots_possiveis]))
            
            # Remover os pots que já tentamos chutar na rules_guesses
            pots_ja_chutados = [p1 for tipo, p1, p2 in rule_guesses if tipo == "pot"]
            pots_paraChutar = [p for p in pots_paraChutar if p not in pots_ja_chutados]

            if len(pots_paraChutar) > 0:
                print("chutando POT", pots_paraChutar[0])
                return ["RULE", ["pot", pots_paraChutar[0], 0]]
            else:
                print("INDO PARA INT")
                return "VAI_PRO_INT" 
            
            
        ultimo_chute, direcao_ultimo, _ = number_guesses[-1]
        
        # Testar inversão (estamos indo de 2 em 2)
        if len(number_guesses) >= 2:
            penultimo_chute, direcao_penultimo, _ = number_guesses[-2]
            if direcao_ultimo != direcao_penultimo and (ultimo_chute - penultimo_chute) != 0:
                if direcao_penultimo == "maior":
                    return ["NUMBER", ultimo_chute - 1]
                else:
                    return ["NUMBER", ultimo_chute + 1]

        # Continuar de 2 em 2
        if direcao_ultimo == "maior":
            return ["NUMBER", ultimo_chute + 2]
        else:
            return ["NUMBER", ultimo_chute - 2]


    if len(corretos) == 1: # com um procura outro
        # Pega o n correto
        n_correto = corretos[0]
        # testamos n+1 e n-1
        if (n_correto + 1) not in historico:
            return ["NUMBER", n_correto + 1]
        if (n_correto - 1) not in historico:
            return ["NUMBER", n_correto - 1]
            
        # Vemos o resultado deles
        dir_mais, acerto_mais = historico[n_correto + 1]
        dir_menos, acerto_menos = historico[n_correto - 1]
        
        if acerto_mais or acerto_menos:
            # Vamos para o int
            return "VAI_PRO_INT"
            
        else:
            # Temos um correto e n+1 e n-1 não são corretos (não é do int)
            # Então podemos já tentar adivinhar a regra POT
            pots_possiveis = []
            for base in range(1, 400):
                for p in range(2, 11):
                    pots_possiveis.append((base**p, p))

            # Filtrar pelos chutes do number_guesses (incluindo o correto e os erros)
            for chute, direcao, acerto in number_guesses:
                if acerto:
                    pots_possiveis = [ (val, p) for (val, p) in pots_possiveis if val == chute ]
                elif direcao == "maior":
                    pots_possiveis = [ (val, p) for (val, p) in pots_possiveis if val > chute ]
                elif direcao == "menor":
                    pots_possiveis = [ (val, p) for (val, p) in pots_possiveis if val < chute ]

            pots_para_chutar = list(set([p for (val, p) in pots_possiveis]))
            pots_ja_chutados = [p1 for tipo, p1, p2 in rule_guesses if tipo == "pot"]
            pots_para_chutar = [p for p in pots_para_chutar if p not in pots_ja_chutados]

            if len(pots_para_chutar) > 0:
                print("chutando POT com 1 acerto", pots_para_chutar[0])
                return ["RULE", ["pot", pots_para_chutar[0], 0]]
            
            # Se não sobrou nenhum pot, então vai buscar o segundo correto pro mod
            dir_100 = historico.get(100, (None, None))[0]
            procurando_2o_n = False
            valor_busca = None
            direcao_busca = None
            qnt_2a_busca = 0
            for chute, direcao, acerto in number_guesses:
                # vê se tem chutes da direção contrario do primeiro
                # correto
                if dir_100 == "maior":
                    if chute <= 100 and not acerto and (chute != 100 or number_guesses.count([chute, direcao, acerto]) > 1):
                        # Pelo menos um chute menor ou igual a 100 que não seja o chute original do 100
                        pass
                    if chute < 100 and not acerto:
                        procurando_2o_n = True
                        direcao_busca = "menor"
                        qnt_2a_busca += 1
                elif dir_100 == "menor":
                    if chute > 100 and not acerto:
                        procurando_2o_n = True
                        direcao_busca = "maior"
                        qnt_2a_busca += 1

            if not procurando_2o_n:
                direcao_busca = "maior" if dir_100 == "menor" else "menor"
                # O Pulo da otimização restaurado e corrigido 
                # (100 aponta pro lado mais proximo, então a gente pula a mesma distancia + 1 para o outro lado)
                valor_busca = 100 + (100 - n_correto)
                
                # Se eu quero ir para a esquerda ("menor"), tenho que DIMINUIR. Se for para a direita, tenho que SOMAR.
                # O bug original de ficar preso no 100 era porque os sinais + e - estavam invertidos e te jogavam de volta.
                if direcao_busca == "menor":
                    valor_busca -= 1
                elif direcao_busca == "maior":
                    valor_busca += 1
                
                return ["NUMBER", valor_busca]

            # chutamos igual no inicio porem reverso
            ultimo_chute, direcao_ultimo, _ = number_guesses[-1]

            if qnt_2a_busca >= 2: # verifica reversão
                penultimo_chute, direcao_penultimo, _ = number_guesses[-2]
                if direcao_ultimo != direcao_penultimo and (ultimo_chute - penultimo_chute) != 0:
                    if direcao_penultimo == "maior":
                        return ["NUMBER", ultimo_chute - 1]
                    else:
                        return ["NUMBER", ultimo_chute + 1]

            # Continuar de 2 em 2 usando a direcao_busca
            if direcao_busca == "maior":
                return ["NUMBER", ultimo_chute + 2]
            else:
                return ["NUMBER", ultimo_chute - 2]
    
    if len(corretos) == 2:
        # temos os 2 n, agora é só chutar a regra certa
        print("certos",corretos[0], corretos[1])
        k_certo = abs(corretos[0] - corretos[1])
        r1_certo = corretos[0] % k_certo
        r2_certo = corretos[1] % k_certo
        if r1_certo == r2_certo:
            return ["RULE", ["mod", k_certo, r1_certo]]
        else:
            raise(Exception("ERRO, DOIS CORRETOS COM RESTOS DIFERENTES, MAS AINDA ASSIM CHEGOU AQUI"))

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

# roda quando tem regra repetida
def quando_congela(number_guesses, rule_guesses, regra):
    tipo, p1, p2 = regra

    if tipo == "mod":
        corretos = []
        for chute, direcao, acerto in number_guesses:
            if acerto:
                corretos.append(chute)
        if len(corretos) == 2:
            # temos 2 ns e a regra certa foi pulada, vamos resolver

            for i in range(2, 101):
                if corretos[0] % i == corretos[1] % i:
                    para_chutar = ["mod", i, corretos[0] % i]
                    if para_chutar not in rule_guesses:
                        return ["RULE", para_chutar]
            
            


        return ["RULE", ["mod", p1, p2]]


def quando_incorreto(number_guesses, rule_guesses, chute):
    return ["NUMBER", 67]

def player(number_guesses, rule_guesses):
    regras_hash = dict()
    regra_repetida = None

    for rg in rule_guesses:
        tipo, p1, p2 = rg
        if (tipo, p1, p2) in regras_hash:
            regra_repetida = (tipo, p1, p2)
        else:
            regras_hash[(tipo, p1, p2)] = True

    
    if regra_repetida is not None:
        print("Regra repetida detectada:", regra_repetida)
        return quando_congela(number_guesses, rule_guesses, regra_repetida)
    
    # Verifica se já pulamos pro int verificando se o chute falso de mod já foi dado
    ja_pulou_pro_int = False
    # ja chutou n mod 2 = 1,
    mod_2_igual_1_chutado = False
    mod_2_igual_0_chutado = False
    for r in rule_guesses:
        # Se a regra for mod 1 0, é o nosso sinal para ir pro int_algorithm
        if r[0] == "mod" and r[1] == 1 and r[2] == 0:
            ja_pulou_pro_int = True
        
        if r[0] == "mod" and r[1] == 2 and r[2] == 1:
            mod_2_igual_1_chutado = True
        
        if r[0] == "mod" and r[1] == 2 and r[2] == 0:
            mod_2_igual_0_chutado = True

    if not mod_2_igual_1_chutado:
        # chutamos ele pq ele faz da erro
        return ["RULE", ["mod", 2, 1]]

    if not mod_2_igual_0_chutado:
        # chutamos ele pq ele faz da erro
        return ["RULE", ["mod", 2, 0]]
            
    if not ja_pulou_pro_int:
        chute = pot_mod_algorithm(number_guesses, rule_guesses)
        if chute == "VAI_PRO_INT":
            # Aqui fazemos um chute de regra aleatório para forçar o erro e pular para a regra 'int' no próximo turno
            return ["RULE", ["mod", 1, 0]]
        
        if chute[0] == "NUMBER" and (chute[1] < 1 or chute[1] > 100_000):
            return quando_incorreto(number_guesses, rule_guesses, chute)
        
        if chute != None:
            return chute

    else:
        chute = int_algorithm(number_guesses, rule_guesses)
        if chute != None:
            if chute[0] == "NUMBER" and (chute[1] < 1 or chute[1] > 100_000):
                return quando_incorreto(number_guesses, rule_guesses, chute)
            return chute
    
    return ["NUMBER", 67]