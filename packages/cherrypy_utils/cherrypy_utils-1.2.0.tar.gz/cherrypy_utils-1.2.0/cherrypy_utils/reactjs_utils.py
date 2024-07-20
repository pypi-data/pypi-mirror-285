import subprocess


def npm_build(project_path):
    subprocess.run(
        ["npm", "install"],
        cwd=project_path.resolve(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    subprocess.run(
        ["npm", "run-script", "build"],
        cwd=project_path.resolve(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
