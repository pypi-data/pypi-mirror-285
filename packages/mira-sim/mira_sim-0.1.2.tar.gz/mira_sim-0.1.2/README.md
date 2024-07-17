# MiRA

MiRA (**M**us**i**c **R**eplication **A**ssessment) tool is a model-independent open evaluation method based on four diverse audio music similarity metrics to assess exact data replication of the training set. 

## quick start 

**create and install conda environment**
```
conda create --name mira python=3.10
conda activate mira
python -m pip install --upgrade pip
```

**install mira package**
```
pip install mira-sim
```

**to run KL divergence download [PaSST](https://github.com/kkoutini/PaSST?tab=readme-ov-file#passt-efficient-training-of-audio-transformers-with-patchout) classifier**

```
pip install 'git+https://github.com/kkoutini/passt_hear21@0.0.19'
```

**to run CLAP and DEfNet scores install pythorch...**

```
pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0+cu113 -f https://download.pytorch.org/whl/torch_stable.html 

# note that you can also install pytorch by following the official instruction (https://pytorch.org/get-started/locally/)
### for H100 GPU: pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**... and download corresponding models**

```
mkdir misc/ 
wget -O misc/music_audioset_epoch_15_esc_90.14.pt https://huggingface.co/lukewys/laion_clap/resolve/main/music_audioset_epoch_15_esc_90.14.pt?download=true 
wget -O misc/discogs_track_embeddings-effnet-bs64-1.pb https://essentia.upf.edu/models/feature-extractors/discogs-effnet/discogs_track_embeddings-effnet-bs64-1.pb
```

**Attention!** MiRA expects to find weights in `misc` folder in the directory you run mira. Note that if you would like to store the models elsewhere, you MUST change the location directory `model_path` at files [clap.py](mira/metrics/clap.py) and [defnet.py](mira/metrics/defnet.py). 


**how to use MiRA?**

Run an evaluation by calling `mira` and indicating
the directory of the reference folder (`reference_foldr`), the target folder (`target_folder`) and name of the evaluation or test (`eval_name`). 

Registering results (`log`) is active by default. You can deactivate storing the results by setting log to `no` or you can specify your preferred directory (`log_directory`). If you do not specify any `log` folder where results should be stored, MiRA will create a `log` folder in the current directory automatically.  

MiRA will run the evaluation between the samples in the reference and target folder for four music similarity metrics: CLAP score, DEfNet score, Cover Identification (CoverID) and KL divergence. However, you can specify a metric with `-m` argument. 

```
mira <reference_folder> <target_folder> --eval_name <eval_name> {--log <no/log_directory> -m <clap,defnet,coverid,kld>}
```

**Important!** Note that MiRA is prepared to interpret `wav` files.  
