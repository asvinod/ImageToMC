import polars as pl 
"""
Goal: Keys being a tuble with the 3 values
Values being the block associated 
"""

def clean_csv(csv):
    df = pl.read_csv(csv)
    df = df[["texture", "rgba_avg"]]
    df = df.with_columns(
        pl.col("texture").str.head(-4).alias("texture_fixed")   
    )
    df = df.drop("texture")

    df = df.with_columns(
        pl.col("rgba_avg").str.split(",").alias("rgb")
    )

    df = df.drop("rgba_avg")

    r, g, b = [], [], []
    for l in df["rgb"]:
        lis = list(l)
        r.append(lis[0])
        g.append(lis[1])
        b.append(lis[2])
    
    add_dict = {
        'r': r, 'g': g, 'b': b
    }

    new_df = pl.DataFrame(add_dict)

    combined = pl.concat([df, new_df], how="horizontal")
    combined = combined.drop("rgb")
    combined.write_csv("csv/blocks.csv")
    

def csv_to_dict(csv):
    result = {} 

    df = pl.read_csv(csv)
    rows = df.shape[0]
    for i in range(rows):
        row = df.row(i)

        val = row[0] 
        key = (row[1], row[2], row[3])
        result[key] = val
    #print(result)
    return result        



