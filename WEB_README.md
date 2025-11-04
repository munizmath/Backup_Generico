# 🌐 Sistema de Backup Avançado - Versão Web

## 🚀 Início Rápido

### Instalação

1. **Instalar dependências:**
```bash
pip install -r web/requirements.txt
```

2. **Iniciar servidor:**
```bash
# Windows
run_web.bat

# Linux/Mac
python app.py
```

3. **Acessar no navegador:**
```
http://localhost:5000
```

## 🎨 Características da Interface Web

### Design Moderno
- ✅ **Glassmorphism**: Efeitos de vidro translúcido
- ✅ **Gradiente Animado**: Fundo com gradiente animado
- ✅ **Tipografia Inter**: Fonte moderna e legível
- ✅ **Responsivo**: Funciona em desktop, tablet e mobile

### Acessibilidade
- ✅ **Foco Visível**: Indicadores claros de foco
- ✅ **Validação Amigável**: Mensagens de erro claras
- ✅ **Navegação por Teclado**: Suporte completo
- ✅ **ARIA Labels**: Atributos de acessibilidade

### Funcionalidades
- ✅ **Menu Completo**: Todas as opções solicitadas
- ✅ **Temas**: Claro e Escuro
- ✅ **Dashboard**: Métricas em tempo real
- ✅ **Monitoramento**: Sistema de alertas
- ✅ **Histórico**: Lista de backups
- ✅ **Configurações**: Personalização completa

## 📱 Menu Disponível

O menu lateral inclui todas as opções solicitadas:

1. **Nova Guia**: Abre a página atual em nova guia
2. **Nova Janela**: Abre em nova janela
3. **Abrir Configurações**: Navega para página de configurações
4. **Dashboards**: Navega para dashboard
5. **Monitoramento**: Navega para monitoramento
6. **Tema Claro/Escuro**: Alterna entre temas
7. **Histórico**: Navega para histórico de backups
8. **Ajuda**: Navega para página de ajuda
9. **Sobre**: Navega para página sobre
10. **Sair**: Fecha a aplicação

## 🎯 Páginas Disponíveis

- `/` - Página inicial com ações rápidas
- `/dashboard` - Dashboard com métricas
- `/monitoramento` - Monitoramento em tempo real
- `/historico` - Histórico de backups
- `/configuracoes` - Configurações do sistema
- `/ajuda` - Ajuda e FAQ
- `/sobre` - Informações sobre o sistema

## 🔧 APIs Disponíveis

### GET `/api/config`
Obter configurações do sistema

### POST `/api/config`
Atualizar configurações

### POST `/api/backup`
Criar novo backup

### GET `/api/system/metrics`
Obter métricas do sistema

### GET `/api/backups/list`
Listar todos os backups

### GET/POST `/api/theme`
Gerenciar tema (claro/escuro)

## 📝 Estrutura de Arquivos

```
web/
├── templates/          # Templates HTML
│   ├── base.html      # Template base
│   ├── index.html     # Página inicial
│   ├── dashboard.html # Dashboard
│   ├── monitoramento.html
│   ├── historico.html
│   ├── configuracoes.html
│   ├── ajuda.html
│   └── sobre.html
├── static/
│   ├── css/
│   │   ├── main.css   # Estilos principais
│   │   └── theme.css  # Sistema de temas
│   └── js/
│       ├── main.js    # JavaScript principal
│       └── theme.js   # Sistema de temas
└── requirements.txt    # Dependências Python

app.py                  # Aplicação Flask principal
run_web.bat            # Script de inicialização
```

## 🎨 Personalização

### Cores e Temas

As cores são definidas em `web/static/css/theme.css`. Você pode personalizar:

- `--bg-primary`: Cor de fundo principal
- `--bg-secondary`: Cor de fundo secundária
- `--text-primary`: Cor do texto principal
- `--accent-color`: Cor de destaque
- E mais...

### Glassmorphism

O efeito glassmorphism é controlado por:

- `--glass-bg`: Fundo translúcido
- `--glass-border`: Borda translúcida
- `--glass-blur`: Intensidade do blur

## 🚀 Deploy

### Produção

Para produção, use um servidor WSGI como Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (Futuro)

Um Dockerfile será criado para facilitar o deploy.

## 📱 Responsividade

A interface é totalmente responsiva:

- **Desktop**: Layout completo com sidebar
- **Tablet**: Sidebar colapsável
- **Mobile**: Menu hamburguer

## 🔒 Segurança

- Validação de entrada no frontend e backend
- Sanitização de dados
- Proteção CSRF (Flask-WTF - opcional)
- Headers de segurança

## 📞 Suporte

Para problemas ou dúvidas:

1. Consulte o README principal
2. Verifique os logs do servidor
3. Abra uma issue no GitHub

