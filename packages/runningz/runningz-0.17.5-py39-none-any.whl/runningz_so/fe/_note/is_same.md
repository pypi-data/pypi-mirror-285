
```
一致性
1） 更新数据前后
    线上5号， 有6号数据之后，再跑5号，
    对比5号, MODE = 'ONLINE' # 'CHECK'
    结论: corr = 1, 
    最后一天的数据是一致的

2）不同终点
    线上5号， 有6号数据之后，跑6号，对比5号, (5号不一样, 因为截面不一样, 对比1,2,3,4号)
    结论: corr = 1
    滚动生成特征, 和一口气生成的, 过程每一天都是一致的

3）不同起点
    2010的数据， 线上5号，
    用2017的数据，线上5号
    结论: 存在少数 corr != 1
    win_max = 258
    ndays = 700, 0 fail
    ndays = 492, 1 fail, 0.999958, inv(roll(sum, ts_code, oma(ret(twap, close), mul(amount, log_ret(low, close))), trade_date, 15))
    ndays = 272, 2 fail, 0.999947, roll(argmin__addsc__sum, ts_code, qtq(agg(max__gapss__firstv, trade_date, log_ret(dow, y_shift_1)), inv(roll(sum, ts_code, oma(ret(twap, close), mul(amount, log_ret(low, close))), trade_date, 15))), trade_date, 10)
    ndays = 262, same with 272
    ndays = 243, 3 fail, 0.999877, roll(std, ts_code, roll(shift, ts_code, roll(std, ts_code, roll(mean, ts_code, gapcs(roll(shift, ts_code, max(y_mean, mean_ret), trade_date, 2), dif(y_shift_2, ret(close, twap))), trade_date, 50), trade_date, 115), trade_date, 1), trade_date, 90)

4）对比scale
    线上5号，重新模型。再跑6号，用6号scale，看scale是否变化
    结论: 完全一致
```

```
# scale_DICT: keep same
# MODE = 'ONLINE'

import os
os.environ['rz_token'] = '5bc2502a20241231'
import numpy as np
import pandas as pd
import runningz as rz
from tqdm.notebook import tqdm
rz.__version__, rz.__file__

dm1 = rz.load_dm('/home/public/data/output/20240111_v2_289_mlp/FE/dm.rz')
dm2 = rz.load_dm('/home/public/data/output/20240111_v2_289_mlp_debug/FE/dm.rz')

date_debug = 20240111
dm1.set_mask(dm1.get_col_numpy('trade_date') == date_debug, 'CMP')
dm2.set_mask(dm2.get_col_numpy('trade_date') == date_debug, 'CMP')

# s = (set(s1.values) & set(s2.values))
# idx_1 = s1.isin(s).values
# idx_2 = s2.isin(s).values

df_cmp = []
for ci, col in enumerate(tqdm(dm1.head().columns)):
    s1 = dm1.get_col_pandas(col, mask_name='CMP')#[idx_1]
    s2 = dm2.get_col_pandas(col, mask_name='CMP')#[idx_2]
    dtype = str(s1.dtype)
    corr, diff_abs, diff_cnt = cmp_2s(s1, s2)
    df_cmp.append([col, corr, diff_abs, diff_cnt])
    if diff_abs > 1e-6:
        print(f'[{ci:04d}] corr = {corr:.6f}, diff_abs = {diff_abs:.6f}, diff_cnt = {diff_cnt} | {dtype:<6} | {col}')
df_cmp = pd.DataFrame(df_cmp, columns = ['col', 'corr', 'diff_abs', 'diff_cnt'])

print(df_cmp.sort_values('corr')[:10])
print(df_cmp.sort_values('diff_abs', ascending = False))
# df_cmp['corr'].value_counts()
# df_cmp['diff_abs'].value_counts()
# print(df_cmp['diff_cnt'].value_counts())


name_dict = rz.DataMaster().namer.name_list_2_dict(['inv(roll(sum, ts_code, oma(ret(twap, close), mul(amount, log_ret(low, close))), trade_date, 15))'])
fe_list = []
namer = rz.DataMaster().namer
namer.dict_2_fe(name_dict, fe_list)
cols = [x['name'] for x in fe_list]

col = 'inv(roll(sum, ts_code, oma(ret(twap, close), mul(amount, log_ret(low, close))), trade_date, 15))'
s1 = dm1.get_col_pandas(col, mask_name='CMP').reset_index(drop = True)
s2 = dm2.get_col_pandas(col, mask_name='CMP').reset_index(drop = True)

s1[(s1 != s2)]
s2[(s1 != s2)]

dm1.get_cols_pandas(cols, mask_name='CMP').iloc[4210:4210+1]
dm2.get_cols_pandas(cols, mask_name='CMP').iloc[4210:4210+1]
```