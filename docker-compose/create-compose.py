from builtins import input
import readline
readline.parse_and_bind("tab: complete")
lines = []
with open("docker-compose.yaml", 'r') as compose_file:
    for line in compose_file:
        if "${TAG}" in line:
            tag = input("Enter image TAG: ")
            assert isinstance(tag, str)
            line = line.replace("${TAG}", tag)

        elif "${ENV_FILE}" in line:
            env_file = input("Enter path to environment file: ")
            assert isinstance(env_file, str)
            line = line.replace("${ENV_FILE}", env_file)

        elif "${CARBON_DIR}" in line:
            carbon_dir = input("Enter path to Carbon: ")
            assert isinstance(carbon_dir, str)
            line = line.replace("${CARBON_DIR}", carbon_dir)
        lines.append(line)
with open("docker-compose.yaml", 'w') as compose_file:
    for line in lines:
        compose_file.write(line)
