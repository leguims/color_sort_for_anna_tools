@echo off
set Path=%Path%;C:\Program Files\7-Zip
set repertoire_source=..\..\Pipelines_rapide\pipeline_6_solutions\*.json
set nom_cible=pipeline_8_Solutions_classees-Archive-%date:~6,4%-%date:~3,2%-%date:~0,2%.7z
set nom_cible_compressee=pipeline_8_Solutions_classees-Archive_compressee-%date:~6,4%-%date:~3,2%-%date:~0,2%.7z

REM Creer l'archive en filtrant les fichiers
7z a -mx0 -t7z -xr!.git -xr!.gitignore -- %nom_cible% %repertoire_source%
REM Compresser l'archive (pas trop pour le temps)
7z a -mx5 -t7z -sdel -- %nom_cible_compressee% %nom_cible%
REM Ranger l'archive
MOVE %nom_cible_compressee% 7z\%nom_cible_compressee%
