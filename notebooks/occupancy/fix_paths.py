import re

# Read the notebook
with open('f:/cpts/projects/437_project/notebooks/occupancy/10_occupancy_data_transformation.ipynb', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all ../data/ with ../../data/
content = content.replace("'../data/", "'../../data/")
content = content.replace('"../data/', '"../../data/')

# Write back
with open('f:/cpts/projects/437_project/notebooks/occupancy/10_occupancy_data_transformation.ipynb', 'w', encoding='utf-8') as f:
    f.write(content)

print(" All paths updated from '../data/' to '../../data/'")
