# Swap the five F1 help pictures into copies of the asset files.
import os
import UnityPy
from PIL import Image
from UnityPy.enums import TextureFormat

GAME = r"E:\T File\Bastard Bonds\BB_Data"
BACKUP = r"E:\T File\BB_WORK\backup"
BUILD = r"E:\T File\BB_WORK\build"
PNG = r"E:\T File\BB_WORK\patch\_help\out"

JOBS = {
    "sharedassets4.assets": [
        "Help_MapExplorer",
        "Help_InventoryManage",
        "Help_Stronghold",
        "Help_BaseManage",
    ],
    "sharedassets5.assets": [
        "Help_Overworld",
    ],
}


def main():
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(BACKUP, exist_ok=True)
    for name, textures in JOBS.items():
        src = os.path.join(GAME, name)
        backed = os.path.join(BACKUP, name)
        if not os.path.exists(backed):
            with open(src, "rb") as f, open(backed, "wb") as g:
                g.write(f.read())
            print("backed up", name)
        env = UnityPy.load(backed)
        wanted = set(textures)
        for obj in env.objects:
            if obj.type.name != "Texture2D":
                continue
            data = obj.read()
            if data.m_Name not in wanted:
                continue
            img = Image.open(os.path.join(PNG, data.m_Name + ".png")).convert("RGBA")
            data.set_image(img, target_format=TextureFormat.RGBA32)
            data.save()
            wanted.remove(data.m_Name)
            print("replaced", data.m_Name, data.m_TextureFormat)
        if wanted:
            raise SystemExit("missing " + ", ".join(wanted))
        out = os.path.join(BUILD, name)
        with open(out, "wb") as f:
            f.write(env.file.save())
        print("wrote", out, os.path.getsize(out))


if __name__ == "__main__":
    main()
