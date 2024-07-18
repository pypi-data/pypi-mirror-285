import subprocess

# Construct the command as a string
command = 'conda install -c conda-forge scikit-beam'

# Run the command using subprocess with shell=True
result = subprocess.run(command, shell=True)

# Check the result
if result.returncode == 0:
    print("Installation successful")
else:
    print("Installation failed")
