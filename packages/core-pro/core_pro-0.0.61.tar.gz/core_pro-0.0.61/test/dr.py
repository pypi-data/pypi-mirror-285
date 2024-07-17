from src.core_pro import Drive
from pathlib import Path


id = '16CafO9K9uiCCx48rK3g9fCOV7QCv59Vw'
lst_file = [*Path('/media/kevin/75b198db-809a-4bd2-a97c-e52daa6b3a2d/category_tag/raw').glob('*.parquet')]
Drive(debug=True).upload_batches(lst_file=lst_file, folder_id=id)
