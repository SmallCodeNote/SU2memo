import os
import shutil
import subprocess

# UserParameter
parallelCountMPI = 7
modelName = "model_000_05"
meshFilename = Rf"{modelName}.su2"
workDirectoryPath = Rf"R:\{modelName}"
projectDirectoryPath = ""
baseCfgFilePath = Rf"{projectDirectoryPath}\cfg\model_BaseFormat.cfg"
meshSourceDirectoryPath = Rf"{projectDirectoryPath}\mesh"
msMpiPath = R"C:\Program Files\Microsoft MPI\Bin\mpiexec.exe"
su2MpiPath = Rf"{projectDirectoryPath}\su2_mpi\bin\SU2_CFD.exe"
outputFrequency = 2
timeStep = 10
totalSteps = 100
inner_iter_start = 3
inner_iter_std = 1

def prepare_work_directory():
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

def generate_cfg(step, inner_iter, restart_file=None):
    with open(baseCfgFilePath, "r") as f:
        cfg = f.read()

    ext_iter_offset = (step-1) * timeStep

    cfg = cfg.replace("{{INNER}}", str(inner_iter))
    cfg = cfg.replace("{{TIME_ITER}}", str(1 if step == 0 else ext_iter_offset + timeStep +1 ))
    cfg = cfg.replace("{{MESH_FILENAME}}", meshFilename)
    cfg = cfg.replace("{{OUTPUT_WRT_FREQ}}", str( outputFrequency))
    restart_filename = f"restart/restart_step{step:05d}.dat"
    cfg = cfg.replace("{{RESTART_FILENAME}}", restart_filename)

    if restart_file:
        cfg += f"\nRESTART_SOL= YES"
        cfg += f"\nREAD_BINARY_RESTART= YES"
        
        cfg += f"\nEXT_ITER_OFFSET= {ext_iter_offset+1}"
        cfg += f"\nRESTART_ITER= {ext_iter_offset+1}"
        cfg += f"\nWINDOW_START_ITER= {ext_iter_offset+1}"

    cfg_filename = os.path.join(workDirectoryPath,f"{modelName}_step{step:05d}.cfg")
    with open(cfg_filename, "w") as f:
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

def main():
    prepare_work_directory()
    for step in range(totalSteps):
        inner_iter = inner_iter_start if step == 0 else inner_iter_std
        restart_file = None if step == 0 else f"restart/restart.dat"
        cfg_file = generate_cfg(step, inner_iter, restart_file)
        run_su2(cfg_file)

if __name__ == "__main__":
    main()
