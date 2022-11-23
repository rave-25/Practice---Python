filenames = ["program.c", "stdio.hpp", "sample.hpp", "a.out", "math.hpp", "hpp.out"]

newFile = [file.replace('hpp', 'h') for file in filenames]
print(newFile)