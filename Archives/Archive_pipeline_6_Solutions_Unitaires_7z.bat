@echo off
setlocal EnableDelayedExpansion

set PATH=%PATH%;C:\Program Files\7-Zip
set repertoire_source=..\..\Pipelines_rapide\pipeline_6_solutions_unitaires\*

set "TEMP=temp"
set "OUTDIR=7z"
set "BATCH=1000"

if not exist "%OUTDIR%" mkdir "%OUTDIR%"
echo if not exist "%OUTDIR%" mkdir "%OUTDIR%"

for /d %%D in (%repertoire_source%) do (
    echo ########## Traitement sur : %%~D
    if /I "%%~nxD"==".git" (
        echo ##########    Repertoire .git ignore
    ) else (
        echo ########## Traitement sur : %%~nxD

        REM Pas de solutions unitaires si elles sont en cours de resolution
        set resolution_achevee=%OUTDIR%\pipeline_6_Plateaux_Difficulte-Archive_compressee-%%~nxD.7z
        if exist "!resolution_achevee!" (
            set nom_cible_compressee=pipeline_6_Solutions_Unitaires-Archive_compressee-%%~nxD.7z
            if not exist "%OUTDIR%\!nom_cible_compressee!" (
                echo ##########    !nom_cible_compressee!

                REM Prepare un index de lots
                set /a idx=0
                set /a next = idx + BATCH

                REM Creer l'archive en filtrant les fichiers
                for %%F in (%%~D\*.json) do (
                    set /a mod = idx %% BATCH
                    if !mod! EQU 0 (
                        set nom_cible=%TEMP%\pipeline_6_Solutions_Unitaires-Archive-%%~nxD-!idx!.7z
                        set /a next = idx + BATCH
                        set nom_cible_suivante=%TEMP%\pipeline_6_Solutions_Unitaires-Archive-%%~nxD-!next!.7z
                        echo ##########    !nom_cible!
                    )
                    REM Enregistrer seulement si l'archive suivante n'existe pas.
                    if not exist "!nom_cible_suivante!" (
                        7z a -mx0 -t7z -- !nom_cible! %%~F >nul
                    )
                    set /a idx+=1
                )
                REM Compresser l'archive (pas trop pour le temps d'execution)
                7z a -mx5 -t7z -sdel -- !nom_cible_compressee! %TEMP%\pipeline_6_Solutions_Unitaires-Archive-%%~nxD-*.7z >nul
                REM Ranger l'archive
                MOVE !nom_cible_compressee! %OUTDIR%\!nom_cible_compressee!
            ) else (
                echo ##########    %%~nxD : deja traite
            )
        ) else (
            echo ##########    %%~nxD : resolution en cours
        )
    )
)

endlocal