from datetime import datetime
from pathlib import Path

from django.conf import settings

from config.celeryapp import app
from core.inout import files


@app.task(bind=True)
def write_test_file(arg):
    temp = Path(settings.ROOT_DIR) / "temp"
    temp.mkdir(exist_ok=True, parents=True)
    path = temp / "celery-beat-test.txt"
    path.touch(exist_ok=True)
    # r mode files are always strings
    content: str = files.read_from_disk(path=path, mode="r")  # type: ignore[annotation-unchecked]
    content += f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {arg} \n"
    return files.write_to_disk(path=path, content=content, panic=True, log_errors=True)
