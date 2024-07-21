
1. params_res
    config/res_config.py

2. args
1) parser.add_argument('--task', type=str, default='DEBUG')
任务名字

2) parser.add_argument('--label', nargs=3, default=['vwap', 0, 1])
使用的label, 3元组决定label

3) parser.add_argument('--label_from_str', type=str, default='')
使用的label, 优先级最高, 字符串定义label, [RAW,ADD,MLP]__p,i,j
用来跑res_labels.py

4) parser.add_argument('--look', nargs=2, default=[None] * 2)
look date的时间范围, 用来跑res_roll.py

5) parser.add_argument('--debug', nargs='*', default=None, help='help info') # any number of
是否debug模式

6) parser.add_argument('--dump', nargs='*', default=None)
将cols_fea, dump到处config

7) parser.add_argument('--init', nargs='*', default=None)
init, 作为eval, 并退出


3. TODO
1) 辅助label 
3) icp不行, 看icp_q20
4) n_update_depth
5) config, 串到pipeline
6) extra = False, 随机性问题
7) early_stopping, 回退到之前
8) 逐渐加深度, 逐渐加cols_exist, 

4. DONE
1) np.float32 -> np.float64, 保证std = 1
2) 正交y_pred_exist, 有3-5千分点提升
