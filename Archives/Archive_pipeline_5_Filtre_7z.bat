@echo off
setlocal enabledelayedexpansion

set Path=%Path%;C:\Program Files\7-Zip
set repertoire_source=..\..\Pipelines_rapide\pipeline_5_filtre_doublons_permutation_jetons_piles\*

for /d %%D in (%repertoire_source%) do (
    echo ########## Traitement sur : %%~nxD
    if "%%~nxD" == ".git" (
        echo ##########    Repertoire ignore
    ) else (
        set nom_cible_compressee=pipeline_5_Filtre-Archive_compressee-%%~nxD.7z
        if not exist "7z\!nom_cible_compressee!" (
            echo ##########    !nom_cible_compressee!

            REM Creer + Compresser l'archive
            7z a -mx5 -t7z -- !nom_cible_compressee! "%%~D"
            REM Ranger l'archive
            MOVE !nom_cible_compressee! 7z\!nom_cible_compressee!
        ) else (
            echo ##########    %%~nxD : deja traite
        )
    )
)

endlocal
