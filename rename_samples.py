import os

sample_dir = 'samples'
file_pattern = "id_%06d"

i = 0
for fname in os.listdir(sample_dir):
    os.rename(os.path.join(sample_dir, fname), file_pattern % i)
    i += 1
