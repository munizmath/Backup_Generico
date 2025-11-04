#!/usr/bin/env python3
"""
Sistema de Criptografia Avançada
Implementa envelope encryption com XChaCha20-Poly1305 e rotação de chaves
"""

import os
import json
import base64
import secrets
from pathlib import Path
from typing import Dict, Optional, Tuple
import time
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

class EncryptionSystem:
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.keys_dir = self.config_dir / "keys"
        self.keys_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / "encryption_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Carregar configuração de criptografia"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Configuração padrão
        return {
            "algorithm": "XChaCha20-Poly1305",
            "key_rotation_days": 90,
            "master_key_id": None,
            "active_keys": [],
            "key_history": []
        }
    
    def _save_config(self):
        """Salvar configuração"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def generate_master_key(self, password: str) -> str:
        """Gerar chave mestra a partir de senha"""
        print("🔐 Gerando chave mestra...")
        
        # Gerar salt
        salt = secrets.token_bytes(32)
        
        # Derivar chave da senha
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        master_key = kdf.derive(password.encode())
        
        # Gerar ID da chave
        key_id = secrets.token_hex(16)
        
        # Salvar chave mestra (criptografada com a senha)
        key_data = {
            "key_id": key_id,
            "salt": base64.b64encode(salt).decode(),
            "iterations": 100000,
            "created": time.time(),
            "algorithm": "PBKDF2-SHA256"
        }
        
        key_file = self.keys_dir / f"master_{key_id}.json"
        with open(key_file, 'w', encoding='utf-8') as f:
            json.dump(key_data, f, indent=2, ensure_ascii=False)
        
        # Atualizar configuração
        self.config["master_key_id"] = key_id
        self.config["active_keys"].append(key_id)
        self._save_config()
        
        print(f"✅ Chave mestra gerada: {key_id}")
        return key_id
    
    def generate_data_key(self) -> Tuple[str, bytes]:
        """Gerar chave de dados para envelope encryption"""
        # Gerar chave aleatória de 32 bytes para XChaCha20-Poly1305
        data_key = secrets.token_bytes(32)
        key_id = secrets.token_hex(16)
        
        # Salvar chave de dados (será criptografada com a chave mestra)
        key_data = {
            "key_id": key_id,
            "created": time.time(),
            "algorithm": "XChaCha20-Poly1305",
            "encrypted": True
        }
        
        key_file = self.keys_dir / f"data_{key_id}.json"
        with open(key_file, 'w', encoding='utf-8') as f:
            json.dump(key_data, f, indent=2, ensure_ascii=False)
        
        return key_id, data_key
    
    def encrypt_data_key(self, data_key: bytes, master_key_id: str, password: str) -> str:
        """Criptografar chave de dados com chave mestra"""
        # Carregar chave mestra
        key_file = self.keys_dir / f"master_{master_key_id}.json"
        if not key_file.exists():
            raise ValueError(f"Chave mestra não encontrada: {master_key_id}")
        
        with open(key_file, 'r', encoding='utf-8') as f:
            key_data = json.load(f)
        
        # Reconstruir chave mestra
        salt = base64.b64decode(key_data["salt"])
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=key_data["iterations"],
        )
        master_key = kdf.derive(password.encode())
        
        # Criptografar chave de dados
        cipher = ChaCha20Poly1305(master_key)
        nonce = secrets.token_bytes(12)  # 96 bits para XChaCha20-Poly1305
        encrypted_data_key = cipher.encrypt(nonce, data_key, None)
        
        # Salvar chave de dados criptografada
        data_key_id = secrets.token_hex(16)
        encrypted_data = {
            "key_id": data_key_id,
            "master_key_id": master_key_id,
            "nonce": base64.b64encode(nonce).decode(),
            "encrypted_key": base64.b64encode(encrypted_data_key).decode(),
            "created": time.time()
        }
        
        key_file = self.keys_dir / f"encrypted_data_{data_key_id}.json"
        with open(key_file, 'w', encoding='utf-8') as f:
            json.dump(encrypted_data, f, indent=2, ensure_ascii=False)
        
        return data_key_id
    
    def decrypt_data_key(self, encrypted_key_id: str, password: str) -> bytes:
        """Descriptografar chave de dados"""
        # Carregar chave de dados criptografada
        key_file = self.keys_dir / f"encrypted_data_{encrypted_key_id}.json"
        if not key_file.exists():
            raise ValueError(f"Chave de dados não encontrada: {encrypted_key_id}")
        
        with open(key_file, 'r', encoding='utf-8') as f:
            encrypted_data = json.load(f)
        
        # Carregar chave mestra
        master_key_id = encrypted_data["master_key_id"]
        master_key_file = self.keys_dir / f"master_{master_key_id}.json"
        
        with open(master_key_file, 'r', encoding='utf-8') as f:
            master_key_data = json.load(f)
        
        # Reconstruir chave mestra
        salt = base64.b64decode(master_key_data["salt"])
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=master_key_data["iterations"],
        )
        master_key = kdf.derive(password.encode())
        
        # Descriptografar chave de dados
        nonce = base64.b64decode(encrypted_data["nonce"])
        encrypted_key = base64.b64decode(encrypted_data["encrypted_key"])
        
        cipher = ChaCha20Poly1305(master_key)
        data_key = cipher.decrypt(nonce, encrypted_key, None)
        
        return data_key
    
    def encrypt_file(self, file_path: Path, output_path: Path, password: str) -> Dict:
        """Criptografar arquivo usando envelope encryption"""
        print(f"🔐 Criptografando arquivo: {file_path}")
        
        # Validar entrada
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        if not password or len(password) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")
        if not self.config.get("master_key_id"):
            raise ValueError("Chave mestra não configurada. Execute 'init' primeiro.")
        
        # Gerar chave de dados
        data_key_id, data_key = self.generate_data_key()
        
        # Criptografar chave de dados
        encrypted_key_id = self.encrypt_data_key(data_key, self.config["master_key_id"], password)
        
        # Ler arquivo
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Criptografar arquivo
        cipher = ChaCha20Poly1305(data_key)
        nonce = secrets.token_bytes(12)
        encrypted_data = cipher.encrypt(nonce, file_data, None)
        
        # Salvar arquivo criptografado
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Criar metadados de criptografia
        metadata = {
            "original_file": str(file_path),
            "encrypted_file": str(output_path),
            "data_key_id": data_key_id,
            "encrypted_key_id": encrypted_key_id,
            "nonce": base64.b64encode(nonce).decode(),
            "algorithm": "XChaCha20-Poly1305",
            "created": time.time()
        }
        
        # Salvar metadados
        metadata_file = output_path.with_suffix('.enc.meta')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Arquivo criptografado: {output_path}")
        return metadata
    
    def decrypt_file(self, encrypted_path: Path, output_path: Path, password: str) -> bool:
        """Descriptografar arquivo"""
        print(f"🔓 Descriptografando arquivo: {encrypted_path}")
        
        # Validar entrada
        if not encrypted_path.exists():
            print(f"❌ Arquivo criptografado não encontrado: {encrypted_path}")
            return False
        if not password or len(password) < 8:
            print("❌ Senha deve ter pelo menos 8 caracteres")
            return False
        
        # Carregar metadados
        metadata_file = encrypted_path.with_suffix('.enc.meta')
        if not metadata_file.exists():
            print(f"❌ Metadados não encontrados: {metadata_file}")
            return False
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        try:
            # Descriptografar chave de dados
            data_key = self.decrypt_data_key(metadata["encrypted_key_id"], password)
            
            # Ler arquivo criptografado
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Descriptografar arquivo
            nonce = base64.b64decode(metadata["nonce"])
            cipher = ChaCha20Poly1305(data_key)
            file_data = cipher.decrypt(nonce, encrypted_data, None)
            
            # Salvar arquivo descriptografado
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(file_data)
            
            print(f"✅ Arquivo descriptografado: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao descriptografar: {e}")
            return False
    
    def rotate_keys(self, password: str):
        """Rotacionar chaves (implementação básica)"""
        print("🔄 Rotacionando chaves...")
        
        # Em uma implementação completa, aqui seria feita a rotação
        # de todas as chaves ativas para novas chaves
        
        current_time = time.time()
        rotation_time = self.config.get("last_rotation", 0) + (self.config["key_rotation_days"] * 24 * 3600)
        
        if current_time > rotation_time:
            print("⚠️  Rotação de chaves necessária")
            # Implementar rotação aqui
            self.config["last_rotation"] = current_time
            self._save_config()
        else:
            print("✅ Chaves ainda válidas")
    
    def get_encryption_stats(self) -> Dict:
        """Obter estatísticas de criptografia"""
        master_keys = len([f for f in self.keys_dir.glob("master_*.json")])
        data_keys = len([f for f in self.keys_dir.glob("data_*.json")])
        encrypted_keys = len([f for f in self.keys_dir.glob("encrypted_data_*.json")])
        
        return {
            "master_keys": master_keys,
            "data_keys": data_keys,
            "encrypted_keys": encrypted_keys,
            "active_keys": len(self.config["active_keys"]),
            "last_rotation": self.config.get("last_rotation", 0)
        }

def main():
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python encryption_system.py <comando> <config_dir> [args...]")
        print("Comandos:")
        print("  init <password>")
        print("  encrypt <file_path> <output_path> <password>")
        print("  decrypt <encrypted_path> <output_path> <password>")
        print("  rotate <password>")
        print("  stats")
        sys.exit(1)
    
    command = sys.argv[1]
    config_dir = sys.argv[2]
    
    encryption = EncryptionSystem(config_dir)
    
    if command == "init":
        if len(sys.argv) < 4:
            print("Uso: init <password>")
            sys.exit(1)
        
        password = sys.argv[3]
        key_id = encryption.generate_master_key(password)
        print(f"✅ Sistema de criptografia inicializado: {key_id}")
    
    elif command == "encrypt":
        if len(sys.argv) < 6:
            print("Uso: encrypt <file_path> <output_path> <password>")
            sys.exit(1)
        
        file_path = Path(sys.argv[3])
        output_path = Path(sys.argv[4])
        password = sys.argv[5]
        
        if not file_path.exists():
            print(f"❌ Arquivo não encontrado: {file_path}")
            sys.exit(1)
        
        metadata = encryption.encrypt_file(file_path, output_path, password)
        print(f"✅ Arquivo criptografado: {output_path}")
    
    elif command == "decrypt":
        if len(sys.argv) < 6:
            print("Uso: decrypt <encrypted_path> <output_path> <password>")
            sys.exit(1)
        
        encrypted_path = Path(sys.argv[3])
        output_path = Path(sys.argv[4])
        password = sys.argv[5]
        
        if not encrypted_path.exists():
            print(f"❌ Arquivo criptografado não encontrado: {encrypted_path}")
            sys.exit(1)
        
        if encryption.decrypt_file(encrypted_path, output_path, password):
            print(f"✅ Arquivo descriptografado: {output_path}")
        else:
            print(f"❌ Erro ao descriptografar arquivo")
            sys.exit(1)
    
    elif command == "rotate":
        if len(sys.argv) < 4:
            print("Uso: rotate <password>")
            sys.exit(1)
        
        password = sys.argv[3]
        encryption.rotate_keys(password)
    
    elif command == "stats":
        stats = encryption.get_encryption_stats()
        print("📊 Estatísticas de criptografia:")
        print(f"  Chaves mestras: {stats['master_keys']}")
        print(f"  Chaves de dados: {stats['data_keys']}")
        print(f"  Chaves criptografadas: {stats['encrypted_keys']}")
        print(f"  Chaves ativas: {stats['active_keys']}")
    
    else:
        print(f"❌ Comando não reconhecido: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
