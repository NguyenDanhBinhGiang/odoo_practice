docker stop odoo-practice
docker exec odoo-db psql -U odoo -c "DROP DATABASE IF EXISTS odoo_practice;"
docker exec odoo-db psql -U odoo -c "CREATE DATABASE odoo_practice OWNER odoo;"
# shellcheck disable=SC2002
cat odoo_practice.bak | docker exec -i odoo-db psql -U odoo -d odoo_practice
docker start odoo-practice