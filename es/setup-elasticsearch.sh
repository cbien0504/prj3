#!/bin/bash

if curl -X HEAD -I "http://elasticsearch:9200/index_users" -o /dev/null -w "%{http_code}" -s | grep -q "200"; then
  echo "Xóa index 'users'..."
  curl -X DELETE "http://elasticsearch:9200/index_users"
fi
echo "Tạo index 'users'..."
curl -X PUT "http://elasticsearch:9200/index_users" -H 'Content-Type: application/json' -d @/es/mapping.json
