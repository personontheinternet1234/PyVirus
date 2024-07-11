import subprocess
output = subprocess.check_output("dir", shell=True)
print(output)