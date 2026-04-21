# ConnectS — Database Connection String Automator

![ConnectS Logo](https://raw.githubusercontent.com/obrunis/ConnectS/main/assets/connects_logo.png) <!-- Placeholder for a potential logo -->

ConnectS é uma ferramenta profissional desenvolvida em Python com Tkinter para automatizar a configuração de strings de conexão Oracle TNS e atualizar arquivos `MegaConfig.xml`. Com uma interface de usuário moderna e temática Cyber/Glassmorphism, o ConnectS simplifica o processo de gerenciamento de conexões de banco de dados, tornando-o mais eficiente e menos propenso a erros.

## Funcionalidades

*   **Automação TNS**: Insere ou atualiza entradas no arquivo `tnsnames.ora`.
*   **Configuração XML**: Atualiza automaticamente as tags `<ORACLE>` e `<LOGONUSERNAME>` no `MegaConfig.xml`.
*   **Detecção Automática de Alias**: Capacidade de detectar automaticamente o alias TNS a partir da string de conexão fornecida.
*   **Lançamento de Executáveis**: Inicia executáveis externos (`MegaConnectionManager.exe` e `Mega_Registro_App.exe`) com um atraso configurável.
*   **Interface Intuitiva**: UI desenvolvida com componentes personalizados em Tkinter, apresentando um design Cyber/Glassmorphism.
*   **Log de Atividades**: Painel de log integrado para acompanhar o progresso e identificar possíveis problemas.

## Tecnologias Utilizadas

*   **Python**: Linguagem de programação principal.
*   **Tkinter**: Biblioteca padrão do Python para criação de interfaces gráficas de usuário (GUI).
*   **`re` (Expressões Regulares)**: Para parsing e manipulação de strings de conexão e arquivos XML.
*   **`os`, `subprocess`, `threading`, `time`**: Para operações de sistema, execução de processos e gerenciamento de threads.

## Instalação e Uso

### Pré-requisitos

*   Python 3.x
*   Git (para clonar o repositório)

### Configuração

1.  **Clone o repositório**:

    ```bash
    git clone https://github.com/seu-usuario/ConnectS.git
    cd ConnectS
    ```

2.  **Crie e ative um ambiente virtual** (recomendado):

    ```bash
    python -m venv venv
    # No Windows
    .\venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências**:
    Este projeto utiliza apenas bibliotecas padrão do Python, então não há dependências adicionais para instalar via `pip`.

### Executando a Aplicação

Para iniciar a aplicação, execute o seguinte comando na raiz do projeto (com o ambiente virtual ativado):

```bash
python connects_automator.py
```

## Estrutura do Projeto

O projeto `connects_automator.py` segue uma arquitetura modular:

*   **Camada de Domínio**: Contém a lógica de negócios pura, como `TnsEntry`, `ConfigUpdate` e funções de parsing.
*   **Camada de Serviço**: Lida com operações de I/O, como leitura/escrita de arquivos e execução de processos externos.
*   **Sistema de Design (DS)**: Define a paleta de cores, tipografia e espaçamento para a interface.
*   **Componentes Glassmorphism**: Implementa componentes personalizados do Tkinter com o estilo visual Cyber/Glassmorphism.
*   **Aplicação Principal (`ConnectSApp`)**: Orquestra a interface do usuário e o fluxo de trabalho de automação.

## Contribuição

Contribuições são bem-vindas! Se você tiver sugestões de melhorias, relatórios de bugs ou quiser adicionar novas funcionalidades, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE). Veja o arquivo `LICENSE` para mais detalhes.

---

**Autor**: Manus AI (em nome do usuário)
