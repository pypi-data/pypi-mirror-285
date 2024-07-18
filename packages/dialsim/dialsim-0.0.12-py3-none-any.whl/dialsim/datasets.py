import os
import pickle
def load_data(root, script_name:str="friends")->tuple:
    """
    A function to load data from the pickle files.
    
    Args:
        script_name (str): one of 'friends', 'theoffice', 'bigbang'.
            Default: "friends"
    
    Returns:
        tuple: (data, oracle_tkg, oracle_fan), where data is the main data, oracle_tkg is the ground truth for tkg-based questions, and oracle_fan is the ground truth for fan-based questions.
    """
    
    if script_name not in ["friends", "theoffice", "bigbang"]:
        raise ValueError("script_name must be one of 'friends', 'theoffice', 'bigbang'")
    if not os.path.exists(f"{root}/data"):
        os.system('wget "https://www.dropbox.com/scl/fi/zpb58dpd1gf54dbs5sfdp/dialsim_v1.1.zip?rlkey=g8ner3up896mrqfio0k100jpu&st=75xceyu6&dl=1" -O dialsim_v1.1.zip')
        os.makedirs(f"{root}/data")
        os.makedirs(f"{root}/prompt")
        os.makedirs(f"{root}/results")
        os.system(f"mv dialsim_v1.1.zip {root}/data")
        os.system(f"unzip {root}/data/dialsim_v1.1.zip -d {root}/data")
        os.system(f"rm {root}/data/dialsim_v1.1.zip")
        os.system(f"mv {root}/data/*.txt {root}/prompt")
    with open(f'{root}/data/{script_name}_dialsim.pickle', 'rb') as f:
        data = pickle.load(f)
    with open(f'{root}/data/{script_name}_oracle_tkg.pickle', 'rb') as f_h:
        oracle_tkg = pickle.load(f_h)
    with open(f'{root}/data/{script_name}_oracle_fan.pickle', 'rb') as f_e:
        oracle_fan = pickle.load(f_e)


    return data, oracle_tkg, oracle_fan