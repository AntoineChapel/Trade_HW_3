import Pkg
Pkg.activate(@__DIR__)
Pkg.add("DataFrames")
Pkg.add("CSV")
Pkg.status()