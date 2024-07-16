# %% Imports


import argparse
from jgtpov import calculate_tlid_range as get_tlid_range

# %%
result = get_tlid_range('2021-01-01', 'H4', 1000)
result
# %%
result = get_tlid_range('21-01-01', 'H4', 1000)
result
# %%
result
# %%

# %%
result = get_tlid_range('2021-01-01', 'D1', 1000)

# %%
result
# %%
# %%
result = get_tlid_range('2021-01-01', 'W1', 1000)

# %%
result
# %%
# %%
result = get_tlid_range('2021-01-01', 'M1', 500)

# %%
result
# %%