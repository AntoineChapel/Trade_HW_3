import Pkg
Pkg.activate(@__DIR__)
using CSV
using DataFrames

CSV.read("ny_od_main_JT00_2010.csv", df)
head(df, 5)