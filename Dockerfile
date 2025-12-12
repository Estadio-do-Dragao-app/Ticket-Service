FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Dar permissão de execução ao script de startup
RUN chmod +x startup.sh

# Criar diretório para QR codes
RUN mkdir -p /app/qr_codes

CMD ["./startup.sh"]