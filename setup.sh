conda create -y --name ticket python==3.11.8
conda activate ticket

conda install -y -c conda-forge pandas=2.2.3
conda install -y -c conda-forge openpyxl=3.1.5
conda install -y -c conda-forge chromadb=0.6.3
conda install -y -c conda-forge langchain-community=0.3.14
conda install -y -c conda-forge streamlit=1.41.0
conda install -y -c conda-forge ipykernel=6.29.4
python -m ipykernel install --user --name ticket --display-name="ticket"

pip install sentence_transformers==3.3.1
pip install transformers==4.48.0