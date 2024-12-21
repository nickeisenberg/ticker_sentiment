import os
lines = 0
for root, dir, files in os.walk("./"):
    for f in files:
        if f.endswith(".pyc"):
            continue
        if f.endswith(".git"):
            continue
        with open(os.path.join(root, f), "r") as ff:
            lines += len(ff.readlines())
print(lines)

