# project #2

The api will return in plain text the segmented chinese text. The [Lac model](https://github.com/baidu/lac) is used as model, it's based on [paddle](https://github.com/PaddlePaddle/Paddle) for both training and deployment.

## build:

> ### prerequisite
> - I recommand installation by source code which will better match the CUDA/CuDNN version depended by [paddle inference](https://paddle-inference.readthedocs.io/en/latest/user_guides/source_compile.html).
>   - Otherwise, the prebuilt lib is on [paddle inference lib](https://paddle-inference.readthedocs.io/en/latest/user_guides/download_lib.html). Please wisely choose the correct package with your CUDA/CuDNN installed, if no precise version matched, then you have to purge the existed CUDA/CuDNN and reinstall the existed combination.
> - All the CUDA packages can be downloaded here [CUDA Archive](https://developer.nvidia.com/cuda-toolkit-archive). The install instruction is on the [official guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html)
> - Same for [CuDNN Archive](https://developer.nvidia.com/rdp/cudnn-archive) and [CuDNN guide](https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html)
> - Download the lastest [Lac segmentation model](https://github.com/baidu/lac/releases/download/v2.1.0/models_general.zip), unzip it locally.
> - Install [Sougou workflow](https://github.com/sogou/workflow)

Replace path below with path where the dependencies installed above, by default, becareful of the two ***/opt*** path which are customized.

``` bash
"/opt/local_paddle" 
"/usr/lib/x86_64-linux-gnu/"
"/usr/local/cuda/lib64" 
"/usr/include/x86_64-linux-gnu" 
"/usr/lib/x86_64-linux-gnu" 
"/opt/sogou/lib/cmake/workflow/" 
```

Change the path, run the cmake command below.

```bash
mkdir build && cd build
cmake \
    -DPADDLE_LIB=<PADDLE_LIB> \
    -DCUDNN_LIB=<CUDNN_LIB> \
    -DCUDA_LIB=<CUDA_LIB> \
    -DTENSORRT_ROOT=<TENSORRT_ROOT> \
    -DTENSORRT_ROOT_LIB=<TENSORRT_ROOT_LIB> \
    -DWORKFLOW_LIB=<WORKFLOW_LIB> \
    ..
make 
```

## Usage:

```bash
# launch the server
# model_path is the lac model previously downloaded in prerequisite
# custom_dict_path is the custom dict location
./build/server_seg <port> <thread_num> <model_path> <custom_dict_path>

# request server
curl -X POST --data-binary @<test_data> <ip>:<port>
```
### Example

```bash
./build/server_seg 9090 4 $(pwd)/models_general/lac_model $(pwd)/custom_dict.txt

# request server
curl -X POST --data-binary @$(pwd)/test/traited_pullword.log 127.0.0.1:9090
```

## How to add customized segmentation word:


See [add customized word](https://github.com/baidu/lac#%E5%AE%9A%E5%88%B6%E5%8C%96%E5%8A%9F%E8%83%BD) for instruction of custom dict file, and modify the ***custom_dict.txt*** whatever you want, test it as before.

## Benchmark

```bash
# download test case
./benchmark.py download

# run all test
./benchmark.py run

# For a shorter test, download one log file, then stop.
# Use `head -n 1000 ...log > trated_...log` to make a 
# short test case, then `./benchmark.py run`
```

## Benchmark result

spec

| Spec | Config                      |
|------|-----------------------------|
| CPU  | AMD 5800H 8 cores 16 thread |
| RAM  | 16GB                        |
| OS   | Ubuntu 20.04 on WSL 2       |

result

| Process num | Thread num | Time   | Traitment speed |
|-------------|------------|--------|-----------------|
| 2           | 5          | 13.25s | 142.34KWords/s  |
| 2           | 8          | 12.19s | 154.73KWords/s  |
| 2           | 10         | 12.37s | 152.50KWords/s  |
| 8           | 5          | 60.69s | 124.33KWords/s  |
| 8           | 8          | 59.40s | 127.02KWords/s  |
| 8           | 10         | 60.59s | 124.53KWords/s  |