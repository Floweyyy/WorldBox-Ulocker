import base64
import hashlib
import json
import os
import pathlib
import re
import shutil
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SAVE_DIR = pathlib.Path(os.path.expandvars(r"%UserProfile%\AppData\LocalLow\mkarpenko\WorldBox"))
STEAM_DATA_DIR = pathlib.Path(r"C:\Program Files (x86)\Steam\steamapps\common\worldbox\worldbox_Data")

# Chaves derivadas do metodo Toolbox.encode / Toolbox.decode e Encryption do WorldBox
PASS_PHRASE = b"WorldboxIsAwesome555"
INIT_VECTOR = b"sayHiIfUReadThis"


def derive_key_pdb(password_bytes: bytes, key_len: int = 32) -> bytes:
    """Replica System.Security.Cryptography.PasswordDeriveBytes(password, null) (SHA1, 100 iteracoes)."""
    base = password_bytes
    for _ in range(99):
        base = hashlib.sha1(base).digest()
    out = bytearray(hashlib.sha1(base).digest())
    counter = 1
    while len(out) < key_len:
        out.extend(hashlib.sha1(str(counter).encode("ascii") + base).digest())
        counter += 1
    return bytes(out[:key_len])


KEY = derive_key_pdb(PASS_PHRASE, 32)


def decode_worldbox(encoded_text: str) -> str:
    ciphertext = base64.b64decode(encoded_text)
    decryptor = Cipher(algorithms.AES(KEY), modes.CBC(INIT_VECTOR)).decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()
    return plaintext.decode("utf-8")


def encode_worldbox(plain_text: str) -> str:
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plain_text.encode("utf-8")) + padder.finalize()
    encryptor = Cipher(algorithms.AES(KEY), modes.CBC(INIT_VECTOR)).encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(ciphertext).decode("ascii")


def step1_list_and_locate_files() -> pathlib.Path:
    print(f"=== [Etapa 1] Listando arquivos em: {SAVE_DIR} ===")
    all_files = sorted(p for p in SAVE_DIR.rglob("*") if p.is_file())
    target_files = [
        p
        for p in all_files
        if p.suffix.lower() in {".json", ".wbax", ".wbox", ".meta", ".vdf", ".s3db"}
        or p.parent == SAVE_DIR
    ]

    for p in target_files:
        rel = p.relative_to(SAVE_DIR)
        print(f"  - {rel} ({p.stat().st_size} bytes)")

    progress_file = None
    print("\nVerificando arquivos de configuracao/progresso quanto a chave 'achievements':")
    for name in ("stats.json", "worldboxData", "worldboxProgress"):
        candidate = SAVE_DIR / name
        if not candidate.exists():
            continue
        raw = candidate.read_text(encoding="utf-8")
        try:
            decoded = raw if raw.lstrip().startswith("{") else decode_worldbox(raw)
            data = json.loads(decoded)
        except Exception as exc:
            print(f"  - {name}: erro ao ler/decodificar ({exc})")
            continue

        if "achievements" in data:
            ach_count = len(data["achievements"]) if isinstance(data["achievements"], list) else 0
            print(f"  - {name}: contem chave 'achievements' ({ach_count} itens)")
            if name == "worldboxProgress" or (progress_file is None and ach_count > 0):
                progress_file = candidate
        else:
            print(f"  - {name}: nao contem chave 'achievements'")

    if progress_file is None:
        raise FileNotFoundError("Nao foi possivel localizar o arquivo com a chave 'achievements'.")

    print(f"\nArquivo de progresso principal identificado: {progress_file}")
    return progress_file


def step2_verify_achievement_id() -> str:
    print(f"\n=== [Etapa 2] Varredura nos arquivos da Steam em: {STEAM_DATA_DIR} ===")
    scan_targets = [
        STEAM_DATA_DIR / "Managed" / "Assembly-CSharp.dll",
        STEAM_DATA_DIR / "Managed" / "strings.dll",
        STEAM_DATA_DIR / "globalgamemanagers",
    ]
    terms = ["not_on_my_watch", "achievementNotOnMyWatch", "being_suspicious"]

    found_camel_id = False
    for file_path in scan_targets:
        if not file_path.exists():
            continue
        blob = file_path.read_bytes()
        rel = file_path.relative_to(STEAM_DATA_DIR)
        for term in terms:
            ascii_hits = len(re.findall(term.encode("ascii"), blob, re.IGNORECASE))
            utf16_hits = len(re.findall(term.encode("utf-16le"), blob, re.IGNORECASE))
            if ascii_hits or utf16_hits:
                print(f"  - {rel}: '{term}' (ascii={ascii_hits}, utf16={utf16_hits})")
                if term == "achievementNotOnMyWatch":
                    found_camel_id = True

    if not found_camel_id:
        raise RuntimeError("ID 'achievementNotOnMyWatch' nao encontrado nos arquivos do jogo.")

    achievement_id = "achievementNotOnMyWatch"
    print(
        f"ID exato confirmado para 'Not on My Watch' (not_on_my_watch) na v0.50+: {achievement_id}"
    )
    return achievement_id


def step3_backup(progress_file: pathlib.Path) -> pathlib.Path:
    print("\n=== [Etapa 3] Criando backup do arquivo de progresso original ===")
    backup_file = progress_file.with_name(progress_file.name + ".bak")
    if not backup_file.exists():
        shutil.copy2(progress_file, backup_file)
        print(f"Backup criado em: {backup_file}")
    else:
        print(f"Backup original ja existe em: {backup_file} (preservado)")
    return backup_file


def step4_and_5_update_and_verify(progress_file: pathlib.Path, achievement_id: str) -> None:
    print("\n=== [Etapa 4] Parseando JSON, inserindo conquista e salvando em UTF-8 ===")
    raw_encrypted = progress_file.read_text(encoding="utf-8")
    decoded_json = decode_worldbox(raw_encrypted)
    data = json.loads(decoded_json)

    achievements = data.get("achievements")
    if not isinstance(achievements, list):
        raise ValueError("A chave 'achievements' nao e uma lista valida.")

    if achievement_id in achievements:
        print(f"Conquista '{achievement_id}' ja esta desbloqueada no arquivo.")
    else:
        achievements.append(achievement_id)
        print(f"Conquista '{achievement_id}' inserida no array 'achievements'.")

    # Preserva exatamente a formatacao do Newtonsoft.Json (indent=2, CRLF, sem newline final, UTF-8 sem BOM)
    updated_json = json.dumps(data, indent=2, ensure_ascii=False).replace("\n", "\r\n")
    updated_encrypted = encode_worldbox(updated_json)
    progress_file.write_text(updated_encrypted, encoding="utf-8", newline="")

    print("\n=== [Etapa 5] Confirmacao ===")
    verified_json = decode_worldbox(progress_file.read_text(encoding="utf-8"))
    verified_data = json.loads(verified_json)
    snippet = json.dumps({"achievements": verified_data["achievements"]}, indent=2, ensure_ascii=False)
    print(f"Caminho do arquivo modificado: {progress_file}")
    print("Trecho do JSON atualizado:")
    print(snippet)


def main() -> None:
    progress_file = step1_list_and_locate_files()
    achievement_id = step2_verify_achievement_id()
    step3_backup(progress_file)
    step4_and_5_update_and_verify(progress_file, achievement_id)


if __name__ == "__main__":
    main()
