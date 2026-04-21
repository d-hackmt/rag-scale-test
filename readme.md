RUN USING 

```
gcloud builds submit --tag us-central1-docker.pkg.dev/dmtxpress/rag-repo/rag-api
```

```

gcloud run deploy rag-api \
  --image us-central1-docker.pkg.dev/dmtxpress/rag-repo/rag-api \
  --region us-central1 \
  --allow-unauthenticated

```



```
 gcloud run deploy rag-api   --source .   --region us-central1   --timeout=300   --allow-unauthenticated
```