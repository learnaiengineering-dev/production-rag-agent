"""Prompts as versioned files, pinned by hash.

prompts/<name>/<version>.txt   one file per version, never edited after release
prompts.lock.json              which version is live, plus each version's sha256
"""
import hashlib, json, os

ROOT = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(path) as f:
        return f.read()


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def load(name, version=None, root=ROOT):
    """Return (version, hash, text). Refuses a file that no longer matches its locked hash."""
    lock = json.loads(read(os.path.join(root, "prompts.lock.json")))
    version = version or lock[name]["live"]
    text = read(os.path.join(root, "prompts", name, version + ".txt"))
    want = lock[name]["versions"][version]
    if sha(text) != want:
        raise ValueError(f"{name} {version} changed after release "
                         f"(hash {sha(text)[:8]}, locked {want[:8]}). Make a new version instead.")
    return version, want[:8], text


def lock_versions(name, live, root=ROOT):
    """Record each version's hash. Run once when a version is released."""
    folder = os.path.join(root, "prompts", name)
    vs = {f[:-4]: sha(read(os.path.join(folder, f))) for f in sorted(os.listdir(folder)) if f.endswith(".txt")}
    with open(os.path.join(root, "prompts.lock.json"), "w") as f:
        json.dump({name: {"live": live, "versions": vs}}, f, indent=1)
