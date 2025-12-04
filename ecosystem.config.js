module.exports = {
  apps: [{
    name: 'absiddikhrm',  // নতুন নাম
    script: '/root/siddikhrm/venv/bin/gunicorn',
    args: 'config.wsgi:application --bind 0.0.0.0:5934 --workers 3 --timeout 60',
    cwd: '/root/siddikhrm/hrm',
    interpreter: 'none',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      DJANGO_SETTINGS_MODULE: 'config.settings',
      PYTHONPATH: '/root/siddikhrm/hrm',
    },
    error_file: '/root/siddikhrm/hrm/logs/pm2-error.log',
    out_file: '/root/siddikhrm/hrm/logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
  }]
};

