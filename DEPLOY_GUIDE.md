# 🚀 Guia de Deploy - TimeTracker v1.2.0

## 📋 Pré-Requisitos de Produção

### Sistema
- **Python 3.8+** (recomendado 3.12)
- **Servidor Web** (Nginx/Apache)
- **WSGI Server** (Gunicorn/uWSGI)
- **Banco de Dados** (PostgreSQL/MySQL recomendado)

### Dependências Python
```bash
pip install -r requirements.txt
```

## 🔧 Configuração de Produção

### 1. Variáveis de Ambiente
```bash
# .env (criar na raiz do projeto)
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:password@localhost/timetracker_db
```

### 2. Settings de Produção
```python
# timetracker/settings.py - Adicionar no final
import os
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY', default='your-secret-key')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Banco de dados
if config('DATABASE_URL', default=None):
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(config('DATABASE_URL'))

# Arquivos estáticos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Segurança
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
```

## 📦 Deploy Steps

### 1. Preparar Código
```bash
# Clone do repositório
git clone https://github.com/Mablemb/time-tracker.git
cd time-tracker

# Ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
pip install gunicorn psycopg2-binary python-decouple dj-database-url
```

### 2. Configurar Banco
```bash
# PostgreSQL (recomendado)
createdb timetracker_db
createuser timetracker_user --password

# Migrar banco
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

### 3. Configurar Gunicorn
```bash
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
user = "www-data"
group = "www-data"
```

### 4. Systemd Service
```ini
# /etc/systemd/system/timetracker.service
[Unit]
Description=TimeTracker Django App
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
RuntimeDirectory=timetracker
WorkingDirectory=/path/to/timetracker
Environment=PATH=/path/to/timetracker/venv/bin
ExecStart=/path/to/timetracker/venv/bin/gunicorn --config gunicorn.conf.py timetracker.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 5. Nginx Configuration
```nginx
# /etc/nginx/sites-available/timetracker
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Static files
    location /static/ {
        alias /path/to/timetracker/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🚀 Iniciar Serviços

### 1. Habilitar e Iniciar
```bash
# Habilitar serviço
sudo systemctl enable timetracker
sudo systemctl start timetracker

# Verificar status
sudo systemctl status timetracker

# Habilitar Nginx
sudo ln -s /etc/nginx/sites-available/timetracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2. Verificar Deploy
```bash
# Logs do serviço
sudo journalctl -u timetracker -f

# Logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Verificar processos
ps aux | grep gunicorn
```

## 📊 Monitoramento

### 1. Health Check
```bash
# Criar script de verificação
#!/bin/bash
# /usr/local/bin/timetracker-health.sh
curl -f http://localhost:8000/ > /dev/null 2>&1
if [ $? -ne 0 ]; then
    systemctl restart timetracker
    echo "TimeTracker restarted at $(date)" >> /var/log/timetracker-health.log
fi
```

### 2. Cron para Health Check
```bash
# crontab -e
*/5 * * * * /usr/local/bin/timetracker-health.sh
```

### 3. Backup Automático
```bash
#!/bin/bash
# /usr/local/bin/timetracker-backup.sh
BACKUP_DIR="/backups/timetracker"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup do banco
pg_dump timetracker_db > "$BACKUP_DIR/db_$DATE.sql"

# Backup dos arquivos
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" /path/to/timetracker

# Limpar backups antigos (manter 7 dias)
find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
```

## 🔒 Segurança

### 1. Firewall
```bash
# UFW
sudo ufw allow 22   # SSH
sudo ufw allow 80   # HTTP
sudo ufw allow 443  # HTTPS
sudo ufw enable
```

### 2. SSL/TLS
```bash
# Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 3. Updates Automáticos
```bash
# /etc/cron.weekly/timetracker-update
#!/bin/bash
cd /path/to/timetracker
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart timetracker
```

## 📈 Performance

### 1. Otimizações de Banco
```sql
-- PostgreSQL - Criar índices
CREATE INDEX idx_sessao_tempo_inicio ON projects_sessaotempo(inicio);
CREATE INDEX idx_sessao_tempo_projeto ON projects_sessaotempo(projeto_id);
CREATE INDEX idx_projeto_ativo ON projects_projeto(ativo);
```

### 2. Cache (Redis)
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## ✅ Checklist de Deploy

- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados criado e migrado
- [ ] Superusuário criado
- [ ] Arquivos estáticos coletados
- [ ] Gunicorn configurado
- [ ] Systemd service criado
- [ ] Nginx configurado
- [ ] SSL/TLS ativo
- [ ] Firewall configurado
- [ ] Backup automático configurado
- [ ] Monitoramento ativo
- [ ] Teste de funcionalidades realizado

## 🚨 Troubleshooting

### Problemas Comuns
1. **502 Bad Gateway**: Verificar se Gunicorn está rodando
2. **Static files não carregam**: Verificar STATIC_ROOT e collectstatic
3. **Database errors**: Verificar conexão e permissões
4. **Permission denied**: Verificar ownership dos arquivos

### Logs Importantes
- `/var/log/nginx/error.log`
- `journalctl -u timetracker`
- `/path/to/timetracker/logs/django.log`

---

**Sistema pronto para produção!** 🎉
