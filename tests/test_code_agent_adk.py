"""
Teste do CodeAgent com Google ADK
=================================
Demonstra o SubAgent funcionando com LLM do Gemini.
"""
import asyncio
import os
import sys

sys.path.insert(0, 'src')

from jarvis.agents.code_agent import CodeAgent  # type: ignore[reportMissingImports], TaskType

async def main():
    print("="*60)
    print("🤖 TESTE: CodeAgent com Google ADK")
    print("="*60)
    
    # Verificar chave de API
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️ Configure GOOGLE_API_KEY no .env")
        return
    
    print(f"✅ API Key encontrada: {api_key[:10]}...")
    
    # Criar CodeAgent
    agent = CodeAgent(
        workspace_path=os.getcwd(),
        enable_github=False,
        model="gemini-2.5-flash"
    )
    
    print("\n🚀 Inicializando CodeAgent...")
    initialized = await agent.initialize()
    
    if not initialized:
        print("❌ CodeAgent não está pronto")
        return
    
    print("✅ CodeAgent pronto!")
    
    # Tarefa de teste
    task = "Analise o arquivo src/jarvis/agent.py e me diga quantas linhas de código tem, quais classes existem e sugira melhorias."
    
    print(f"\n📝 TAREFA: {task}")
    print("-"*60)
    
    # Executar usando analyze_file
    result = await agent.analyze_file("src/jarvis/agent.py")
    
    print("\n📤 RESPOSTA DO CODEAGENT:")
    print("-"*60)
    print(f"Sucesso: {result.success}")
    print(f"Mensagem: {result.message}")
    if result.suggestions:
        print("\n💡 Sugestões:")
        for s in result.suggestions:
            print(f"  - {s}")
    
    # Desligar
    await agent.shutdown()
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    # Carregar .env
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(main())
