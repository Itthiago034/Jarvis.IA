"""
Voice Verification Module usando embeddings de voz
Verifica se a voz é do usuário autorizado (Thiago) ou de um desconhecido.

Versão compatível com Python 3.14+ (sem webrtcvad)
"""

import os
import json
import logging
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Diretório para armazenar voice prints
VOICE_DATA_DIR = Path(__file__).parent.parent.parent / "config" / "voice_profiles"


@dataclass
class VerificationResult:
    """Resultado da verificação de voz."""
    is_authorized: bool
    confidence: float  # 0.0 a 1.0
    user_name: Optional[str]
    message: str


class VoiceVerifier:
    """
    Verificador de voz usando embeddings de áudio.
    Compara características de voz para identificar o usuário.
    """
    
    # Threshold de similaridade para considerar mesma pessoa
    SIMILARITY_THRESHOLD = 0.75  # Ajustável (0.7-0.85 recomendado)
    
    def __init__(self, voice_data_dir: Path = VOICE_DATA_DIR):
        self.voice_data_dir = voice_data_dir
        self.voice_data_dir.mkdir(parents=True, exist_ok=True)
        
        self.encoder = None
        self.authorized_embeddings: dict[str, np.ndarray] = {}
        self._initialized = False
        
    def _lazy_init(self):
        """Inicializa o encoder apenas quando necessário (lazy loading)."""
        if self._initialized:
            return
            
        try:
            # Tenta usar resemblyzer primeiro
            try:
                from resemblyzer import VoiceEncoder
                self.encoder = VoiceEncoder()
                self._use_resemblyzer = True
                logger.info("Usando Resemblyzer para verificação de voz")
            except ImportError:
                # Fallback para implementação simplificada
                self._use_resemblyzer = False
                logger.info("Usando implementação simplificada (MFCC-based)")
            
            self._load_authorized_voices()
            self._initialized = True
            logger.info("VoiceVerifier inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar VoiceVerifier: {e}")
            raise
    
    def _extract_mfcc_embedding(self, audio: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
        """
        Extrai embedding baseado em MFCC (fallback quando resemblyzer não funciona).
        """
        import librosa
        
        # Normaliza áudio
        if audio.max() > 1.0:
            audio = audio / 32768.0
        
        # Extrai MFCCs
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        
        # Estatísticas dos MFCCs como embedding
        mfcc_mean = np.mean(mfccs, axis=1)
        mfcc_std = np.std(mfccs, axis=1)
        
        # Delta MFCCs
        delta_mfccs = librosa.feature.delta(mfccs)
        delta_mean = np.mean(delta_mfccs, axis=1)
        
        # Combina em um embedding
        embedding = np.concatenate([mfcc_mean, mfcc_std, delta_mean])
        
        # Normaliza
        embedding = embedding / (np.linalg.norm(embedding) + 1e-10)
        
        return embedding
    
    def _get_embedding(self, audio: np.ndarray) -> np.ndarray:
        """Obtém embedding do áudio usando o método disponível."""
        if self._use_resemblyzer:
            return self.encoder.embed_utterance(audio)
        else:
            return self._extract_mfcc_embedding(audio)
    
    def _load_authorized_voices(self):
        """Carrega voice prints salvos dos usuários autorizados."""
        profiles_file = self.voice_data_dir / "profiles.json"
        
        if not profiles_file.exists():
            logger.info("Nenhum perfil de voz encontrado. Use enroll_user() para cadastrar.")
            return
        
        try:
            with open(profiles_file, 'r') as f:
                profiles = json.load(f)
            
            for user_name, data in profiles.items():
                embedding_file = self.voice_data_dir / f"{user_name}_embedding.npy"
                if embedding_file.exists():
                    self.authorized_embeddings[user_name] = np.load(embedding_file)
                    logger.info(f"Voice print carregado para: {user_name}")
                    
        except Exception as e:
            logger.error(f"Erro ao carregar perfis de voz: {e}")
    
    def enroll_user(self, user_name: str, audio_samples: list[np.ndarray]) -> bool:
        """
        Cadastra um novo usuário com amostras de áudio.
        
        Args:
            user_name: Nome do usuário (ex: "Thiago")
            audio_samples: Lista de arrays numpy com áudio (16kHz)
            
        Returns:
            True se cadastro foi bem sucedido
        """
        self._lazy_init()
        
        if len(audio_samples) < 3:
            logger.warning("Recomendado pelo menos 3 amostras de áudio para cadastro preciso")
        
        try:
            # Gera embeddings para cada amostra
            embeddings = []
            for audio in audio_samples:
                emb = self._get_embedding(audio)
                embeddings.append(emb)
            
            # Média dos embeddings para representação robusta
            mean_embedding = np.mean(embeddings, axis=0)
            
            # Salva embedding
            embedding_file = self.voice_data_dir / f"{user_name}_embedding.npy"
            np.save(embedding_file, mean_embedding)
            
            # Atualiza profiles.json
            profiles_file = self.voice_data_dir / "profiles.json"
            profiles = {}
            if profiles_file.exists():
                with open(profiles_file, 'r') as f:
                    profiles = json.load(f)
            
            profiles[user_name] = {
                "enrolled_at": str(np.datetime64('now')),
                "samples_count": len(audio_samples),
                "threshold": self.SIMILARITY_THRESHOLD
            }
            
            with open(profiles_file, 'w') as f:
                json.dump(profiles, f, indent=2)
            
            # Atualiza cache em memória
            self.authorized_embeddings[user_name] = mean_embedding
            
            logger.info(f"Usuário '{user_name}' cadastrado com {len(audio_samples)} amostras")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao cadastrar usuário: {e}")
            return False
    
    def enroll_from_files(self, user_name: str, audio_files: list[str]) -> bool:
        """
        Cadastra usuário a partir de arquivos de áudio.
        
        Args:
            user_name: Nome do usuário
            audio_files: Lista de caminhos para arquivos WAV (16kHz)
        """
        self._lazy_init()
        
        audio_samples = []
        for file_path in audio_files:
            try:
                wav = self._load_audio_file(file_path)
                audio_samples.append(wav)
            except Exception as e:
                logger.warning(f"Erro ao processar {file_path}: {e}")
        
        if not audio_samples:
            logger.error("Nenhuma amostra de áudio válida encontrada")
            return False
            
        return self.enroll_user(user_name, audio_samples)
    
    def _load_audio_file(self, file_path: str, target_sr: int = 16000) -> np.ndarray:
        """Carrega arquivo de áudio e converte para 16kHz mono."""
        import librosa
        audio, sr = librosa.load(file_path, sr=target_sr, mono=True)
        return audio
    
    def verify(self, audio: np.ndarray) -> VerificationResult:
        """
        Verifica se o áudio pertence a um usuário autorizado.
        
        Args:
            audio: Array numpy com áudio (16kHz)
            
        Returns:
            VerificationResult com status da verificação
        """
        self._lazy_init()
        
        if not self.authorized_embeddings:
            return VerificationResult(
                is_authorized=False,
                confidence=0.0,
                user_name=None,
                message="Nenhum usuário cadastrado. Configure seu perfil de voz primeiro."
            )
        
        try:
            # Gera embedding do áudio atual
            current_embedding = self._get_embedding(audio)
            
            # Compara com todos os usuários autorizados
            best_match = None
            best_similarity = 0.0
            
            for user_name, authorized_emb in self.authorized_embeddings.items():
                # Similaridade do cosseno
                similarity = np.dot(current_embedding, authorized_emb) / (
                    np.linalg.norm(current_embedding) * np.linalg.norm(authorized_emb)
                )
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = user_name
            
            # Verifica se passa o threshold
            if best_similarity >= self.SIMILARITY_THRESHOLD:
                return VerificationResult(
                    is_authorized=True,
                    confidence=float(best_similarity),
                    user_name=best_match,
                    message=f"Voz reconhecida: {best_match} (confiança: {best_similarity:.1%})"
                )
            else:
                return VerificationResult(
                    is_authorized=False,
                    confidence=float(best_similarity),
                    user_name=None,
                    message=f"Voz não reconhecida (similaridade: {best_similarity:.1%}). Quem está falando?"
                )
                
        except Exception as e:
            logger.error(f"Erro na verificação: {e}")
            return VerificationResult(
                is_authorized=False,
                confidence=0.0,
                user_name=None,
                message=f"Erro ao verificar voz: {str(e)}"
            )
    
    def verify_from_file(self, audio_file: str) -> VerificationResult:
        """Verifica voz a partir de arquivo WAV."""
        self._lazy_init()
        
        try:
            wav = self._load_audio_file(audio_file)
            return self.verify(wav)
        except Exception as e:
            return VerificationResult(
                is_authorized=False,
                confidence=0.0,
                user_name=None,
                message=f"Erro ao processar arquivo: {str(e)}"
            )
    
    def list_enrolled_users(self) -> list[str]:
        """Retorna lista de usuários cadastrados."""
        self._lazy_init()
        return list(self.authorized_embeddings.keys())
    
    def remove_user(self, user_name: str) -> bool:
        """Remove um usuário cadastrado."""
        try:
            # Remove embedding
            embedding_file = self.voice_data_dir / f"{user_name}_embedding.npy"
            if embedding_file.exists():
                embedding_file.unlink()
            
            # Atualiza profiles.json
            profiles_file = self.voice_data_dir / "profiles.json"
            if profiles_file.exists():
                with open(profiles_file, 'r') as f:
                    profiles = json.load(f)
                if user_name in profiles:
                    del profiles[user_name]
                with open(profiles_file, 'w') as f:
                    json.dump(profiles, f, indent=2)
            
            # Remove do cache
            if user_name in self.authorized_embeddings:
                del self.authorized_embeddings[user_name]
            
            logger.info(f"Usuário '{user_name}' removido")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover usuário: {e}")
            return False
    
    def adjust_threshold(self, new_threshold: float):
        """
        Ajusta o threshold de similaridade.
        
        Args:
            new_threshold: Valor entre 0.6 e 0.95
                - 0.6-0.7: Mais permissivo (menos falsos negativos)
                - 0.75-0.8: Balanceado (recomendado)
                - 0.85-0.95: Mais restritivo (mais seguro)
        """
        if 0.5 <= new_threshold <= 0.99:
            self.SIMILARITY_THRESHOLD = new_threshold
            logger.info(f"Threshold ajustado para: {new_threshold}")
        else:
            logger.warning("Threshold deve estar entre 0.5 e 0.99")


# Singleton para uso global
_verifier: Optional[VoiceVerifier] = None


def get_verifier() -> VoiceVerifier:
    """Retorna instância singleton do verificador."""
    global _verifier
    if _verifier is None:
        _verifier = VoiceVerifier()
    return _verifier


# ========== CLI para cadastro ==========

def record_audio_sample(duration: float = 3.0, sample_rate: int = 16000) -> np.ndarray:
    """
    Grava uma amostra de áudio do microfone.
    
    Args:
        duration: Duração em segundos
        sample_rate: Taxa de amostragem (16kHz para Resemblyzer)
    """
    try:
        import sounddevice as sd
        print(f"Gravando {duration} segundos... Fale algo!")
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()
        print("Gravação concluída!")
        return audio.flatten()
    except ImportError:
        print("Instale sounddevice: pip install sounddevice")
        raise
    except Exception as e:
        print(f"Erro ao gravar: {e}")
        raise


def interactive_enrollment(user_name: str = "Thiago", num_samples: int = 5):
    """
    Processo interativo de cadastro de voz.
    
    Args:
        user_name: Nome do usuário
        num_samples: Quantidade de amostras a gravar
    """
    print(f"\n{'='*50}")
    print(f"  CADASTRO DE VOZ - {user_name}")
    print(f"{'='*50}")
    print(f"\nVocê irá gravar {num_samples} amostras de áudio.")
    print("Para cada amostra, fale uma frase diferente de 3 segundos.")
    print("Exemplos de frases:")
    print("  - 'Jarvis, estou precisando da sua ajuda'")
    print("  - 'Abra o Spotify e coloque uma música'")
    print("  - 'Qual é a previsão do tempo para hoje'")
    print("  - 'Me mostre os arquivos da pasta documentos'")
    print("  - 'Jarvis, qual é o status do sistema'")
    
    input("\nPressione ENTER quando estiver pronto...")
    
    samples = []
    for i in range(num_samples):
        print(f"\n[Amostra {i+1}/{num_samples}]")
        input("Pressione ENTER para iniciar a gravação...")
        
        try:
            audio = record_audio_sample(duration=3.0)
            samples.append(audio)
            print(f"✓ Amostra {i+1} gravada!")
        except Exception as e:
            print(f"✗ Erro na amostra {i+1}: {e}")
            retry = input("Tentar novamente? (s/n): ")
            if retry.lower() == 's':
                audio = record_audio_sample(duration=3.0)
                samples.append(audio)
    
    if len(samples) >= 3:
        print("\nProcessando amostras...")
        verifier = get_verifier()
        success = verifier.enroll_user(user_name, samples)
        
        if success:
            print(f"\n✅ Cadastro de '{user_name}' concluído com sucesso!")
            print(f"   Amostras processadas: {len(samples)}")
            print(f"   Perfil salvo em: {verifier.voice_data_dir}")
        else:
            print("\n❌ Erro ao cadastrar. Verifique os logs.")
    else:
        print(f"\n❌ Necessário pelo menos 3 amostras. Obtidas: {len(samples)}")


def test_verification():
    """Testa verificação com uma nova gravação."""
    print("\n" + "="*50)
    print("  TESTE DE VERIFICAÇÃO DE VOZ")
    print("="*50)
    
    verifier = get_verifier()
    users = verifier.list_enrolled_users()
    
    if not users:
        print("\nNenhum usuário cadastrado. Execute o cadastro primeiro.")
        return
    
    print(f"\nUsuários cadastrados: {', '.join(users)}")
    input("\nPressione ENTER para gravar e testar...")
    
    audio = record_audio_sample(duration=3.0)
    result = verifier.verify(audio)
    
    print(f"\n{'='*50}")
    if result.is_authorized:
        print(f"✅ {result.message}")
    else:
        print(f"⚠️ {result.message}")
    print(f"   Confiança: {result.confidence:.1%}")
    print(f"{'='*50}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "enroll":
            name = sys.argv[2] if len(sys.argv) > 2 else "Thiago"
            interactive_enrollment(name)
            
        elif command == "test":
            test_verification()
            
        elif command == "list":
            verifier = get_verifier()
            users = verifier.list_enrolled_users()
            print(f"Usuários cadastrados: {users if users else 'Nenhum'}")
            
        elif command == "remove":
            if len(sys.argv) > 2:
                verifier = get_verifier()
                verifier.remove_user(sys.argv[2])
            else:
                print("Uso: python voice_verification.py remove <nome>")
        else:
            print("Comandos: enroll [nome], test, list, remove <nome>")
    else:
        print("JARVIS Voice Verification")
        print("="*30)
        print("Comandos disponíveis:")
        print("  python -m jarvis.voice_verification enroll [nome]  - Cadastrar voz")
        print("  python -m jarvis.voice_verification test           - Testar verificação")
        print("  python -m jarvis.voice_verification list           - Listar usuários")
        print("  python -m jarvis.voice_verification remove <nome>  - Remover usuário")
