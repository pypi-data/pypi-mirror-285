# Simple Security for FastAPI

Este projeto fornece um middleware de segurança de facíl condiguração para FastAPI, permitindo a detecção e mitigação de ataques de injeção (SQL, XSS, NoSQL) e a adição de cabeçalhos de segurança às respostas.

## Instalação

Instale a biblioteca via pip:

```sh
pip install fastapi-SimpleSecurity
```

## Configuração

### Arquivo de Configuração

Edite o arquivo `config.yaml` na pasta `app/config/` para definir as regras de injeção, exclusões e limitação de taxa. Exemplo:

```yaml
rules:
  injection:
    enabled: true
    sql:
      enabled: true
      patterns:
        - "(?i)\\b(select|insert|update|delete|drop|truncate|alter|exec|execute|declare|union|join)\\b|'--|--[\\s]*$|';[\\s]*$|\"\\s*;|/\\*.*\\*/|--[^-]*-|' OR ''='|' OR '1'='1|' OR 1=1|--|/\\*|\\*/|;|@@|char\\(|nchar\\(|varchar\\(|nvarchar\\(|alter\\(|begin\\(|cast\\(|create\\(|cursor\\(|declare\\(|delete\\(|drop\\(|end\\(|exec\\(|execute\\(|fetch\\(|insert\\(|kill\\(|open\\(|select\\(|sys\\(|sysobjects\\(|syscolumns\\(|table\\(|update\\("
        - '(?i)(\\b(SELECT|INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|EXEC|EXECUTE|DECLARE|UNION|JOIN)\\b|--;|'';|-- |\\x27|\\x22)'
    xss:
      enabled: true
      patterns:
        - "<script[^>]*?>.*?</script>"
        - "<iframe[^>]*?>.*?</iframe>"
        - "<object[^>]*?>.*?</object>"
        - "(?i)javascript:"
        - "(?i)\\bon\\w+=.*"
        - "(?i)<img[^>]+src[^>]+onerror=.*"
        - "(?i)<a[^>]+href[^>]+javascript:.*"
        - "(?i)\\bstyle=.*expression\\(.*"
        - "(?i)\\bstyle=.*url\\(.*"
        - "(?i)\\bstyle=.*import\\(.*"
        - "(?i)\\b@import\\b"
    nosql:
      enabled: true
      patterns:
        - "\\{\\$ne\\}"
        - "\\{\\$gt\\}"
        - "\\{\\$lt\\}"
        - "\\{\\$exists\\}"
        - "\\{\\$regex\\}"
        - "\\{\\$where\\}"
        - "\\{\\$all\\}"
        - "\\{\\$elemMatch\\}"

exclusions:
  - "/excluded-route"

rate_limiting:
  enabled: true
  requests: 100
  per_minute: 1
```

### Inicialização do Middleware

Para usar o middleware de segurança em sua aplicação FastAPI, configure e adicione o middleware usando a classe `WAFMiddleware`:

```python
from fastapi import FastAPI
from simple_security.middleware import WAFMiddleware

app = FastAPI()

waf_middleware = WAFMiddleware(app, config_file_path="app/config/settings.yaml")

@app.get("/")
async def root():
    return {"message": "Hello, World!"}
```

## Funcionalidades

### Filtros de Injeção

O middleware verifica padrões de injeção em solicitações para detectar e prevenir ataques de injeção SQL, XSS e NoSQL.

- **SQL Injection**: Detecta padrões comuns de injeção SQL.
- **XSS (Cross-Site Scripting)**: Detecta scripts maliciosos embutidos em solicitações.
- **NoSQL Injection**: Detecta padrões de injeção NoSQL.

### Cabeçalhos de Segurança

O middleware adiciona cabeçalhos de segurança às respostas para proteger contra várias ameaças.

- `X-Frame-Options`
- `Cache-Control`
- `Clear-Site-Data`
- `Content-Security-Policy`
- `Cross-Origin-Embedder-Policy`
- `Cross-Origin-Opener-Policy`
- `Cross-Origin-Resource-Policy`
- `Referrer-Policy`
- `Strict-Transport-Security`
- `X-Content-Type-Options`
- `X-DNS-Prefetch-Control`
- `X-Download-Options`
- `X-Permitted-Cross-Domain-Policies`
- `X-XSS-Protection`

### Exclusões

Você pode especificar caminhos a serem excluídos das verificações de segurança no arquivo de configuração.

### Limitação de Taxa

O middleware suporta limitação de taxa, permitindo definir o número de solicitações permitidas por minuto.

## Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.