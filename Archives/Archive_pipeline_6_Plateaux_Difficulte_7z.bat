set Path=%Path%;C:\Program Files\7-Zip

# Créer l'archive sans filtrer les fichiers
7z a -t7z 7z\Archive_pipeline_6_Plateaux_Difficulte_%date:~6,4%-%date:~3,2%-%date:~0,2%.7z ..\..\Pipelines\pipeline_6_plateaux_avec_difficulte -xr!.git
