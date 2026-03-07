
document.addEventListener('DOMContentLoaded', () => {
    // Exemplo de funcionalidade: rolagem suave para links de navegação
    document.querySelectorAll('nav a').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - document.querySelector('header').offsetHeight, // Ajusta para a altura do cabeçalho fixo
                    behavior: 'smooth'
                });
            }
        });
    });

    // Adicione mais interatividade aqui, se necessário
    console.log("Site Pessoal Carregado!");
});
