# Migração de fs_storage para SqlStorage (abstra-json-sql)

## Data: 2025-10-19

## Resumo
Substituímos a implementação de `FileSystemStorage` (fs_storage.py) por `SqlStorage` que utiliza a biblioteca `abstra-json-sql` para armazenamento de dados estruturados usando SQL sobre JSON.

## Alterações Realizadas

### Arquivos Criados
- `abstra_internals/services/sql_storage.py` - Nova implementação usando abstra-json-sql
- `abstra_internals/services/sql_storage_test.py` - Testes adaptados (renomeado de fs_storage_test.py)

### Arquivos Removidos
- `abstra_internals/services/fs_storage.py`

### Arquivos Modificados
- `abstra_internals/repositories/execution.py` - Atualizado para usar SqlStorage
- `abstra_internals/repositories/tasks.py` - Atualizado para usar SqlStorage
- `requirements.txt` - Adicionada dependência `abstra-json-sql`

## Problemas Encontrados e Soluções

### 1. Palavras Reservadas SQL como Nomes de Colunas
**Problema:** Quando um modelo Pydantic tem campos com nomes que são palavras reservadas SQL (como `update`, `select`, `where`, etc.), o parser da biblioteca `abstra-json-sql` falha ao interpretar os comandos INSERT e UPDATE.

**Exemplo de erro:**
```python
AssertionError: Expected column name, got Token(type='keyword', value='update')
```

**Solução implementada:**
Usar aspas duplas (`"`) para escapar nomes de colunas em todas as queries SQL:
```python
# Ao invés de:
INSERT INTO data (id, update, name) VALUES ('1', 'value', 'John')

# Usamos:
INSERT INTO data ("id", "update", "name") VALUES ('1', 'value', 'John')
```

Isso garante que palavras reservadas sejam tratadas como identificadores, não como keywords.

**Teste adicionado:** `test_reserved_sql_keywords` para garantir que campos com nomes reservados funcionam corretamente.

### 2. WHERE Clause não funcionando em alguns casos
**Problema:** Ao executar queries SQL com `WHERE` clause, a biblioteca `abstra-json-sql` lança erro `Unknown variable: <column_name>` em alguns contextos, mesmo quando a coluna existe e os dados foram inseridos corretamente.

**Exemplo de erro:**
```python
eval_sql("SELECT * FROM data WHERE id = 'test_id'", tables, {})
# ValueError: Unknown variable: id
```

**Workaround implementado:**
- Em `_load()`: Carregar todos os registros com `SELECT * FROM table` e filtrar manualmente em Python
- Em `save()`: Carregar todos os IDs e filtrar para checar existência
- Em `delete()`: Carregar todos os registros, encontrar o índice e usar `_delete()` diretamente

**Código exemplo do workaround:**
```python
# Ao invés de:
eval_sql(f"SELECT * FROM {table_name} WHERE id = '{id}'", tables, {})

# Usamos:
result = eval_sql(f"SELECT * FROM {table_name}", tables, {})
for row in result:
    if row.get("id") == id:
        return row
```

**TODO para json-sql:** Investigar por que WHERE clause falha em alguns contextos. Os testes unitários da biblioteca passam, mas em uso real com `FileSystemJsonTables` o problema ocorre consistentemente.

### 2. Singleton Pattern para FileSystemJsonTables
**Problema:** Criar uma nova instância de `FileSystemJsonTables` a cada acesso poderia causar problemas de sincronização.

**Solução:** Implementado um singleton pattern usando `_tables_instance` cached no `SqlStorage`.

## Notas de Implementação

### Serialização
- Valores são serializados usando `abstra_internals.interface.sdk.tables.utils.serialize()`
- Objetos complexos (dict, list) são convertidos para JSON strings
- Valores None são armazenados como strings vazias
- Na deserialização, tentamos fazer parse JSON, se falhar mantemos como string

### Campo ID
- O campo `id` é sempre criado como coluna primary key, mesmo que não exista no modelo Pydantic
- Se o modelo não tem campo `id`, ele é adicionado automaticamente ao salvar
- Isso garante compatibilidade com modelos que não têm `id` explícito

### Thread Safety
- Mantido o uso de `mp_context.RLock()` para garantir thread-safety nas operações

## Testes
Todos os 7 testes passaram:
- ✅ test_clear
- ✅ test_delete
- ✅ test_load_all
- ✅ test_load_nonexistent
- ✅ test_save_and_load
- ✅ test_save_invalid_data
- ✅ test_reserved_sql_keywords (novo teste para palavras reservadas)

## Próximos Passos
1. Reportar o problema do WHERE clause no repositório do abstra-json-sql
2. Quando o bug for corrigido, remover os workarounds e usar WHERE clause diretamente
3. Considerar adicionar índices para melhorar performance em tabelas grandes
4. Avaliar uso de `FileSystemJsonLTables` (JSONL format) para melhor performance com grandes volumes
