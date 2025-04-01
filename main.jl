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


println(first(df_agg, 15))
println(describe(df_agg[:, Not([:w_geocode_11, :h_geocode_11])]))
println("Number of rows: ", size(df_agg, 1))