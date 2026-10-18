import json
from copy import deepcopy
from pathlib import Path

BASE = Path(__file__).resolve().parent / 'data'
BASE.mkdir(exist_ok=True)


def load(name, default):
    """Devuelve los registros guardados. Si el archivo está dañado, lo respalda
    en lugar de sobrescribirlo, para no perder datos."""
    path = BASE / f'{name}.json'
    if not path.exists():
        data = deepcopy(default)
        save(name, data)
        return data
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (ValueError, OSError):
        backup = path.with_name(f'{name}.corrupto.json')
        try:
            path.replace(backup)
        except OSError:
            pass
        return deepcopy(default)


def save(name, records):
    """Escritura atómica: primero a un temporal y luego se reemplaza el original."""
    path = BASE / f'{name}.json'
    tmp = path.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(path)
