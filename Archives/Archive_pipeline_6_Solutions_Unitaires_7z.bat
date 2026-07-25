@echo off
setlocal enabledelayedexpansion

set Path=%Path%;C:\Program Files\7-Zip
set repertoire_source=..\..\Pipelines_rapide\pipeline_6_solutions_unitaires\*

for /d %%D in (%repertoire_source%) do (
    echo ########## Traitement sur : %%~nxD
    if "%%~nxD" == ".git" (
        echo ##########    Repertoire ".git" ignore
    ) else (
        set nom_cible_compressee=pipeline_6_Solutions_Unitaires-Archive_compressee-%%~nxD.7z
        if not exist "7z\!nom_cible_compressee!" (
            set nom_cible=pipeline_6_Solutions_Unitaires-Archive-%%~nxD.7z
            echo ##########    !nom_cible!
            echo ##########    !nom_cible_compressee!

            REM Creer l'archive en filtrant les fichiers
            7z a -mx0 -t7z -- !nom_cible! %%~D
            REM Compresser l'archive (pas trop pour le temps)
            7z a -mx5 -t7z -sdel -- !nom_cible_compressee! !nom_cible!
            REM Ranger l'archive
            MOVE !nom_cible_compressee! 7z\!nom_cible_compressee!
        ) else (
            echo ##########    %%~nxD : déja traité
        )
    )
)

endlocal
