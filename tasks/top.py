from pathlib import Path

from invoke import task

from tasks.assets import download_file


@task
def clean(c):
    """remove recursively generated and cache files (*.pyc, __generated__) """
    from pathlib import Path
    for path in Path().rglob('*.pyc'):
        path.unlink()

    print("*.pyc  directories deleted")


@task
def build(c):
    static_path = Path("scrat/web/static")
    download_file("https://cdn.jsdelivr.net/npm/bulma@0.9.1/css/bulma.min.css", static_path)
    download_file("https://unpkg.com/bulma-prefers-dark", static_path, "bulma-prefers-dark.css")
    c.run("poetry build")
