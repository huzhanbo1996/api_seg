#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import subprocess
import signal
import sys
import re
import requests
import os
import wget
import time

TEST_CASE_DIR = "test/"
TEST_URL = "http://116.196.101.207:8080/pullword/"
LOG_PATTERN = r'<a href="(.*?\.log)">'

SHARED_LIB_PATH = "/opt/paddle/all_libs"
BINARY = "/mnt/c/Users/luc/Desktop/liangbo/lac/c++/build/server_seg"
MODEL_PATH = "/mnt/c/Users/luc/Desktop/liangbo/lac/c++/models_general/lac_model"
LOG_LINE_PATTERN = r'^\d{4}-\d+-\d+ \d+:\d+:\d+\t' + \
    r'(.*)\t' + r'.*\t' + r'.*\t' + \
    r'\d+\.\d+\.\d+\.\d+:\d+,seq:\d+'

CURL_PATTERN = "curl -X POST --data-binary @{} '127.0.0.1:{}' "


def bar_progress(current, total, width=80):
    progress_message = "Downloading: %d%% [%d / %d] bytes" % (
        current / total * 100, current, total)
    # Don't use print() as it will print in new line every time.
    sys.stdout.write("\r" + progress_message)
    sys.stdout.flush()


def DownloadTestCases():
    if not os.path.exists(TEST_CASE_DIR):
        os.makedirs(TEST_CASE_DIR)
    testCaseHTML = requests.get(TEST_URL)
    if testCaseHTML.ok:
        logFiles = re.findall(LOG_PATTERN, testCaseHTML.text)
        for fileName in logFiles:
            logUrl = "{0}{1}".format(TEST_URL, fileName)
            print("{}".format(logUrl))
            wget.download(logUrl, TEST_CASE_DIR + fileName, bar=bar_progress)


def FilterTestCases():
    for file in os.listdir(TEST_CASE_DIR):
        if not file.startswith("traited"):
            with open(TEST_CASE_DIR + "/" + file, "r", encoding='utf-8', errors='ignore') as orig, open(TEST_CASE_DIR + "/traited_" + file, 'w+', encoding='utf-8') as out:
                for line in orig.readlines():
                    matched = re.match(LOG_LINE_PATTERN, line)
                    if matched:
                        out.write(matched.group(1) + '\n')
                    elif len(line) > 1:
                        print(line)


def SimpleTest(listPort, threadNum, result):
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = SHARED_LIB_PATH

    listServerProcess = []
    for port in listPort:
        serverProcess = subprocess.Popen("{} {} {} {}".format(
                BINARY, port, threadNum, MODEL_PATH), shell=True, env=env, preexec_fn=os.setsid)
        listServerProcess.append(serverProcess)

    testFiles = []
    fileLength = 0
    for file in os.listdir(TEST_CASE_DIR):
        if file.startswith("traited"):
            with open(TEST_CASE_DIR + "/" + file, "r", encoding='utf-8', errors='ignore') as test:
                testFiles.append(TEST_CASE_DIR + "/" + file)
                fileLength += len(test.read())

    time.sleep(5)
    testProcess = []
    startTime = time.time()
    for test in testFiles:
        for port in listPort:
            print(CURL_PATTERN.format(test, port))
            testCurl = subprocess.Popen(CURL_PATTERN.format(test, port), shell=True)
            testProcess.append(testCurl)
    
    for test in testProcess:
        test.wait()
    
    processNum = len(listPort)
    timeCost = time.time() - startTime
    wordPerSec = fileLength * processNum / timeCost
    with open(result, "a+") as resultFile:
        resultFile.write("{}\t{}\t{:.2f}s\t{:.2f}KWords/s\n".format(processNum, threadNum, timeCost, wordPerSec / 1000.0)) 

    for server in listServerProcess:
        os.killpg(os.getpgid(server.pid), signal.SIGTERM)

    time.sleep(10)


def AllTest():
    SimpleTest([i for i in range(9000,9000+2)], 5, "test/benchmark.txt")
    SimpleTest([i for i in range(9000,9000+2)], 8, "test/benchmark.txt")
    SimpleTest([i for i in range(9000,9000+2)], 10, "test/benchmark.txt")
    SimpleTest([i for i in range(9000,9000+8)], 5, "test/benchmark.txt")
    SimpleTest([i for i in range(9000,9000+8)], 8, "test/benchmark.txt")
    SimpleTest([i for i in range(9000,9000+8)], 10, "test/benchmark.txt")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: {0} download; or; {0} run".format(sys.argv[0]))
    elif sys.argv[1] == "download":
        DownloadTestCases()
        FilterTestCases()
    elif sys.argv[1] == "run":
        AllTest()
    else:
        print("Usage: {1} download; or; {1} run".format(sys.argv[0]))
