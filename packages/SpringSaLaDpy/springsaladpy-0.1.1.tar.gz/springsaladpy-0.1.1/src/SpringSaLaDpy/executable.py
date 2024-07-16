import os
import importlib.resources as pkg_resources
import subprocess
import platform

def simulate(model, runs=1):
    
    os_name = platform.system()

    if os_name == 'Windows':
        executable_name = 'langevin-windows-latest'
        executable_extension = '.exe'
    elif os_name == 'Darwin':
        if platform.version().split('.')[0] == '14':
            executable_name = 'langevin-macos-14'
        else:
            executable_name = 'langevin-macos-13'
        executable_extension = '.app'
    else:
        executable_name = 'langevin-ubuntu-latest'
        executable_extension = ''

    with pkg_resources.path('saladpy', executable_name) as executable_path:
        executable_path = f"{executable_path}{executable_extension}"
        model_path = os.path.abspath(model)
        print(f'Model "{model}" is running') 
        raw_s = r'{}'.format(model_path)
        for i in range(runs):
            subprocess.run([executable_path, 'simulate', raw_s, str(i)])
        output_model_path = os.path.join(model_path[:-4] + '_FOLDER', os.path.split(model_path)[1])
        with open(output_model_path, mode='a') as file:
            file.write(f'Runs: {str(runs)}')
        print(f'Simulation complete, results can be found here: {model_path[:-4]}_FOLDER')

#simulate(r'C:\Users\cpero\Downloads\test_output\Simulation0_SIM.txt')
