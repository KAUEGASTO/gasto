# Gastô · app instalável (versão 5.0)

O mesmo Gastô do protótipo (fatura em PDF do Itaú, conferência, metas, gráfico do ano, ritmo da fatura),
agora com **login** e **dados na nuvem**: o que um lança aparece no celular do outro.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `site/` | O app. É isso que vai para o endereço na internet (GitHub Pages). |
| `site/index.html` | O app inteiro (telas e regras). |
| `site/manifest.json`, `site/sw.js`, ícones | Fazem virar "app" na tela do celular e abrir sem internet. |
| `supabase.sql` | Cria o banco de dados no Supabase. Rode uma vez. |
| `build.py` | Gera a pasta `site/` a partir do `cartao.html`, já com o endereço e a chave do Supabase. |

## Como funciona

- **Supabase** (gratuito) guarda os dados e faz o login com e-mail e senha.
- Cada pessoa tem o próprio login. A família compartilha os dados:
  - quem começa toca em **Criar a família**;
  - os outros entram com o **código da família** (aparece em Configurações).
- Cada login escolhe **"Quem é você?"**. Os gastos lançados naquele celular já entram no nome dessa pessoa.
- Sem internet o app continua funcionando. O que for lançado fica guardado no celular e é enviado quando a internet voltar.
  A bolinha ao lado de "Seu cartão sob controle" mostra o estado:
  - verde: sincronizado;
  - amarela: salvando;
  - vermelha: sem internet.
- **Backup** (em Configurações) exporta e restaura todos os dados: pessoas, cartões, categorias, metas, gastos e lojas aprendidas.

## Banco de dados (para o app nativo depois)

- `families`: a família, com o código de convite.
- `members`: o login de cada pessoa → qual pessoa ela é no app.
- `items`: tudo do app, uma linha por item. O campo `kind` diz o tipo: `person`, `card`, `category`, `expense`, `rule` ou `meta`.
- **Regras de acesso:** cada um só enxerga a própria família. Isso já foi testado.

O app nativo (Expo) vai usar o mesmo banco, os mesmos logins e as mesmas regras. Nada se perde.

## Publicar uma versão nova

```
python3 build.py https://SEU-PROJETO.supabase.co SUA_CHAVE_ANON
```

Depois envie o conteúdo de `site/` para o repositório do GitHub Pages.

A chave "anon" é feita para ficar no app: quem protege os dados são as regras de acesso do banco.
