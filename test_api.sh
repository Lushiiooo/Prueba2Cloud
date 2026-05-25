#!/bin/bash
# Script para probar endpoints de la API

BASE_URL="http://localhost:8000/api"

echo "============================================"
echo "🧪 Pruebas de API Medical Reserva"
echo "============================================"

echo -e "\n1️⃣  Obtener Token JWT"
TOKEN_RESPONSE=$(curl -s -X POST $BASE_URL/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')
echo $TOKEN_RESPONSE | jq '.'
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access')
echo "Access Token: $ACCESS_TOKEN"

echo -e "\n2️⃣  Listar Doctores"
curl -s -X GET $BASE_URL/doctores/ | jq '.'

echo -e "\n3️⃣  Filtrar Doctores Disponibles"
curl -s -X GET "$BASE_URL/doctores/disponibles/" | jq '.'

echo -e "\n4️⃣  Listar Pacientes (Requiere Auth)"
curl -s -X GET $BASE_URL/pacientes/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'

echo -e "\n5️⃣  Mi Perfil (Paciente)"
curl -s -X GET $BASE_URL/pacientes/mi_perfil/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'

echo -e "\n6️⃣  Listar Reservas del Usuario"
curl -s -X GET $BASE_URL/reservas/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'

echo -e "\n7️⃣  Reservas Próximas"
curl -s -X GET $BASE_URL/reservas/proximas/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'

echo -e "\n✅ Pruebas Completadas"
