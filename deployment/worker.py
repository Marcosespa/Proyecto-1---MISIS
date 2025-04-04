import os
import time

NFS_PATH = "/mnt/nfs/files"

print("🟢 Worker iniciado, observando:", NFS_PATH)

while True:
    for filename in os.listdir(NFS_PATH):
        filepath = os.path.join(NFS_PATH, filename)
        if os.path.isfile(filepath) and not filename.endswith(".done"):
            print(f"Procesando archivo: {filename}")
            time.sleep(2)
            new_name = filepath + ".done"
            os.rename(filepath, new_name)
            print(f"✅ Procesado: {new_name}")
    time.sleep(5)
