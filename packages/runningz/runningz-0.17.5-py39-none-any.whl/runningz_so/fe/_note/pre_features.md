```
# ----------------------------------------------------------------------
# 1m kline, pre features
# 尽量1> 在0~1之间, 或者 2> -1~1, 0对称
# ----------------------------------------------------------------------

# ----------------------------------------> return
# ----------> return, single ti
# to c
o2c =
h2c = 
l2c = 
v2c = 
t2c = 
mid2c =
ask2c = 
bid2c = 

# from open
o2h = 
o2l = 
o2v = 
o2t = 
o2mid = 
o2ask = 
o2bid = 

# other
t2v = 
l2h = 

# ----------> return, daily_xx to intra_xx
Do2o = 
Dc2c = 
Dh2h = 
Dl2l = 
Dv2v = 
Dt2t = 
Dvol2vol = volumne
Da2a = amount = tvrvalue

# ----------> return, pre k ti
# o2c, first of open
o10m2c = roll(first, open, 10)
o1h2c  = roll(first, open, 60)
o0002c = agg(first, open)

# t2c, mean of twap
t10m2v = roll(mean, open, 10)
t1h2v  = roll(mean, open, 60)
t0002v = roll(cummean, open, 999)

# h2h # max of h
# l2l # min of l
# l2h # min of l, max of h
# for each do, 10m = roll, 1h = roll, cum = cum


# ----------------------------------------> v, p
# ----------> tvr = amount = tvrvalue
tvr = o(intra_tvr)
tvr10m = roll(sum, id, tvr, 10, tid)
tvr1h = roll(sum, id, tvr, 60, tid)
cumtvr = roll(sum, x(id,date), tvr, 999, tid)
log1p(tvr) = 
log1p(tvr10m) = 
log1p(tvr1h)
log1p(cumtvr) = 

# ----------> tvr rank
tvrrank = dif(div(agg(rank, tid, tvr), agg(count, tid, tvr)), 1)
cumtvrrank = dif(div(agg(rank, tid, cumtvr), agg(count, tid, cumtvr)), 1)

# ----------> vol / totalfloatshares
volr = intra_volume / totalfloatshares - 1
cumvolr = intra_cumvolume / totalfloatshares - 1


# ----------------------------------------> imbalance
# ----------> ask or bid
log1p_ask_v1p1 = av1 * ap1
log1p_bid_v1p1 = bv1 * bp1
bid_gap = bid_p1 - roll(max, x(id,date), bid_p1, 999, tid)
ask_gap = asp_p1 - roll(min, x(id,date), bid_p1, 999, tid)

# ----------> ask vs bid
imba_v_dif = av1 - bv1
imba_v_rdif = (av1 - bv1) / (av1 + bv1)
imba_p_dif = (ap1 * av1 - bp1 * bv1) / (av1 + bv1)
imba_p_add = (ap1 * av1 + bp1 * bv1) / (av1 + bv1)
logimba = log1p(imba)
spread = ask_p1 / bid_p1 - 1

```