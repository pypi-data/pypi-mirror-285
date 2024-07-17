from .GSheet import Sheet
import polars as pl
from pathlib import Path
import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from loguru import logger
from time import sleep, perf_counter
from tqdm import tqdm
from datetime import timedelta, datetime
from openpyxl.utils.cell import get_column_letter, column_index_from_string, coordinate_from_string


def update_df(df, sheet_name: str, sheet_id: str, start: str = 'A1'):
    # Call sheet
    sheet = Sheet(sheet_id)
    # Dataframe type
    if isinstance(df, pl.DataFrame):
        col_df = [*df.schema.keys()]
        values = [col_df]
        values.extend(df.to_pandas().astype(str).to_numpy().tolist())
    else:
        col_df = df.columns
        values = df.transpose().reset_index().transpose().astype(str).to_numpy().tolist()
    # Export to sheets
    end = get_column_letter(len(col_df) + column_index_from_string(coordinate_from_string(start)[0]) - 1)
    sheet.clear_gsheet(
        sheet_name,
        sheet_range=f"{start}:{end}"
    )
    sheet.update_value_single_axis(
        sheet_range=f"{start}:{end}",
        value_input=values,
        sheet_name=sheet_name,
        value_option='USER_ENTERED'
    )


def format_df(
        sheet_name: str,
        sheet_id: str,
        num_col: int,
        title_format_start: str = 'A1',
        frozen_rows: int = 2,
):
    # Sheet
    sheet = Sheet(sheet_id)
    ws_id = sheet.get_worksheet_properties(sheet_name)['sheetId']
    # Frozen
    sheet.frozen_view(ws_id, frozen_rows)
    # Title
    sheet.format_title(ws_id, title_format_start)
    # Header
    next_start = ''.join((coordinate_from_string(title_format_start)[0], str(coordinate_from_string(title_format_start)[1] + 1)))
    sheet.format_header(ws_id, next_start, num_col)


def make_dir(folder_name: str | Path) -> None:
    """Make a directory if it doesn't exist'"""
    if isinstance(folder_name, str):
        folder_name = Path(folder_name)
    if not folder_name.exists():
        folder_name.mkdir(parents=True, exist_ok=True)


def update_stt(stt: str, pos: int, sheet_id: str, sheet_name: str):
    Sheet(sheet_id).update_value_single_axis(sheet_range=f'I{pos}', sheet_name=sheet_name, value_input=stt)


def remove_old_file(path, days: int, file_type: str):
    check_date = datetime.today().date() - timedelta(days=days)
    print(f'Files {file_type} before {check_date} ({days} days) will be removed')

    for file in Path(path).glob(f'*.{file_type}'):
        mdate = datetime.fromtimestamp(file.stat().st_mtime).date()
        if mdate < check_date:
            print(f'Remove: file {file.name} - mdate: {mdate}')
            file.unlink()


def rm_all_folder(path: Path | str) -> None:
    """Remove all files in folder recursively"""
    if isinstance(path, str):
        path = Path(path)

    for child in path.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            rm_all_folder(child)

    if path.exists():
        path.rmdir()


def cpu_ram(cache_mem: int = 0) -> int:
    """Memory usage in megabytes"""
    import psutil
    from loguru import logger

    cpu = psutil.cpu_percent()
    mem = psutil.Process().memory_full_info().uss / (1024 ** 2)
    ram_usage = dict(psutil.virtual_memory()._asdict())
    logger.info(
        f"[CPU]: {cpu}% "
        f"[RAM]: Used {ram_usage['used'] / 1024 ** 3}GB "
        f"[Memory]: Cache {cache_mem:,.0f}MB - Current: {mem:,.0f}MB - Diff: {mem - cache_mem:,.0f}MB"
    )
    return mem


def sleep_with_progress(seconds: int, desc: str = ''):
    """ Sleep until specified number of seconds has elapsed"""
    with tqdm(total=seconds, desc=desc) as pbar:
        for _ in range(seconds):
            sleep(1)
            pbar.update(1)


def upload_ds(file_path: Path, api_endpoint: str, ingestion_token: str):
    """ Uploads csv file to DataHub"""
    def my_callback(monitor):
        pbar.update(monitor.bytes_read - pbar.n)

    # files
    file_name = str(file_path)
    file_parent_dir = str(file_path.parent)

    # upload
    m = MultipartEncoder(fields={
        'file': (file_name, open(file_name, 'rb'), 'text/plain'),
        'parent_dir': file_parent_dir
    })
    me = MultipartEncoderMonitor(m, my_callback)
    headers = {'data-ingestion-token': ingestion_token, 'Content-Type': me.content_type}
    total_size = m.len

    while True:
        with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024, desc='Uploading to DataHub', leave=True) as pbar:
            response = requests.request('POST', api_endpoint, headers=headers, data=me)
        if response.status_code != 400:
            break
        sleep_with_progress(60 * 6, desc='Waiting DataHub')

    logger.success(f'{response.json().get('message')}, {file_path.name}')
    return response


def time_decorator(func):
    def wrapper(*args, **kwargs):
        begin_time = perf_counter()
        output = func(*args, **kwargs)
        end_time = perf_counter() - begin_time
        print(f"[Execution Time] {func.__name__}: {end_time:,.2f} sec")
        return output
    return wrapper
