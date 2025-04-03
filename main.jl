import Pkg
Pkg.activate(@__DIR__)
using CSV
using DataFrames

df = CSV.read("ny_od_main_JT00_2010.csv", DataFrame)

df.w_geocode_11 = [parse(Int, string(x)[1:11]) for x in df.w_geocode]
df.h_geocode_11 = [parse(Int, string(x)[1:11]) for x in df.h_geocode]

df = df[:, Not([:w_geocode, :h_geocode, :createdate])]

df_agg = combine(
    groupby(df, [:w_geocode_11, :h_geocode_11]),
    Not([:w_geocode_11, :h_geocode_11]) .=> sum
)
#w_geocode: workplace census tract code
#h_geocode: home census tract code
#S000: total number of jobs
#SA01: number of workers age 29 or younger
#SA02: number of workers age 30-54
#SA03: number of workers age 55 or older
#SE01: number of jobs with earnings 1250 or less
#SE02: number of jobs with earnings 1251-3333
#SE03: number of jobs with earnings above 3334
#SI01: number of jobs in goods producing industry sectors
#SI02: number of jobs in Trade, Transportation and Utilities
#SI03: number of jobs in All Other Services


println(describe(df_agg[:, Not([:w_geocode_11, :h_geocode_11])]))
println("Number of rows: ", size(df_agg, 1))


# Central county in Albany OMB defined MSA: Albany County, Rensselaer County, Saratoga County, Schenectady County
# Tracts in Albany County, Rensselaer County, Saratoga County, Schenectady County:
## Albany county: 36001
## Rensselaer county: 36083
## Saratoga county: 36091
## Schenectady county: 36093
# Central county in Syracuse OMB defined MSA: Onondaga County 36067

df_agg.w_county = [parse(Int, string(x)[1:5]) for x in df_agg.w_geocode_11]
df_agg.h_county = [parse(Int, string(x)[1:5]) for x in df_agg.h_geocode_11]

df_agg.albany_core = [x in [36001, 36083, 36091, 36093] ? 1 : 0 for x in df_agg.w_county]
df_agg.syracuse_core = [x == 36067 ? 1 : 0 for x in df_agg.w_county]

println(first(df_agg, 10))
