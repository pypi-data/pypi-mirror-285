
"""
frampp:
    multi-phase
        multi-path
            filter rank add    
"""

可以切换不同模型
from runningz.model.tree import XXXModel as Model

Pooler. 完善pooler


## rank is very slow
[0001] __TEMP__ = agg(rank, x(trade_date, x(ts_code)), pct_chg)                                  time = 9.22


## 取数内存
X_train = dm.get_cols_numpy(xxx, is_big = True)

## 预测内存
model_list_predict, 内存峰值小很多

## getattr 替换掉eval
eval, 不适合启动大任务， 内存不释放
去掉eval启动任务的TODO


params_1
cols_fix, cols_not, cols_init, adv_test
icp



# ==================================================================
1) k = 5 or 5 + fk(i)
2) top + opt
3) pooler, op_type, op_3, comb, agg_roll_2
4) open adv
5) from 2010, 2017
6) valid, 2019, or ..
7) valid_1, valid_2, valid_3, ...



## 289, path_dict: 'cache/00000000/top_opt_20231104_013616_0.2568_289.dict' # /home/rx/temp/runningz/fe
```
1) ~/temp/runningz/fe/config/fm_config.py
    2017-2019
    fm_config_list_ALL = fm_config_list_TOP[:15] + fm_config_list_OPT
2) ~/temp/runningz/fe/FEMaster.py
    open, adv
3)  ~/temp/runningz/fe/config/fm_config_opt.py
    # 'ranker': [('last_ic_icpn_icpm', 300), ('imp_lgb', 50)], # 0.14
    # 'k': int(5 + 5 * (i // 5)), 
    # 'metrics': 'rz_ic_icpn_icpm',
    # 'model': {'num_leaves': 255, 'n_estimators': int(100 + 50 * (i // 2))},
4) ~/temp/runningz/fe/er/pooler.py
    n_num = min(params.get('n_num', 50), len(cols_num_top)) *** good ***
    n_cat = min(params.get('n_cat', 20), len(cols_cat_top))
    op_type_all = ['op_1', 'op_1_v', 'op_2', 'op_2_v', 'op_3', 'op_3_v', 'op_m', 'agg', 'roll', 'agg_comb', 'roll_comb']
```

## 381, path_dict: 'cache/00000000/20102021_20231105_192437_0.1616_381.dict' # /home/rx/temp_1104/runningz/fe
```
1) ~/temp_1104/runningz/fe/config/fm_config.py
    2010-2022
    fm_config_list_ALL = fm_config_list_TOP[:15] + fm_config_list_OPT
2) ~/temp_1104/runningz/fe/FEMaster.py
    open adv
3) ~/temp_1104/runningz/fe/config/fm_config_opt.py
    # 'ranker': [('last_ic_icpn_icpm', 300), ('imp_lgb', 50)], # 0.14
    # 'k': int(5 + 5 * (i // 5)), 
    # 'metrics': 'rz_ic_icpn_icpm',
    # 'model': {'num_leaves': 255, 'n_estimators': int(100 + 50 * (i // 2))},
4) ~/temp_1104/runningz/fe/er/pooler.py
    n_num = min(params.get('n_num', 50), len(cols_num_top))
    n_cat = min(params.get('n_cat', 20), len(cols_cat_top))
    op_type_all = ['op_1', 'op_1_v', 'op_2', 'op_2_v', 'op_3', 'op_3_v', 'op_m', 'agg', 'roll', 'agg_comb', 'roll_comb']
```

# 652   path_dict: 'cache/00000000/DEBUG_20230730_094745_0.2653_437.dict' # /home/rx/project/runningz/fe
path_dict_other:
    - cache/00000000/v2_vwap_0_2_20230806_143902_0.2514_284.dict # /home/rx/project/runningz/fe
```
1) ~/project/runningz_so/fe/config/fm_config.py
    2017-2019
    fm_config_list_ALL = fm_config_list_TOP[:15] + fm_config_list_OPT
2) open adv

3) same with above

4) ~/project/runningz_so/fe/er/pooler.py
    n_num = min(params.get('n_num', 30), len(cols_num_top))
    n_cat = min(params.get('n_cat', 30), len(cols_cat_top))
    op_type_all = ['op_1', 'op_1_v', 'op_2', 'op_2_v', 'op_m', 'agg', 'roll']
```

# 731 path_dict: 'cache/00000000/comb12_20231111_172040_0.2690_266.dict' # /home/rx/runningz/fe
  path_dict_other:
    - cache/00000000/combv3_20231113_132015_0.2675_253.dict # /home/rx/temp_1110/runningz/fe
```
1) ~/runningz/fe/config/fm_config.py
    2017-2019
    fm_config_list_ALL = fm_config_list_OPT

2) ~/runningz/fe/FEMaster.py
    open adv
3) ~/runningz/fe/config/fm_config_opt.py
    'k': 5,
    'ranker': [('last_ic_icpn_icpm', 300), ('imp_lgb', 50)], # 0.14
    'ranker': [('last_ic_icpn_icpm', 500), ('imp_lgb', 50)], # 0.14
    'model': {'num_leaves': 255, 'n_estimators': int(100 + 50 * (i // 2))},

4) ~/runningz/fe/er/pooler.py
    n_num = min(params.get('n_num', max(50, n_num // 4)), n_num)
    n_cat = min(params.get('n_cat', max(20, n_cat // 4)), n_cat)
    op_type_all =  ['op_1', 'op_1_v', 'op_2', 'op_2_v', 'op_3', 'op_3_v', 'op_m', 'agg', 'roll']
    op_type_all += ['agg_comb_1', 'roll_comb_1']
    op_type_all += ['agg_comb_2', 'roll_comb_2']
    # op_type_all += ['agg_2', 'roll_2'] not use
```



TODO
1) cols_origin, not for train. add from zero features
2) add + labels

runningz/fe/config/fm_config_opt.py
runningz/fe/er/pooler.py # op_1_list, 进一步过拟合
runningz/fe/FEMaster.py  # tarin=1,valid=1,find=1, 就可以过拟合
runningz/fe/util/util.py # params  = {**params, 'deterministic': True, 'force_col_wise': True},
runningz/core/op/__init__.py # 打开cos, sin则更进一步过拟合
随机种子影响还蛮大的, 换一个seed再来一遍

