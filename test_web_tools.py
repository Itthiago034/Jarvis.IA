"""Teste das ferramentas web expandidas"""
import asyncio
from src.jarvis.tools.web import fetch_webpage, search_web, WebBrowser

async def test():
    print("=" * 50)
    print("🌐 TESTANDO FERRAMENTAS WEB EXPANDIDAS")
    print("=" * 50)
    
    # Teste 1: Busca DuckDuckGo
    print("\n🔍 Teste 1: Busca web (DuckDuckGo)...")
    results = await search_web("Python programming language", num_results=3)
    if results:
        for i, r in enumerate(results[:3], 1):
            title = r.get("title", "?")[:60]
            print(f"  {i}. {title}")
        print("  ✅ Busca funcionando!")
    else:
        print("  ⚠️ Nenhum resultado")
    
    # Teste 2: Fetch de página
    print("\n🌐 Teste 2: Acessando httpbin.org...")
    page = await fetch_webpage("https://httpbin.org/get", extract_text=False)
    print(f"  Status: {page.get('status_code')}")
    print(f"  Success: {page.get('success')}")
    if page.get('success'):
        print("  ✅ Acesso a páginas funcionando!")
    
    # Teste 3: WebBrowser com sessão
    print("\n🖥️ Teste 3: WebBrowser com sessão persistente...")
    browser = WebBrowser()
    try:
        result = await browser.get("https://jsonplaceholder.typicode.com/posts/1")
        print(f"  Status: {result.get('status_code')}")
        print(f"  Content type: {result.get('content_type')}")
        if result.get('success'):
            print("  ✅ WebBrowser funcionando!")
    finally:
        await browser.close()
    
    # Teste 4: Fetch de página com extração de texto
    print("\n📄 Teste 4: Extração de texto de página...")
    page = await fetch_webpage("https://example.com", extract_text=True)
    print(f"  Title: {page.get('title', 'N/A')}")
    print(f"  Content size: {len(page.get('content', ''))} chars")
    if page.get('success'):
        print("  ✅ Extração de texto funcionando!")
    
    print("\n" + "=" * 50)
    print("✅ TODOS OS TESTES CONCLUÍDOS!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test())
