import os
import shutil
import subprocess
import re

# ModelList
modelNames = ["SimpleTestModelC"]

# Parameter
parallelCountMPI = 7
projectDirectoryPath  = R"D:\Code\25\SU2memo"
saveDirectoryPath  = R"R:"
workTopDirectoryPath = Rf"{saveDirectoryPath}\result\try05"
baseCfgFilePath = Rf"{projectDirectoryPath}\cfg\incRANS_BaseFormatC.cfg"
meshSourceDirectoryPath = Rf"{projectDirectoryPath}\mesh"
su2MpiPath = Rf"SU2_CFD.exe"
msMpiPath = R"C:\Program Files\Microsoft MPI\Bin\mpiexec.exe"
outputFrequency = 10
cofigCreateTimeStep = 100
simTimeStep=0.0001
totalSteps = 5
inner_iter_start = 20000
inner_iter_std = 2000


def prepare_work_directory(workDirectoryPath, meshFilename):
    if not os.path.exists(workDirectoryPath):
        os.makedirs(workDirectoryPath)
        print(f"Created work directory: {workDirectoryPath}")
    os.chdir(workDirectoryPath)

    if not os.path.exists(meshFilename):
        source_path = os.path.join(meshSourceDirectoryPath, meshFilename)
        if os.path.exists(source_path):
            shutil.copy(source_path, meshFilename)
            print(f"Copied mesh file from {source_path} to {workDirectoryPath}")
        else:
            raise FileNotFoundError(f"Mesh file not found in source directory: {source_path}")

    for subdir in ["restart", "surface"]:
        if not os.path.exists(subdir):
            os.makedirs(subdir)
            print(f"Created subdirectory: {subdir}")

def generate_cfg(modelName, workDirectoryPath, meshFilename, step, inner_iter, restart_file=None):
    with open(baseCfgFilePath, "r", encoding="utf-8") as f:
        cfg = f.read()

    ext_iter_offset = (step - 1) * cofigCreateTimeStep
    cfg = cfg.replace("{{INNER}}", str(inner_iter))
    cfg = cfg.replace("{{TIME_ITER}}", str(1 if step == 0 else ext_iter_offset + cofigCreateTimeStep + 1))
    cfg = cfg.replace("{{MESH_FILENAME}}", meshFilename)
    cfg = cfg.replace("{{OUTPUT_WRT_FREQ}}", str(outputFrequency))
    restart_filename = f"restart/restart_step{step:05d}.dat"
    cfg = cfg.replace("{{RESTART_FILENAME}}", restart_filename)
    cfg = cfg.replace("{{TIME_STEP}}", str(simTimeStep))

    #cfg = re.sub(r"RESTART_SOL=.*", "", cfg)
    #cfg = re.sub(r"READ_BINARY_RESTART=.*", "", cfg)
    #cfg = re.sub(r"RESTART_FILENAME=.*", "", cfg)

    if restart_file:
        cfg += f"\nRESTART_SOL= YES"
        cfg += f"\nREAD_BINARY_RESTART= YES"
        cfg += f"\nEXT_ITER_OFFSET= {ext_iter_offset + 1}"
        cfg += f"\nRESTART_ITER= {ext_iter_offset + 1}"
        cfg += f"\nWINDOW_START_ITER= {ext_iter_offset + 1}"

    cfg_filename = os.path.join(workDirectoryPath, f"{modelName}_step{step:05d}.cfg")
    with open(cfg_filename, "w", encoding="utf-8") as f:
        f.write(cfg)

    return cfg_filename

def run_su2(cfg_file):
    command = [
        msMpiPath,
        "-n", str(parallelCountMPI),
        su2MpiPath,
        cfg_file
    ]
    print(f"Running: {' '.join(command)}")
    subprocess.run(command)

def process_model(modelName):
    meshFilename = f"{modelName}.su2"
    workDirectoryPath = Rf"{workTopDirectoryPath}\{modelName}"
    prepare_work_directory(workDirectoryPath, meshFilename)

    for step in range(totalSteps):
        inner_iter = inner_iter_start if step == 0 else inner_iter_std
        restart_file = None if step == 0 else f"restart/restart.dat"
        cfg_file = generate_cfg(modelName, workDirectoryPath, meshFilename, step, inner_iter, restart_file)
        run_su2(cfg_file)

def main():
    for modelName in modelNames:
        print(f"\n=== Processing {modelName} ===")
        process_model(modelName)

if __name__ == "__main__":
    main()
