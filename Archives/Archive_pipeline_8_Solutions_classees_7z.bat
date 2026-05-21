set Path=%Path%;C:\Program Files\7-Zip

# Créer l'archive en filtrant les fichiers
7z a -t7z 7z\Archive_pipeline_8_Solutions_classees_%date:~6,4%-%date:~3,2%-%date:~0,2%.7z ..\..\Pipelines\pipeline_6_solutions -xr!*Resolution*.json -xr!.git