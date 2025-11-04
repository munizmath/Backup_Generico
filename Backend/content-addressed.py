#!/usr/bin/env python3
"""
Sistema de Armazenamento Content-Addressed
Implementa chunking variável, deduplicação e índices otimizados
"""

import os
import hashlib
import json
import struct
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import zlib
import time
from logging_config import get_logger

class ContentAddressedStorage:
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)
        self.chunks_dir = self.storage_dir / "chunks"
        self.manifests_dir = self.storage_dir / "manifests"
        self.index_file = self.storage_dir / "index.json"
        self.logger = get_logger("content_addressed")
        
        # Criar diretórios se não existirem
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        self.manifests_dir.mkdir(parents=True, exist_ok=True)
        
        # Carregar índice
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """Carregar índice de chunks"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"chunks": {}, "manifests": {}}
    
    def _save_index(self):
        """Salvar índice de chunks"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def _calculate_chunk_hash(self, data: bytes) -> str:
        """Calcular hash BLAKE3 do chunk"""
        # Usar SHA-256 como fallback (BLAKE3 não está disponível por padrão)
        return hashlib.sha256(data).hexdigest()
    
    def _rabin_chunking(self, data: bytes, target_size: int = 8192) -> List[bytes]:
        """
        Chunking variável usando algoritmo Rabin
        Implementação simplificada para demonstração
        """
        chunks = []
        chunk_size = target_size
        min_size = target_size // 2
        max_size = target_size * 2
        
        i = 0
        while i < len(data):
            # Determinar tamanho do próximo chunk
            remaining = len(data) - i
            if remaining <= min_size:
                # Último chunk - pegar tudo que resta
                chunk_size = remaining
            elif remaining <= max_size:
                # Chunk médio
                chunk_size = remaining
            else:
                # Chunk normal - usar tamanho alvo
                chunk_size = min(target_size, remaining)
            
            # Extrair chunk
            chunk = data[i:i + chunk_size]
            chunks.append(chunk)
            i += chunk_size
        
        return chunks
    
    def _compress_chunk(self, data: bytes) -> bytes:
        """Comprimir chunk usando zlib"""
        return zlib.compress(data, level=6)
    
    def _decompress_chunk(self, data: bytes) -> bytes:
        """Descomprimir chunk"""
        return zlib.decompress(data)
    
    def store_file(self, file_path: Path, manifest_id: str) -> Dict:
        """
        Armazenar arquivo usando content-addressed storage
        """
        self.logger.info(f"📦 Armazenando arquivo: {file_path}")
        
        # Validar entrada
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        if not manifest_id or not manifest_id.strip():
            raise ValueError("manifest_id não pode ser vazio")
        
        # Ler arquivo
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Chunking do arquivo
        chunks = self._rabin_chunking(file_data)
        self.logger.info(f"🔪 Arquivo dividido em {len(chunks)} chunks")
        
        # Armazenar chunks
        chunk_hashes = []
        original_size = 0  # Tamanho original de todos os chunks
        unique_stored_size = 0  # Tamanho comprimido dos chunks únicos armazenados
        
        for i, chunk in enumerate(chunks):
            # Calcular hash do chunk
            chunk_hash = self._calculate_chunk_hash(chunk)
            
            # Sempre contar o tamanho original
            original_size += len(chunk)
            chunk_hashes.append(chunk_hash)
            
            # Verificar se chunk já existe
            if chunk_hash in self.index["chunks"]:
                self.logger.debug(f"♻️  Chunk {i+1} já existe (deduplicação)")
                # Usar tamanho comprimido já armazenado
                unique_stored_size += self.index["chunks"][chunk_hash]["compressed_size"]
                continue
            
            # Comprimir chunk
            compressed_chunk = self._compress_chunk(chunk)
            unique_stored_size += len(compressed_chunk)
            
            # Salvar chunk
            chunk_file = self.chunks_dir / f"{chunk_hash}.chunk"
            with open(chunk_file, 'wb') as f:
                f.write(compressed_chunk)
            
            # Atualizar índice
            self.index["chunks"][chunk_hash] = {
                "size": len(chunk),
                "compressed_size": len(compressed_chunk),
                "file": str(chunk_file),
                "created": time.time()
            }
            
            self.logger.debug(f"💾 Chunk {i+1} armazenado: {chunk_hash[:8]}...")
        
        # Calcular taxa de deduplicação corretamente
        # Ratio = (tamanho original - tamanho armazenado) / tamanho original
        deduplication_ratio = max(0, min(1, (original_size - unique_stored_size) / original_size)) if original_size > 0 else 0
        
        # Criar manifesto
        manifest = {
            "id": manifest_id,
            "file_path": str(file_path),
            "file_size": len(file_data),
            "chunk_count": len(chunks),
            "chunk_hashes": chunk_hashes,
            "created": time.time(),
            "deduplication_ratio": deduplication_ratio,
            "original_size": original_size,
            "stored_size": unique_stored_size
        }
        
        # Salvar manifesto
        manifest_file = self.manifests_dir / f"{manifest_id}.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # Atualizar índice
        self.index["manifests"][manifest_id] = {
            "file": str(manifest_file),
            "created": time.time()
        }
        
        # Salvar índice
        self._save_index()
        
        self.logger.info(f"✅ Arquivo armazenado com {manifest['deduplication_ratio']:.1%} de deduplicação")
        return manifest
    
    def restore_file(self, manifest_id: str, output_path: Path) -> bool:
        """
        Restaurar arquivo a partir do content-addressed storage
        """
        self.logger.info(f"📤 Restaurando arquivo: {manifest_id}")
        
        # Validar entrada
        if not manifest_id or not manifest_id.strip():
            self.logger.error("manifest_id não pode ser vazio")
            return False
        
        # Carregar manifesto
        if manifest_id not in self.index["manifests"]:
            self.logger.error(f"❌ Manifesto não encontrado: {manifest_id}")
            return False
        
        manifest_file = Path(self.index["manifests"][manifest_id]["file"])
        if not manifest_file.exists():
            self.logger.error(f"❌ Arquivo de manifesto não encontrado: {manifest_file}")
            return False
        
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Restaurar chunks
        file_data = b""
        for i, chunk_hash in enumerate(manifest["chunk_hashes"]):
            if chunk_hash not in self.index["chunks"]:
                self.logger.error(f"❌ Chunk não encontrado: {chunk_hash}")
                return False
            
            chunk_file = Path(self.index["chunks"][chunk_hash]["file"])
            if not chunk_file.exists():
                self.logger.error(f"❌ Arquivo de chunk não encontrado: {chunk_file}")
                return False
            
            # Ler e descomprimir chunk
            with open(chunk_file, 'rb') as f:
                compressed_data = f.read()
            
            chunk_data = self._decompress_chunk(compressed_data)
            file_data += chunk_data
            
            self.logger.debug(f"🔧 Chunk {i+1} restaurado: {chunk_hash[:8]}...")
        
        # Salvar arquivo restaurado
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(file_data)
        
        self.logger.info(f"✅ Arquivo restaurado: {output_path}")
        return True
    
    def list_manifests(self) -> List[Dict]:
        """Listar todos os manifestos"""
        manifests = []
        for manifest_id, info in self.index["manifests"].items():
            manifest_file = Path(info["file"])
            if manifest_file.exists():
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                manifests.append(manifest)
        return manifests
    
    def get_storage_stats(self) -> Dict:
        """Obter estatísticas do armazenamento"""
        total_chunks = len(self.index["chunks"])
        total_manifests = len(self.index["manifests"])
        
        total_size = 0
        total_compressed_size = 0
        
        for chunk_info in self.index["chunks"].values():
            total_size += chunk_info["size"]
            total_compressed_size += chunk_info["compressed_size"]
        
        return {
            "total_chunks": total_chunks,
            "total_manifests": total_manifests,
            "total_size": total_size,
            "total_compressed_size": total_compressed_size,
            "compression_ratio": (total_size - total_compressed_size) / total_size if total_size > 0 else 0,
            "storage_dir": str(self.storage_dir)
        }
    
    def cleanup_orphaned_chunks(self):
        """Limpar chunks órfãos (não referenciados por nenhum manifesto)"""
        self.logger.info("🧹 Limpando chunks órfãos...")
        
        # Coletar todos os chunks referenciados
        referenced_chunks = set()
        for manifest_id, info in self.index["manifests"].items():
            manifest_file = Path(info["file"])
            if manifest_file.exists():
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                referenced_chunks.update(manifest["chunk_hashes"])
        
        # Remover chunks não referenciados
        removed_count = 0
        for chunk_hash, chunk_info in list(self.index["chunks"].items()):
            if chunk_hash not in referenced_chunks:
                chunk_file = Path(chunk_info["file"])
                if chunk_file.exists():
                    chunk_file.unlink()
                del self.index["chunks"][chunk_hash]
                removed_count += 1
        
        self._save_index()
        self.logger.info(f"✅ {removed_count} chunks órfãos removidos")

def main():
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python content-addressed.py <comando> <storage_dir> [args...]")
        print("Comandos:")
        print("  store <file_path> <manifest_id>")
        print("  restore <manifest_id> <output_path>")
        print("  list")
        print("  stats")
        print("  cleanup")
        sys.exit(1)
    
    command = sys.argv[1]
    storage_dir = sys.argv[2]
    
    storage = ContentAddressedStorage(storage_dir)
    
    if command == "store":
        if len(sys.argv) < 5:
            print("Uso: store <file_path> <manifest_id>")
            sys.exit(1)
        
        file_path = Path(sys.argv[3])
        manifest_id = sys.argv[4]
        
        if not file_path.exists():
            print(f"❌ Arquivo não encontrado: {file_path}")
            sys.exit(1)
        
        manifest = storage.store_file(file_path, manifest_id)
        print(f"✅ Arquivo armazenado: {manifest_id}")
    
    elif command == "restore":
        if len(sys.argv) < 5:
            print("Uso: restore <manifest_id> <output_path>")
            sys.exit(1)
        
        manifest_id = sys.argv[3]
        output_path = Path(sys.argv[4])
        
        if storage.restore_file(manifest_id, output_path):
            print(f"✅ Arquivo restaurado: {output_path}")
        else:
            print(f"❌ Erro ao restaurar arquivo")
            sys.exit(1)
    
    elif command == "list":
        manifests = storage.list_manifests()
        print(f"📋 {len(manifests)} manifestos encontrados:")
        for manifest in manifests:
            print(f"  {manifest['id']}: {manifest['file_path']} ({manifest['file_size']} bytes)")
    
    elif command == "stats":
        stats = storage.get_storage_stats()
        print("📊 Estatísticas do armazenamento:")
        print(f"  Chunks: {stats['total_chunks']}")
        print(f"  Manifestos: {stats['total_manifests']}")
        print(f"  Tamanho original: {stats['total_size']:,} bytes")
        print(f"  Tamanho comprimido: {stats['total_compressed_size']:,} bytes")
        print(f"  Taxa de compressão: {stats['compression_ratio']:.1%}")
    
    elif command == "cleanup":
        storage.cleanup_orphaned_chunks()
    
    else:
        print(f"❌ Comando não reconhecido: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
