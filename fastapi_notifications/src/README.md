### Миграции:
- **создать миграцию**:
`alembic revision --autogenerate -m "migration1"`,

где `migration1` - имя миграции;
- **применить все миграции**: 
`alembic upgrade head`.