# Automação Fiscal Flow & Integração SIEG

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Context](https://img.shields.io/badge/Context-Fiscal_Automation-orange)

## 📌 Visão Geral do Projeto

[cite_start]Este sistema foi desenvolvido para **eliminar completamente o processo manual** de recebimento e organização de XML de documentos fiscais proveniente do FiscalFlow que é enviado todos os dias para o e-mail do departamento fiscal, utilizando a API do Google para ler o corpo do e-mail e achar a requisição HTML escrito "aqui" para baixar o documento.

[cite_start]O robô monitora e processa arquivos XML enviados pela plataforma **Linx Fiscal Flow**, organiza-os em rede e prepara o ambiente para a coleta automática do **Agente SIEG** que fica alocado em no servidor ou maquina local onde é feito o download, garantindo a integração final com o ERP **Domínio Contábil**[cite: 4, 17].

> [cite_start]**Impacto:** Eliminação de tarefas manuais, redução de erros de escrituração e garantia de que 100% das notas (NF-e/NFS-e) estejam disponíveis para auditoria[cite: 20, 24].

## Arquitetura da Solução

O fluxo automatizado conecta a entrada de dados (E-mail) até a contabilidade (Domínio):

```mermaid
graph TD
    subgraph Entrada de Dados
    A[Linx Fiscal Flow] -->|Envia E-mail| B(Gmail Server)
    end

    subgraph Core - Automação Python
    B -->|Protocolo IMAP| C[Script de Extração]
    C -->|Web Scraping| D{Link Seguro?}
    D -->|Sim| E[Download do Pacote]
    E -->|Descompactação| F[Organização por Data]
    end

    subgraph Integração Contábil
    F -->|Salva em| G[Pasta de Rede Monitorada]
    G -->|Monitoramento Ativo| H[Agente SIEG]
    H -->|Upload Automático| I[Plataforma SIEG]
    I -->|Integração| J[Domínio Contábil]
    end
