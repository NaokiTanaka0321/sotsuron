"""
5段階評価を元に
1.エリート選択
2.ルーレット選択
3.実数値交叉
4.ランダム生成
をしていく。
"""

"""
parent1 = 
[[気導音のdB減り始め, 気導音のdB減り終わり], 0
[耳骨導音のdB減り始め, 耳骨導音のdB減り終わり], 1
[喉骨導音のdB減り始め, 喉骨導音のdB減り終わり], 2
気導音→体内音の重み, 3
耳導音→体内音の重み, 4
喉骨導音→体内音の重み, 5
体内音→自己聴取音の重み, 6
気導音→自己聴取音の重み] 7

f_border = [0→31, 1→44, 2→63, 3→88, 4→125, 5→180, 6→250, 7→355, 8→500, 9→710, 10→1000, 11→1400, 12→2000, 13→2800, 14→4000, 15→5600, 16→8000, 17→11300, 18→16000, 19→22000]
"""

import random
import numpy as np
import bisect

n = 8 #1世代の個数
elite_num = 1 #エリート選択をする個数
roulette_num = 1 #ルーレット選択する個数
BLX_num = 2 #BLXする個数
random_num = 4 #ランダム生成する個数
alpha = 1.5 #BLXの際のパラメーター

#エリート選択のアルゴリズム
def elite_selection(elite_num, evaluation, children): #エリート選択する個数、評価値、パラメーター
    elite_children = []
    elite = []
    evaluation_np = np.array(evaluation)
    for i in range(elite_num):
        elite_i = np.argsort(evaluation_np)[::-1][i]
        elite_children.append(children[elite_i])
        elite.append(elite_i)
    return elite_children, elite
    #返り値：新しい個体が入った配列、エリートの番号が入った配列

#ルーレット選択のアルゴリズム
def roulette_selection(roulette_num, elite, evaluation, children): 
    #ルーレット選択する個数、エリートになった番号評価値、パラメーター
    roulette_children = []
    roulette = []

    #エリート選択された個体をルーレット選択から除外する
    evaluation_for_roulette = []
    for i in range(len(evaluation)):
        if i in elite:
            evaluation_for_roulette.append(0)
        else:
            evaluation_for_roulette.append(evaluation[i])
    
    #ルーレット選択
    for _ in range(roulette_num):
        total = sum(evaluation_for_roulette)
        c_sum = np.cumsum(evaluation_for_roulette)
        roulette_i = bisect.bisect_left(c_sum, total * random.random())
        roulette_children.append(children[roulette_i])
        roulette.append(roulette_i)
        evaluation_for_roulette[roulette_i] = 0
    
    return roulette_children, roulette
    #返り値：新しい個体が入った配列、ルーレット選択された番号が入った配列

#フィルター部分のBLX法
def BLX_filter(parent1, parent2, alpha): #親１、親２、子供の数、探索空間の拡大率
    new_filter = []
    for i in range(3):
        freq_left_width = abs(parent1[i][0]-parent2[i][0])
        freq_right_width = abs(parent1[i][1]-parent2[i][1])
        freq_left_min = max(min(parent1[i][0], parent2[i][0])-freq_left_width*(alpha-1)//2, 0)
        freq_left_max = min(max(parent1[i][0], parent2[i][0])+freq_left_width*(alpha-1)//2, 19)
        freq_right_min = max(min(parent1[i][1], parent2[i][1])-freq_right_width*(alpha-1)//2, 0)
        freq_right_max = min(max(parent1[i][1], parent2[i][1])+freq_right_width*(alpha-1)//2, 19)
        while True:
            freq_left_new = random.randint(freq_left_min, freq_left_max)
            freq_right_new = random.randint(freq_right_min, freq_right_max)
            if freq_left_new < freq_right_new:
                new_filter.append([freq_left_new, freq_right_new])
                break
    return new_filter

#重み部分のBLX法
def BLX_weight(parent1, parent2, alpha): #親１、親２、子供の数、探索空間の拡大率
    #体内音の方
    rectx = abs(parent1[3]-parent2[3])
    recty = abs(parent1[4]-parent2[4])
    xmin = max(min(parent1[3], parent2[3])-rectx*(alpha-1)/2, 0)
    xmax = min(max(parent1[3], parent2[3])+rectx*(alpha-1)/2, 1)
    ymin = max(min(parent1[4], parent2[4])-recty*(alpha-1)/2, 0)
    ymax = min(max(parent1[4], parent2[4])+recty*(alpha-1)/2, 1)

    #自己聴取音の方
    width = abs(parent1[6] - parent2[6])
    pmin = max(min(parent1[6], parent2[6])-width*(alpha-1)/2, 0)
    pmax = min(max(parent1[6], parent2[6])+width*(alpha-1)/2, 1)
    
    while True:
        newx = random.uniform(xmin, xmax)
        newy = random.uniform(ymin, ymax)
        if(newx+newy <= 1):
            newp = random.uniform(pmin, pmax)
            new_weight = [newx, newy, 1-newx-newy, newp, 1-newp]
            return new_weight

#実数値交叉全体の処理
def blx(BLX_num, elite, roulette, children, alpha):
    blx_children = []
    if(len(elite)+len(roulette) >= 2):
        parent1 = children[elite[0]]
        parent2 = children[roulette[0]]
        for _ in range(BLX_num):
            new_filter = BLX_filter(parent1, parent2, alpha)
            new_weight = BLX_weight(parent1, parent2, alpha)
            new_child = new_filter+new_weight
            blx_children.append(new_child)
    return blx_children
    #返り値：新しい個体が入った配列



#ランダム生成のアルゴリズム
def mutation(random_num):
    mutation_children = []
    for _ in range(random_num):
        air_dB_start = random.randint(5, 13)
        air_dB_end = random.randint(air_dB_start+1, 14)
        ear_dB_start = random.randint(5, 13)
        ear_dB_end = random.randint(ear_dB_start+1, 14)
        throat_dB_start = random.randint(5, 13)
        throat_dB_end = random.randint(throat_dB_start+1, 14)

        air_to_body_weight = random.random()
        ear_to_body_weight = random.uniform(0, 1-air_to_body_weight)
        throat_to_body_weight = 1-air_to_body_weight-ear_to_body_weight

        body_to_myvoice_weight = random.random()
        air_to_myvoice_weight = 1-body_to_myvoice_weight

        new_filter = [[air_dB_start, air_dB_end], [ear_dB_start, ear_dB_end], [throat_dB_start, throat_dB_end]]
        new_weight = [air_to_body_weight, ear_to_body_weight, throat_to_body_weight, body_to_myvoice_weight, air_to_myvoice_weight]
        new_child = new_filter+new_weight
        mutation_children.append(new_child)
    return mutation_children


#全体の処理
#変数は左から 親の配列 評価値の配列 1世代の個数 エリート選択の個数 ルーレット選択の個数 実数値交叉の個数 ランダム生成の個数 実数値交叉のパラメーター
def ga(children, evaluation, n, elite_num, roulette_num, BLX_num, random_num, alpha):
    new_children = []

    #エリート選択
    elite_children, elite = elite_selection(elite_num, evaluation, children)
    new_children += elite_children

    #ルーレット選択
    roulette_children, roulette = roulette_selection(roulette_num, elite, evaluation, children)
    new_children += roulette_children

    #実数値交差
    blx_children = blx(BLX_num, elite, roulette, children, alpha)
    new_children += blx_children

    #ランダム生成
    mutation_children = mutation(random_num)
    new_children += mutation_children


    #配列の順番をランダムにする
    random.shuffle(new_children)

    return new_children


