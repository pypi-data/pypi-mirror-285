from importlib import resources as impresources
import itertools
import io

from . import data

linaro_forge_file_path = impresources.files(data) / "linaro_forge_commands.txt"
linaro_forge_initEndSplit = -1

def define_initialise(profilefile: io.TextIOWrapper, profilerdict: dict = None):
    '''
    define_initialise creates any needed variables, and writes the required arguments into the profile_file in order
    to initialise the profiling for a user, in this case that is Linaro Forge MAP.

    Parameters
    ----------
    profilefile: io.TextIOWrapper = Open text file that can be written to and is being used to initiate, call and
        terminate all profiling codes that are to be executed with the user specified bash script.
    profilerdict: dict = dictionary containing required arguments that the profiler has or other values.

    Returns
    -------
    None
    '''
    global linaro_forge_file_path
    global linaro_forge_initEndSplit
    if 'code_line' not in profilerdict.keys():
        exit("Linaro Forge requires the 'code_line' entry containing the string of the line where Linaro Forge "
             "should be used for profiling.")


    profilefile.write('# linaro_forge initialisation declarations\n')
    if 'requirements' in profilerdict.keys():
        for i in profilerdict['requirements']:
            profilefile.write(i)
            profilefile.write('\n')
    profilefile.write('\n')
    profilefile.write('export LINARO_RUNNING_DIR=${WORKING_DIR}/LinaroForge\n')
    with open(linaro_forge_file_path, 'r') as read_file:
        for number, line in enumerate(read_file):
            if line == '# *=*\n':
                linaro_forge_initEndSplit = number + 1
                break
            profilefile.write(line)
    profilefile.write('# Linaro Forge initialisation done\n')
    profilefile.write('\n')
    return

def define_run(profilefile: io.TextIOWrapper, bash_options: list, works: list = None,
               tmp_work_script: str = './tmp_workfile.sh', profilerdict: dict = None):
    '''
    define_run calls the user given bash script using linaro_forge to execute and profile the work done.
    Parameters. This only has to be defined, if the profiler in question is used to execute the user given bash script.
    ----------
    profilefile: io.TextIOWrapper = Open text file that can be written to and is being used to initiate, call and
        terminate all profiling codes that are to be executed with the user specified bash script.
    bash_options: list = List of bash options that the user specified bash script needs to execute as intended
    tmp_work_script: str = Path and name of the temporary work script that contains all the users code minus
        queue options.

    Returns
    -------
    None
    '''
    print(profilerdict['code_line'])
    for work_line in range(len(works)):
        for code_line in profilerdict['code_line']:
            if code_line in works[work_line]:
                works[work_line] = "map --profile --no-queue " + works[work_line]
                print(works[work_line])
    profilefile.write('' +
                      '{} {}\n'.format(tmp_work_script, ' '.join(str(x) for x in bash_options)))
    profilefile.write('\n')
    return works


def define_end(profilefile: io.TextIOWrapper):
    '''
    define_end terminates and scrapes any data from the profiler that was used to profile the user specified bash
    script, in this case that is linaro_forge.
    Parameters
    ----------
    profilefile: io.TextIOWrapper = Open text file that can be written to and is being used to initiate, call and
        terminate all profiling codes that are to be executed with the user specified bash script.

    Returns
    -------
    None
    '''
    global linaro_forge_file_path
    global linaro_forge_initEndSplit
    profilefile.write('# Linaro_Forge final steps declarations\n')
    with open(linaro_forge_file_path, 'r') as read_file:
        for line in itertools.islice(read_file, linaro_forge_initEndSplit, None):
            profilefile.write(line)
    profilefile.write('# Linaro_Forge final steps done\n')
    profilefile.write('\n')
    return
