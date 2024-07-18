### Syntax

```bash
python main.py -b=bucket_name -p=file_prefix -a=app_url -o=operation
```

Where:
- **bucket_name**: GCS Bucket name where files are
- **file_prefix**: [Optional] GCS File prefix where files are.
- **app_url**: Cloud Run app url.
- **operation**: delete, embed or summarize 
