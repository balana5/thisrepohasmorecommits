import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor

fileName = "file.txt"
readMe = "README.md"
excludedFiles = ["poetry.lock", "pyproject.toml", ".replit"]
numThreads = 10
batchSize = 10

lastOperation = threading.Lock()
operationState = "add"

def addLetterE():
    with open(fileName, "a") as f:
        f.write("e")

def removeLetterE():
    with open(fileName, "r+") as f:
        content = f.read()
        if content.endswith("e"):
            f.seek(0)
            f.truncate()
            f.write(content[:-1])

def getCommitCount():
    result = subprocess.run(["git", "rev-list", "--count", "HEAD"], capture_output=True, text=True)
    return int(result.stdout.strip())

def updateReadMe(commitCount):
    with open(readMe, "w") as f:
        f.write("hi")

def gitCommitAndPush():
    subprocess.run(["git", "add", fileName, readMe])
    subprocess.run(["git", "commit", "-m", "Pushing through!"])
    subprocess.run(["git", "push"])

def removeExcludedFiles():
    for file in excludedFiles:
        result = subprocess.run(["git", "ls-files", "--error-unmatch", file], capture_output=True)
        if result.returncode == 0:
            subprocess.run(["git", "rm", "--cached", file])

def updateRepo():
    global operationState
    while True:
        with lastOperation:
            for _ in range(batchSize):
                if operationState == "add":
                    addLetterE()
                    operationState = "remove"
                else:
                    removeLetterE()
                    operationState = "add"

        commitCount = getCommitCount() + 1
        updateReadMe(commitCount)
        gitCommitAndPush()

removeExcludedFiles()

with ThreadPoolExecutor(max_workers=numThreads) as executor:
    futures = [executor.submit(updateRepo) for _ in range(numThreads)]
    for future in futures:
        future.result()
