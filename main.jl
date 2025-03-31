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


println(first(df_agg, 15))