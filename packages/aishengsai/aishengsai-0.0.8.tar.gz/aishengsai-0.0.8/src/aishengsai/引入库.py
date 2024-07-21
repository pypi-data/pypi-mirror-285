pip install opencv-python

pip install jieba

pip install scikit-learn

pip install imbalanced-learn

pip install labelme

pip install numpy

pip install pandas

pip install seaborn

pip install xgboost

pip install tensorflow

pip install image_classification_model

pip install transformers

pip install torch


# 基础环境配置
python -m pip install --upgrade pip
# 更换 pypi 源加速库的安装
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install modelscope==1.9.5
pip install "transformers>=4.40.0"
pip install streamlit==1.24.0
pip install sentencepiece==0.1.99
pip install accelerate==0.29.3
pip install datasets==2.19.0
pip install peft==0.10.0

MAX_JOBS=8 pip install flash-attn --no-build-isolation