import os

DESC_KEY = 'aeroelectric'
PREFIX = 'ae__'
output_dir = f"../data/{DESC_KEY}/"

aFiles = os.listdir(output_dir)
for file in aFiles:
    old_path = output_dir+file
    new_path = output_dir+PREFIX+file
    print(f"renaming {old_path} to {new_path}")
    os.rename(old_path,new_path)