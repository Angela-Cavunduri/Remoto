import os
import uuid
import boto3
from botocore.exceptions import ClientError

# Leitura das variáveis de ambiente (devem estar configuradas no Render ou .env)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET")

# Cliente S3 único (singleton)
_s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

def upload_profile_image(file_bytes: bytes, filename: str) -> str:
    """Envia a foto do perfil para o bucket S3 e devolve a URL pública.
    O nome do objeto é um UUID para evitar colisões.
    """
    ext = os.path.splitext(filename)[1] or ".jpg"
    object_name = f"profile/{uuid.uuid4().hex}{ext}"
    try:
        _s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=object_name,
            Body=file_bytes,
            ContentType="image/jpeg",
            ACL="public-read",
        )
    except ClientError as exc:
        raise RuntimeError(f"Erro ao fazer upload da imagem para S3: {exc}")
    return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{object_name}"

def delete_profile_image(url: str) -> None:
    """Remove a imagem do S3 a partir da URL completa armazenada no banco.
    Se a URL não pertencer ao bucket configurado, a função simplesmente retorna.
    """
    prefix = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/"
    if not url.startswith(prefix):
        return
    key = url.replace(prefix, "")
    try:
        _s3_client.delete_object(Bucket=S3_BUCKET, Key=key)
    except ClientError as exc:
        # Falha não crítica – apenas loga
        print(f"Falha ao deletar imagem do S3 ({key}): {exc}")
