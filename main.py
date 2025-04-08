# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd

# %%
df = pd.read_csv(r"ny_od_main_JT00_2010.csv")

# %%
df.drop(columns=['createdate'], inplace=True)
df['w_tract'] = df['w_geocode'].astype(str).str[:11].astype(int)
df['h_tract'] = df['h_geocode'].astype(str).str[:11].astype(int)
df_agg = df.groupby(['w_tract', 'h_tract']).sum().reset_index().drop(columns=['w_geocode', 'h_geocode'])

# %% [markdown]
# Central county in Albany OMB defined MSA: Albany County, Rensselaer County, Saratoga County, Schenectady County
# 
# Tracts in Albany County, Rensselaer County, Saratoga County, Schenectady County:
# * Albany county: 36001 (central county)
# * Rensselaer county: 36083
# * Saratoga county: 36091
# * Schenectady county: 36093
# 
# Central county in Syracuse OMB defined MSA: 
# * Onondaga County 36067

# %%
df_agg['w_county'] = df_agg['w_tract'].astype(str).str[:5].astype(int)
df_agg['h_county'] = df_agg['h_tract'].astype(str).str[:5].astype(int)
df_agg.head()

# %%
df_agg_s = df_agg[['w_tract', 'h_tract', 'S000', 'w_county', 'h_county']]

# %%
total_worker_per_w_tract = df_agg_s[['w_tract', 'S000']].groupby('w_tract').sum().reset_index()
total_worker_per_h_tract = df_agg_s[['h_tract', 'S000']].groupby('h_tract').sum().reset_index()
df_agg_s1 = pd.merge(df_agg_s, total_worker_per_w_tract, left_on='w_tract', right_on='w_tract', how='inner')
df_agg_s2 = pd.merge(df_agg_s1, total_worker_per_h_tract, left_on='h_tract', right_on='h_tract', how='inner')
df_agg_s2.rename(columns={'S000_x': 'S000', 'S000_y': 'S000_w_total', 'S000': 'S000_h_total'}, inplace=True)

# %%
flow_matrix = df_agg_s2.pivot(index='h_tract', 
                              columns='w_tract', 
                              values='S000').fillna(0) #convert to a (#home x #work) matrix

# %%
tract_home_rows = flow_matrix.index 
tract_work_cols = flow_matrix.columns
flow_matrix_np = flow_matrix.astype(int).values #each row is a home, each column is a work
total_home = np.sum(flow_matrix_np, axis=1)
total_work = np.sum(flow_matrix_np, axis=0)

# %%
counties_home_rows = np.array(tract_home_rows.astype(str).str[:5]).astype(int)
counties_work_cols = np.array(tract_work_cols.astype(str).str[:5]).astype(int)

# %%
core_albany_init = np.unique(np.concatenate((tract_home_rows[counties_home_rows==36001], tract_work_cols[counties_work_cols==36001]), axis=0))
core_syracuse_init = np.unique(np.concatenate((tract_home_rows[counties_home_rows==36067], tract_work_cols[counties_work_cols==36067]), axis=0))

# %%
def update_core(core, flow_matrix, tract_home_rows, tract_work_cols):
    """
    This function updates the core, by adding the tracts that are not in the core but have either:
    * >25% of people who live in the tract work in the core
    * >25% of people who work in the tract live in the core
    """
    row_index_core = np.where(np.isin(tract_home_rows, core))[0]
    col_index_core = np.where(np.isin(tract_work_cols, core))[0]
    total_home = np.sum(flow_matrix, axis=1)
    total_work = np.sum(flow_matrix, axis=0)

    # find indexes of rows and columns that are not in the core but fit the definition 
    indexes_rows_add_core = np.setdiff1d(np.where((flow_matrix[:, col_index_core].sum(axis=1)/total_home) > 0.26)[0], row_index_core, assume_unique=True)
    indexes_cols_add_core = np.setdiff1d(np.where((flow_matrix[row_index_core, :].sum(axis=0)/total_work) > 0.26)[0], col_index_core, assume_unique=True)

    # adds these new tracts to the core
    new_core = np.union1d(core, np.concatenate((tract_home_rows[indexes_rows_add_core], tract_work_cols[indexes_cols_add_core]), axis=0))
    return np.unique(new_core)

# %%
def update_core_iterative(core, flow_matrix, tract_home_rows, tract_work_cols):
    """
    This function updates the core iteratively until no new tracts are added
    """
    core_init_length = core.shape[0]
    while True:
        new_core = update_core(core, flow_matrix, tract_home_rows, tract_work_cols)
        if np.array_equal(new_core, core):
            break
        core = new_core
    core_final_length = core.shape[0]
    print(f"Number of tracts added: {core_final_length - core_init_length}")
    return core

# %%
core_albany = update_core_iterative(core_albany_init, flow_matrix_np, tract_home_rows, tract_work_cols)

# %%
core_syracuse = update_core_iterative(core_syracuse_init, flow_matrix_np, tract_home_rows, tract_work_cols)

# %%
### BUILD COUNTY BASED MAPS

# %%
albany_countybased_omb_list_counties = [36001, 36083, 36091, 36093]
albany_countybased_omb_core = []
for county in albany_countybased_omb_list_counties:
    county_path = f"partnership_shapefiles_{county}/PVS_24_v2_cbsa_{county}.shp"
    county_df = gpd.read_file(county_path)
    albany_countybased_omb_core.append(county_df)
merged_gdf_albany_omb_core = gpd.GeoDataFrame(pd.concat([albany_countybased_omb_core[i] for i in range(len(albany_countybased_omb_list_counties))], ignore_index=True))

# %%
syracuse_countybased_omb_list_counties = [36067]
syracuse_countybased_omb_core = []
for county in syracuse_countybased_omb_list_counties:
    county_path = f"partnership_shapefiles_{county}/PVS_24_v2_cbsa_{county}.shp"
    county_df = gpd.read_file(county_path)
    syracuse_countybased_omb_core.append(county_df)
merged_gdf_syracuse_omb_core = gpd.GeoDataFrame(pd.concat([syracuse_countybased_omb_core[i] for i in range(len(syracuse_countybased_omb_list_counties))], ignore_index=True))

# %%
tracts_ny_path = 'partnership_shapefiles_36/PVS_24_v2_tracts2020_36.shp' 
tracts_ny_df = gpd.read_file(tracts_ny_path)

# %%
tracts_albany_core_gdf = tracts_ny_df.iloc[np.where(np.isin(np.array(tracts_ny_df['TRACTID']).astype(int), core_albany))[0], :]
tracts_syracuse_core_gdf = tracts_ny_df.iloc[np.where(np.isin(np.array(tracts_ny_df['TRACTID']).astype(int), core_syracuse))[0], :]

# %%


# %%
tracts_syracuse_core_gdf.boundary.plot(linewidth=0.3)

# %%



