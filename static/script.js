document.addEventListener('DOMContentLoaded', function() {
    // Atualizar o nome do arquivo selecionado
    const fileInput = document.getElementById('xml-file');
    const fileLabel = document.getElementById('file-label');

    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                if (fileInput.files.length === 1) {
                    fileLabel.innerText = `${fileInput.files[0].name}`;
                } else {
                    fileLabel.innerText = `${fileInput.files.length} arquivos selecionados`;
                }
            } else {
                fileLabel.innerText = 'Nenhum arquivo selecionado';
            }
        });
    }

    // Verifica se algum arquivo foi selecionado ao tentar enviar o formulário
    const uploadBtn = document.getElementById('upload-btn');
    if (uploadBtn) {
        uploadBtn.addEventListener('click', function(event) {
            const xmlFileInput = document.getElementById('xml-file');
            if (xmlFileInput.files.length === 0) {
                event.preventDefault();
                alert('Por favor, selecione pelo menos um arquivo XML.');
                return false;
            }

            // Verifica se todos os arquivos têm a extensão .xml
            for (let i = 0; i < xmlFileInput.files.length; i++) {
                if (!xmlFileInput.files[i].name.endsWith('.xml')) {
                    event.preventDefault(); 
                    alert('Por favor, selecione apenas arquivos XML.');
                    return false;
                }
            }
        });
    }

    // Script para exibir o ano atual no rodapé
    const footerYear = document.getElementById('ano-atual');
    if (footerYear) {
        footerYear.textContent = new Date().getFullYear();
    }
});
