@echo off

:loop
ping -n 1 8.8.8.8
if %ERRORLEVEL% EQU 0 (
  echo Internet ok

  echo folder ek 
  cd "C:\storm\ps_in\ek"
  if exist "C:\storm\ps_in\ek\*.ps" (
     for /f "delims=" %%a in ('dir /b /a:-d /o:d /t:w "*.ps"') do (
       move C:\storm\ps_in\ek\%%a C:\storm\ps_in\ek\w\%%a
       timeout 1 > nul
       echo drukuje C:\storm\ps_in\ek\w\%%a
       copy C:\storm\ps_in\ek\w\%%a \\127.0.0.1\ek
     ) 
  )

  echo folder js 
  cd "C:\storm\ps_in\js"
  if exist "C:\storm\ps_in\js\*.ps" (
     for /f "delims=" %%a in ('dir /b /a:-d /o:d /t:w "*.ps"') do (
       move C:\storm\ps_in\js\%%a C:\storm\ps_in\js\w\%%a
       timeout 1 > nul
       echo drukuje C:\storm\ps_in\js\w\%%a
       copy C:\storm\ps_in\js\w\%%a \\127.0.0.1\js
     ) 
  )

  echo folder ms 
  cd "C:\storm\ps_in\ms"
  if exist "C:\storm\ps_in\ms\*.ps" (
     for /f "delims=" %%a in ('dir /b /a:-d /o:d /t:w "*.ps"') do (
       move C:\storm\ps_in\ms\%%a C:\storm\ps_in\ms\w\%%a
       timeout 1 > nul
       echo drukuje C:\storm\ps_in\ms\w\%%a
       copy C:\storm\ps_in\ms\w\%%a \\127.0.0.1\ms
     ) 
  )

  echo folder mk
  cd "C:\storm\ps_in\mk"
  if exist "C:\storm\ps_in\mk\*.ps" (
     for /f "delims=" %%a in ('dir /b /a:-d /o:d /t:w "*.ps"') do (
       move C:\storm\ps_in\mk\%%a C:\storm\ps_in\mk\w\%%a
       timeout 1 > nul
       echo drukuje C:\storm\ps_in\mk\w\%%a
       copy C:\storm\ps_in\mk\w\%%a \\127.0.0.1\mk
     ) 
  )

  echo folder ho
  cd "C:\storm\ps_in\ho"
  if exist "C:\storm\ps_in\ho\*.ps" (
     for /f "delims=" %%a in ('dir /b /a:-d /o:d /t:w "*.ps"') do (
       move C:\storm\ps_in\ho\%%a C:\storm\ps_in\ho\w\%%a
       timeout 1 > nul
       echo drukuje C:\storm\ps_in\ho\w\%%a
       copy C:\storm\ps_in\ho\w\%%a \\127.0.0.1\ho
     ) 
  )

  echo folder mw
  cd "C:\storm\ps_in\mw"
  if exist "C:\storm\ps_in\mw\*.ps" (
     for /f "delims=" %%a in ('dir /b /a:-d /o:d /t:w "*.ps"') do (
       move C:\storm\ps_in\mw\%%a C:\storm\ps_in\mw\w\%%a
       timeout 1 > nul
       echo drukuje C:\storm\ps_in\mw\w\%%a
       copy C:\storm\ps_in\mw\w\%%a \\127.0.0.1\mw
     ) 
  )

)

if %ERRORLEVEL% EQU 1 (
echo ########################################
echo !!! UWAGA BRAK POLACZENIA Z INTERNETEM !!! 
echo ########################################
  echo folder ek 
  cd "C:\storm\ps_in\ek"
  if exist "C:\storm\ps_in\ek\*.ps" (
     for /f "delims=" %%a in ('dir /b /a:-d /o:d /t:w "*.ps"') do (
       move C:\storm\ps_in\ek\%%a C:\storm\ps_in\ek\w\%%a
       timeout 1 > nul
       echo drukuje C:\storm\ps_in\ek\w\%%a
       copy C:\storm\ps_in\ek\w\%%a \\127.0.0.1\bp
     ) 
  )

  echo folder js 
  cd "C:\storm\ps_in\js"
  if exist "C:\storm\ps_in\js\*.ps" (
     for /f "delims=" %%a in ('dir /b /a:-d /o:d /t:w "*.ps"') do (
       move C:\storm\ps_in\js\%%a C:\storm\ps_in\js\w\%%a
       timeout 1 > nul
       echo drukuje C:\storm\ps_in\js\w\%%a
       copy C:\storm\ps_in\js\w\%%a \\127.0.0.1\bp
     ) 
  )

  echo folder ms 
  cd "C:\storm\ps_in\ms"
  if exist "C:\storm\ps_in\ms\*.ps" (
     for /f "delims=" %%a in ('dir /b /a:-d /o:d /t:w "*.ps"') do (
       move C:\storm\ps_in\ms\%%a C:\storm\ps_in\ms\w\%%a
       timeout 1 > nul
       echo drukuje C:\storm\ps_in\ms\w\%%a
       copy C:\storm\ps_in\ms\w\%%a \\127.0.0.1\bp
     ) 
  )

  echo folder mk
  cd "C:\storm\ps_in\mk"
  if exist "C:\storm\ps_in\mk\*.ps" (
     for /f "delims=" %%a in ('dir /b /a:-d /o:d /t:w "*.ps"') do (
       move C:\storm\ps_in\mk\%%a C:\storm\ps_in\mk\w\%%a
       timeout 1 > nul
       echo drukuje C:\storm\ps_in\mk\w\%%a

       copy C:\storm\ps_in\mk\w\%%a \\127.0.0.1\bp
     ) 
  )

  echo folder ho
  cd "C:\storm\ps_in\ho"
  if exist "C:\storm\ps_in\ho\*.ps" (
     for /f "delims=" %%a in ('dir /b /a:-d /o:d /t:w "*.ps"') do (
       move C:\storm\ps_in\ho\%%a C:\storm\ps_in\ho\w\%%a
       timeout 1 > nul
       echo drukuje C:\storm\ps_in\ho\w\%%a
       copy C:\storm\ps_in\ho\w\%%a \\127.0.0.1\bp
     ) 
  )

  echo folder mw
  cd "C:\storm\ps_in\mw"
  if exist "C:\storm\ps_in\mw\*.ps" (
     for /f "delims=" %%a in ('dir /b /a:-d /o:d /t:w "*.ps"') do (
       move C:\storm\ps_in\mw\%%a C:\storm\ps_in\mw\w\%%a
       timeout 1 > nul
       echo drukuje C:\storm\ps_in\mw\w\%%a
       copy C:\storm\ps_in\mw\w\%%a \\127.0.0.1\bp
     ) 
  )
)
timeout 10 > nul
goto loop